from django.shortcuts import render
from django.http import HttpResponse, Http404
from pathlib import Path
from functools import lru_cache
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.offline as opy

# Dicionário institucional com nome por extenso de todas as 27 UFs do Brasil
NOMES_ESTADOS = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}

# Delitos Oficiais de CVLI (Crimes Violentos Letais Intencionais)
# Regra estrita: Homicídio doloso + Feminicídio + Roubo seguido de morte + Lesão corporal seguida de morte
# NÃO inclui tentativas, suicídios, trânsito ou intervenção policial
DELITOS_CVLI = [
    'Homicídio doloso',
    'Feminicídio',
    'Roubo seguido de morte (latrocínio)',
    'Lesão corporal seguida de morte'
]

# Delitos Oficiais de CVP (Crimes Violentos contra o Patrimônio)
# Regra estrita: Roubos qualificados com emprego de violência/grave ameaça à pessoa (NÃO inclui furto)
DELITOS_CVP = [
    'Roubo de veículo',
    'Roubo de carga',
    'Roubo a instituição financeira',
    'Roubo seguido de morte (latrocínio)'
]

DELITO_MANDADOS = 'Mandado de prisão cumprido'
DELITO_ARMAS = 'Arma de Fogo Apreendida'

# Serviços de bombeiros, atos administrativos e acolhimento social (excluídos das análises criminais estritas da UF)
EVENTOS_NAO_CRIMINAIS = [
    'Atendimento pré-hospitalar',
    'Busca e salvamento',
    'Combate a incêndios',
    'Emissão de Alvarás de licença',
    'Realização de vistorias',
    'Pessoa Desaparecida',
    'Pessoa Localizada'
]

# ==============================================================================
# CARREGAMENTO COM CACHE EM MEMÓRIA (@lru_cache)
# ==============================================================================
@lru_cache(maxsize=1)
def obter_dataframe_cache():
    """
    Carrega e pré-processa o dataset apenas uma vez na memória RAM.
    Garante respostas em milissegundos para os filtros dinâmicos e mapa.
    """
    base_dir = Path(__file__).resolve().parent.parent
    caminho_arquivo = base_dir / 'data' / 'BancoVDE 2025.csv'
    
    if not caminho_arquivo.exists():
        caminho_arquivo = Path('data/BancoVDE 2025.csv')
        
    df = pd.read_csv(caminho_arquivo, sep=";", encoding="utf-8", low_memory=False)
    
    # Tratamento das colunas numéricas
    df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)
    df['total_vitima'] = pd.to_numeric(df['total_vitima'], errors='coerce').fillna(0)
    df['feminino'] = pd.to_numeric(df['feminino'], errors='coerce').fillna(0)
    df['masculino'] = pd.to_numeric(df['masculino'], errors='coerce').fillna(0)
    df['nao_informado'] = pd.to_numeric(df['nao_informado'], errors='coerce').fillna(0)
    df['evento_lower'] = df['evento'].astype(str).str.lower().str.strip()

    # Métrica de Vítimas e Quantidade Real Unificada
    soma_generos = df['feminino'] + df['masculino'] + df['nao_informado']
    df['vitimas_reais'] = np.where(df['total_vitima'] > 0, df['total_vitima'], soma_generos)
    df['quantidade_real'] = np.where(df['total'] > 0, df['total'], df['vitimas_reais'])
    
    # Tratamento de datas com dayfirst=True para padrão brasileiro (Dia/Mês/Ano)
    if pd.api.types.is_numeric_dtype(df['data_referencia']):
        df['data_dt'] = pd.to_datetime(df['data_referencia'], unit='D', origin='1899-12-30')
    else:
        df['data_dt'] = pd.to_datetime(df['data_referencia'], dayfirst=True, errors='coerce')
        
    df['mes_num'] = df['data_dt'].dt.month
    meses_pt = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    df['mes_nome'] = df['mes_num'].map(meses_pt)
    
    return df


def index(request):
    """
    View principal do Dashboard de Segurança Pública do Brasil (Visão Nacional).
    Calcula KPIs nacionais, dados do Mapa Coroplético do Brasil por UF,
    série temporal e rankings.
    """
    # 1. Carrega o dataset da memória cache
    df_completo = obter_dataframe_cache()
    
    # 2. Lista ordenada de eventos para o menu suspenso do filtro
    lista_eventos = sorted(df_completo['evento'].dropna().unique())
    lista_ufs = sorted(list(NOMES_ESTADOS.keys()))
    
    # 3. Captura o evento selecionado pelo usuário via parâmetro GET
    evento_selecionado = request.GET.get('evento', '').strip()
    
    # 4. Aplica o filtro dinâmico
    if evento_selecionado and evento_selecionado in lista_eventos:
        df = df_completo[df_completo['evento'] == evento_selecionado].copy()
        filtro_ativo = True
        titulo_contexto = f"Evento: {evento_selecionado}"
    else:
        df = df_completo
        evento_selecionado = ''
        filtro_ativo = False
        titulo_contexto = "Todos os Eventos (Brasil - Geral)"

    # ==========================================================================
    # CÁLCULO DOS CARTÕES DE MÉTRICAS (KPIS) COM SPARKLINES
    # ==========================================================================
    if filtro_ativo:
        total_ocorrencias = int(df['quantidade_real'].sum())
        total_vitimas_identificadas = int(df['vitimas_reais'].sum())

        serie_mensal_total = [
            int(v) for v in df.groupby('mes_num')['quantidade_real']
            .sum().reindex(range(1, 13), fill_value=0).tolist()
        ]

        if total_vitimas_identificadas > 0:
            total_fem = int(df['feminino'].sum())
            total_masc = int(df['masculino'].sum())
            
            base_calculo = total_vitimas_identificadas if total_vitimas_identificadas > 0 else 1
            pct_fem = (total_fem / base_calculo * 100)
            pct_masc = (total_masc / base_calculo * 100)

            sparkline_fem = [
                int(v) for v in df.groupby('mes_num')['feminino']
                .sum().reindex(range(1, 13), fill_value=0).tolist()
            ]
            sparkline_masc = [
                int(v) for v in df.groupby('mes_num')['masculino']
                .sum().reindex(range(1, 13), fill_value=0).tolist()
            ]

            kpis = [
                {
                    'titulo': f'Total de {evento_selecionado}',
                    'valor': f"{total_ocorrencias:,}".replace(",", "."),
                    'descricao': 'Total de vítimas / ocorrências no Brasil em 2025',
                    'cor': 'rose',
                    'tipo_icone': 'alerta',
                    'sparkline': serie_mensal_total,
                },
                {
                    'titulo': 'Vítimas Femininas',
                    'valor': f"{total_fem:,}".replace(",", "."),
                    'descricao': f'{pct_fem:.1f}% das vítimas identificadas',
                    'cor': 'pink',
                    'tipo_icone': 'feminino',
                    'sparkline': sparkline_fem,
                },
                {
                    'titulo': 'Vítimas Masculinas',
                    'valor': f"{total_masc:,}".replace(",", "."),
                    'descricao': f'{pct_masc:.1f}% das vítimas identificadas',
                    'cor': 'indigo',
                    'tipo_icone': 'masculino',
                    'sparkline': sparkline_masc,
                },
            ]
            total_cvli = total_ocorrencias
            total_mandados = total_fem
            total_transito = total_masc

        else:
            top_uf_serie = df.groupby('uf')['quantidade_real'].sum().sort_values(ascending=False)
            top_uf_sigla = top_uf_serie.index[0] if not top_uf_serie.empty else 'N/D'
            top_uf_qtd = int(top_uf_serie.iloc[0]) if not top_uf_serie.empty else 0
            pct_top_uf = (top_uf_qtd / total_ocorrencias * 100) if total_ocorrencias > 0 else 0

            df_top_uf = df[df['uf'] == top_uf_sigla]
            sparkline_top_uf = [
                int(v) for v in df_top_uf.groupby('mes_num')['quantidade_real']
                .sum().reindex(range(1, 13), fill_value=0).tolist()
            ]

            top_mes_serie = df.groupby('mes_nome')['quantidade_real'].sum().sort_values(ascending=False)
            top_mes_nome = top_mes_serie.index[0] if not top_mes_serie.empty else 'N/D'
            top_mes_qtd = int(top_mes_serie.iloc[0]) if not top_mes_serie.empty else 0

            kpis = [
                {
                    'titulo': f'Total de {evento_selecionado}',
                    'valor': f"{total_ocorrencias:,}".replace(",", "."),
                    'descricao': 'Registros consolidados no Brasil em 2025',
                    'cor': 'blue',
                    'tipo_icone': 'seguranca',
                    'sparkline': serie_mensal_total,
                },
                {
                    'titulo': f'Estado Líder ({top_uf_sigla})',
                    'valor': f"{top_uf_qtd:,}".replace(",", "."),
                    'descricao': f'{pct_top_uf:.1f}% do volume nacional registrado',
                    'cor': 'amber',
                    'tipo_icone': 'localizacao',
                    'sparkline': sparkline_top_uf,
                },
                {
                    'titulo': f'Pico Mensal ({top_mes_nome})',
                    'valor': f"{top_mes_qtd:,}".replace(",", "."),
                    'descricao': 'Mês com maior volume registrado',
                    'cor': 'indigo',
                    'tipo_icone': 'calendario',
                    'sparkline': serie_mensal_total,
                },
            ]
            total_cvli = total_ocorrencias
            total_mandados = top_uf_qtd
            total_transito = top_mes_qtd

    else:
        # VISÃO GERAL (TODOS OS EVENTOS)
        eventos_cvli_oficiais = [
            'homicídio doloso',
            'feminicídio',
            'roubo seguido de morte (latrocínio)',
            'lesão corporal seguida de morte'
        ]
        filtro_cvli = df['evento_lower'].isin(eventos_cvli_oficiais)
        total_cvli = int(df.loc[filtro_cvli, 'quantidade_real'].sum())
        sparkline_cvli = [
            int(v) for v in df[filtro_cvli].groupby('mes_num')['quantidade_real']
            .sum().reindex(range(1, 13), fill_value=0).tolist()
        ]

        filtro_mandados = df['evento_lower'].str.contains('mandado', na=False)
        total_mandados = int(df.loc[filtro_mandados, 'quantidade_real'].sum())
        sparkline_mandados = [
            int(v) for v in df[filtro_mandados].groupby('mes_num')['quantidade_real']
            .sum().reindex(range(1, 13), fill_value=0).tolist()
        ]

        filtro_transito = df['evento_lower'].str.contains('trânsito', na=False)
        total_transito = int(df.loc[filtro_transito, 'quantidade_real'].sum())
        sparkline_transito = [
            int(v) for v in df[filtro_transito].groupby('mes_num')['quantidade_real']
            .sum().reindex(range(1, 13), fill_value=0).tolist()
        ]

        kpis = [
            {
                'titulo': 'Ocorrências de CVLI',
                'valor': f"{total_cvli:,}".replace(",", "."),
                'descricao': 'Crimes Violentos Letais Intencionais',
                'cor': 'rose',
                'tipo_icone': 'alerta',
                'sparkline': sparkline_cvli,
            },
            {
                'titulo': 'Mandados de Prisão',
                'valor': f"{total_mandados:,}".replace(",", "."),
                'descricao': 'Mandados de prisão cumpridos no país',
                'cor': 'blue',
                'tipo_icone': 'prisao',
                'sparkline': sparkline_mandados,
            },
            {
                'titulo': 'Ocorrências de Trânsito',
                'valor': f"{total_transito:,}".replace(",", "."),
                'descricao': 'Sinistros viários com vítimas fatais',
                'cor': 'amber',
                'tipo_icone': 'transito',
                'sparkline': sparkline_transito,
            },
        ]

    # ==========================================================================
    # DADOS ESTATÍSTICOS PARA O MAPA COROPLÉTICO DO BRASIL (LEAFLET / GEOJSON)
    # ==========================================================================
    total_brasil_mapa = float(df['quantidade_real'].sum())
    if total_brasil_mapa == 0:
        total_brasil_mapa = 1.0

    ranking_ufs_serie = df.groupby('uf')['quantidade_real'].sum().sort_values(ascending=False)
    
    mapa_dados_uf = {}
    posicao = 1
    for uf_sigla, total_uf in ranking_ufs_serie.items():
        uf_str = str(uf_sigla).strip().upper()
        pct = round((total_uf / total_brasil_mapa) * 100, 2)
        mapa_dados_uf[uf_str] = {
            'sigla': uf_str,
            'nome': NOMES_ESTADOS.get(uf_str, uf_str),
            'total': int(total_uf),
            'total_formatado': f"{int(total_uf):,}".replace(",", "."),
            'pct_brasil': pct,
            'ranking': posicao,
        }
        posicao += 1

    # Inclui as 27 UFs mesmo que tenham zero registros
    for sigla, nome in NOMES_ESTADOS.items():
        if sigla not in mapa_dados_uf:
            mapa_dados_uf[sigla] = {
                'sigla': sigla,
                'nome': nome,
                'total': 0,
                'total_formatado': '0',
                'pct_brasil': 0.0,
                'ranking': 27,
            }

    max_ocorrencias_uf = max([d['total'] for d in mapa_dados_uf.values()]) if mapa_dados_uf else 1

    # Matriz completa de dados por evento para filtragem reativa no mapa (sem recarregar)
    dados_por_evento = {}
    totais_geral_uf = df_completo.groupby('uf')['quantidade_real'].sum()
    total_brasil_geral = float(totais_geral_uf.sum()) or 1.0
    mapa_geral = {}
    pos = 1
    for uf_s, val in totais_geral_uf.sort_values(ascending=False).items():
        uf_str = str(uf_s).strip().upper()
        mapa_geral[uf_str] = {
            'sigla': uf_str,
            'total': int(val),
            'total_formatado': f"{int(val):,}".replace(",", "."),
            'pct_brasil': round((val / total_brasil_geral) * 100, 2),
            'ranking': pos,
            'nome': NOMES_ESTADOS.get(uf_str, uf_str)
        }
        pos += 1
    for s, n in NOMES_ESTADOS.items():
        if s not in mapa_geral:
            mapa_geral[s] = {'sigla': s, 'total': 0, 'total_formatado': '0', 'pct_brasil': 0.0, 'ranking': 27, 'nome': n}
            
    dados_por_evento[''] = mapa_geral
    dados_por_evento['Todos os Eventos'] = mapa_geral

    grupos_ev_uf = df_completo.groupby(['evento', 'uf'])['quantidade_real'].sum()
    for ev in lista_eventos:
        if ev in grupos_ev_uf.index.levels[0]:
            serie_ev = grupos_ev_uf.loc[ev].sort_values(ascending=False)
        else:
            serie_ev = pd.Series(dtype=float)
        total_ev_br = float(serie_ev.sum()) or 1.0
        mapa_ev = {}
        pos = 1
        for uf_s, val in serie_ev.items():
            uf_str = str(uf_s).strip().upper()
            mapa_ev[uf_str] = {
                'sigla': uf_str,
                'total': int(val),
                'total_formatado': f"{int(val):,}".replace(",", "."),
                'pct_brasil': round((val / total_ev_br) * 100, 2),
                'ranking': pos,
                'nome': NOMES_ESTADOS.get(uf_str, uf_str)
            }
            pos += 1
        for s, n in NOMES_ESTADOS.items():
            if s not in mapa_ev:
                mapa_ev[s] = {'sigla': s, 'total': 0, 'total_formatado': '0', 'pct_brasil': 0.0, 'ranking': 27, 'nome': n}
        dados_por_evento[ev] = mapa_ev

    # ==========================================================================
    # DADOS ESTRUTURADOS PARA CHART.JS
    # ==========================================================================
    # --- GRÁFICO 1: BARRAS HORIZONTAIS (Top 10) ---
    if filtro_ativo:
        df_chart_barras = (
            df.groupby('uf')['quantidade_real']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        chart_barras_labels = df_chart_barras['uf'].tolist()
        chart_barras_values = [int(v) for v in df_chart_barras['quantidade_real'].tolist()]
        chart_barras_titulo = f"Distribuição por Estado - Top 10 UFs ({evento_selecionado})"
    else:
        df_chart_barras = (
            df.groupby('evento')['quantidade_real']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        chart_barras_labels = df_chart_barras['evento'].tolist()
        chart_barras_values = [int(v) for v in df_chart_barras['quantidade_real'].tolist()]
        chart_barras_titulo = "Distribuição por Indicador - Top 10 Frequentes"

    # --- GRÁFICO 2: LINHAS / ÁREA (Evolução Mensal) ---
    df_chart_mensal = (
        df.groupby('mes_num')['quantidade_real']
        .sum()
        .reindex(range(1, 13), fill_value=0)
    )
    chart_linhas_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    chart_linhas_values = [int(v) for v in df_chart_mensal.tolist()]
    chart_linhas_titulo = (
        f"Evolução Temporal Mês a Mês - {evento_selecionado}"
        if filtro_ativo else
        "Série Histórica - Evolução Mensal (Janeiro a Dezembro de 2025)"
    )

    # Plotly retrocompatibilidade
    if filtro_ativo:
        df_barras_plotly = (
            df.groupby('uf')['quantidade_real']
            .sum().sort_values(ascending=True).tail(10).reset_index()
        )
        fig_barras = px.bar(
            df_barras_plotly, x='quantidade_real', y='uf', orientation='h',
            title=f'<b>{chart_barras_titulo}</b>',
            labels={'quantidade_real': 'Quantidade', 'uf': 'UF'},
            color='quantidade_real', color_continuous_scale='Reds' if df['vitimas_reais'].sum() > 0 else 'Blues'
        )
    else:
        df_barras_plotly = (
            df.groupby('evento')['quantidade_real']
            .sum().sort_values(ascending=True).tail(10).reset_index()
        )
        fig_barras = px.bar(
            df_barras_plotly, x='quantidade_real', y='evento', orientation='h',
            title=f'<b>{chart_barras_titulo}</b>',
            labels={'quantidade_real': 'Total', 'evento': 'Indicador'},
            color='quantidade_real', color_continuous_scale='Blues'
        )
    fig_barras.update_layout(template='plotly_white', margin=dict(l=20, r=20, t=50, b=20), height=420, coloraxis_showscale=False)

    df_mensal_plotly = (
        df.groupby(['mes_num', 'mes_nome'])['quantidade_real']
        .sum().reset_index().sort_values('mes_num')
    )
    fig_linhas = px.line(
        df_mensal_plotly, x='mes_nome', y='quantidade_real', markers=True,
        title=f'<b>{chart_linhas_titulo}</b>',
        labels={'quantidade_real': 'Total', 'mes_nome': 'Mês'}
    )
    cor_linha = '#e11d48' if filtro_ativo and df['vitimas_reais'].sum() > 0 else '#2563eb'
    fig_linhas.update_traces(line=dict(color=cor_linha, width=3), marker=dict(size=8))
    fig_linhas.update_xaxes(categoryorder='array', categoryarray=chart_linhas_labels)
    fig_linhas.update_layout(template='plotly_white', margin=dict(l=20, r=20, t=50, b=20), height=420)

    grafico_barras_div = opy.plot(fig_barras, output_type='div', include_plotlyjs=False)
    grafico_linhas_div = opy.plot(fig_linhas, output_type='div', include_plotlyjs=False)

    context = {
        'lista_eventos': lista_eventos,
        'lista_ufs': lista_ufs,
        'evento_selecionado': evento_selecionado,
        'filtro_ativo': filtro_ativo,
        'titulo_contexto': titulo_contexto,
        'kpis': kpis,
        # Dados para o Mapa Coroplético do Brasil
        'mapa_dados_uf_json': json.dumps(mapa_dados_uf, ensure_ascii=False),
        'dados_mapa_por_evento_json': json.dumps(dados_por_evento, ensure_ascii=False),
        'max_ocorrencias_uf': max_ocorrencias_uf,
        # Dados para Chart.js
        'chart_barras_labels_json': json.dumps(chart_barras_labels, ensure_ascii=False),
        'chart_barras_values_json': json.dumps(chart_barras_values),
        'chart_barras_titulo': chart_barras_titulo,
        'chart_linhas_labels_json': json.dumps(chart_linhas_labels),
        'chart_linhas_values_json': json.dumps(chart_linhas_values),
        'chart_linhas_titulo': chart_linhas_titulo,
        # Variáveis legadas
        'total_cvli': f"{total_cvli:,}".replace(",", "."),
        'total_mandados': f"{total_mandados:,}".replace(",", "."),
        'total_transito': f"{total_transito:,}".replace(",", "."),
        'grafico_barras': grafico_barras_div,
        'grafico_linha': grafico_linhas_div,
        'grafico_linhas': grafico_linhas_div,
    }

    return render(request, 'dashboard/index.html', context)


# ==============================================================================
# VIEW DA PÁGINA DEDICADA DO ESTADO (UF)
# ==============================================================================
def detalhe_estado(request, uf):
    """
    Página individual dedicada a um Estado (UF) específico.
    Apresenta 4 Cards Analíticos Qualificados (CVLI, CVP, Mandados de Prisão e Armas Apreendidas),
    decomposição analítica dos sub-indicadores, comparativo nacional,
    evolução temporal mensal e distribuição estrita de ocorrências de segurança pública.
    """
    df_completo = obter_dataframe_cache()
    uf_upper = uf.strip().upper()
    
    if uf_upper not in NOMES_ESTADOS:
        raise Http404(f"Estado com a sigla '{uf}' não foi encontrado.")
    
    nome_estado = NOMES_ESTADOS[uf_upper]
    lista_ufs = sorted(list(NOMES_ESTADOS.keys()))
    
    # 1. Filtro do DataFrame para a UF selecionada
    df_uf = df_completo[df_completo['uf'] == uf_upper].copy()
    
    # 2. DataFrame estritamente policial/criminal (exclui bombeiros, vistorias e assistenciais)
    df_uf_seguranca = df_uf[~df_uf['evento'].isin(EVENTOS_NAO_CRIMINAIS)].copy()

    # ==========================================================================
    # CÁLCULO DOS 4 GRANDES INDICADORES ESTATÍSTICOS E SEUS RANKINGS NACIONAIS
    # ==========================================================================
    
    # --- 1. CVLI (Crimes Violentos Letais Intencionais) ---
    df_cvli_br = df_completo[df_completo['evento'].isin(DELITOS_CVLI)]
    total_cvli_br = int(df_cvli_br['quantidade_real'].sum())
    rank_cvli_serie = df_cvli_br.groupby('uf')['quantidade_real'].sum().sort_values(ascending=False)
    
    total_cvli = int(df_uf[df_uf['evento'].isin(DELITOS_CVLI)]['quantidade_real'].sum())
    pos_cvli = list(rank_cvli_serie.index).index(uf_upper) + 1 if uf_upper in rank_cvli_serie.index else 27
    pct_cvli_br = round((total_cvli / total_cvli_br * 100), 2) if total_cvli_br > 0 else 0.0

    # Decomposição dos 4 crimes do CVLI
    cvli_itens = []
    cores_cvli = ['bg-rose-600', 'bg-rose-500', 'bg-pink-500', 'bg-red-700']
    for idx, crime in enumerate(DELITOS_CVLI):
        qtd = int(df_uf[df_uf['evento'] == crime]['quantidade_real'].sum())
        pct = round((qtd / total_cvli * 100), 1) if total_cvli > 0 else 0.0
        cvli_itens.append({
            'crime': crime,
            'qtd': qtd,
            'qtd_fmt': f"{qtd:,}".replace(",", "."),
            'pct': pct,
            'cor_bg': cores_cvli[idx % len(cores_cvli)],
        })

    # --- 2. CVP (Crimes Violentos contra o Patrimônio) ---
    df_cvp_br = df_completo[df_completo['evento'].isin(DELITOS_CVP)]
    total_cvp_br = int(df_cvp_br['quantidade_real'].sum())
    rank_cvp_serie = df_cvp_br.groupby('uf')['quantidade_real'].sum().sort_values(ascending=False)

    total_cvp = int(df_uf[df_uf['evento'].isin(DELITOS_CVP)]['quantidade_real'].sum())
    pos_cvp = list(rank_cvp_serie.index).index(uf_upper) + 1 if uf_upper in rank_cvp_serie.index else 27
    pct_cvp_br = round((total_cvp / total_cvp_br * 100), 2) if total_cvp_br > 0 else 0.0

    # Decomposição dos 4 crimes do CVP
    cvp_itens = []
    cores_cvp = ['bg-amber-500', 'bg-orange-500', 'bg-yellow-600', 'bg-rose-500']
    for idx, crime in enumerate(DELITOS_CVP):
        qtd = int(df_uf[df_uf['evento'] == crime]['quantidade_real'].sum())
        pct = round((qtd / total_cvp * 100), 1) if total_cvp > 0 else 0.0
        cvp_itens.append({
            'crime': crime,
            'qtd': qtd,
            'qtd_fmt': f"{qtd:,}".replace(",", "."),
            'pct': pct,
            'cor_bg': cores_cvp[idx % len(cores_cvp)],
        })

    # --- 3. Mandados de Prisão Cumpridos ---
    df_mandados_br = df_completo[df_completo['evento'] == DELITO_MANDADOS]
    total_mandados_br = int(df_mandados_br['quantidade_real'].sum())
    rank_mandados_serie = df_mandados_br.groupby('uf')['quantidade_real'].sum().sort_values(ascending=False)

    total_mandados = int(df_uf[df_uf['evento'] == DELITO_MANDADOS]['quantidade_real'].sum())
    pos_mandados = list(rank_mandados_serie.index).index(uf_upper) + 1 if uf_upper in rank_mandados_serie.index else 27
    pct_mandados_br = round((total_mandados / total_mandados_br * 100), 2) if total_mandados_br > 0 else 0.0

    # --- 4. Armas de Fogo Apreendidas ---
    df_armas_br = df_completo[df_completo['evento'] == DELITO_ARMAS]
    total_armas_br = int(df_armas_br['quantidade_real'].sum())
    rank_armas_serie = df_armas_br.groupby('uf')['quantidade_real'].sum().sort_values(ascending=False)

    total_armas = int(df_uf[df_uf['evento'] == DELITO_ARMAS]['quantidade_real'].sum())
    pos_armas = list(rank_armas_serie.index).index(uf_upper) + 1 if uf_upper in rank_armas_serie.index else 27
    pct_armas_br = round((total_armas / total_armas_br * 100), 2) if total_armas_br > 0 else 0.0

    # ==========================================================================
    # OS 4 CARDS ESTATÍSTICOS DA ABA DO ESTADO
    # ==========================================================================
    kpis_estado = [
        {
            'titulo': 'Total de CVLI',
            'valor': f"{total_cvli:,}".replace(",", "."),
            'subtitulo': 'Crimes Violentos Letais Intencionais',
            'tooltip': 'Homicídio Doloso, Feminicídio, Latrocínio e Lesão Corporal Seguida de Morte (exclui tentativas e trânsito)',
            'ranking': f'{pos_cvli}º no Brasil',
            'pct_nacional': f'{pct_cvli_br}% do país',
            'cor': 'rose',
            'tipo_icone': 'cvli'
        },
        {
            'titulo': 'Total de CVP',
            'valor': f"{total_cvp:,}".replace(",", "."),
            'subtitulo': 'Crimes Violentos contra o Patrimônio',
            'tooltip': 'Roubos de veículo, de carga, banco e latrocínio (exclui furtos)',
            'ranking': f'{pos_cvp}º no Brasil',
            'pct_nacional': f'{pct_cvp_br}% do país',
            'cor': 'amber',
            'tipo_icone': 'cvp'
        },
        {
            'titulo': 'Mandados de Prisão',
            'valor': f"{total_mandados:,}".replace(",", "."),
            'subtitulo': 'Mandados de Prisão Cumpridos',
            'tooltip': 'Capturas e prisões judiciais cumpridas pelas forças policiais',
            'ranking': f'{pos_mandados}º no Brasil',
            'pct_nacional': f'{pct_mandados_br}% do país',
            'cor': 'blue',
            'tipo_icone': 'mandados'
        },
        {
            'titulo': 'Armas Apreendidas',
            'valor': f"{total_armas:,}".replace(",", "."),
            'subtitulo': 'Armas de Fogo Apreendidas',
            'tooltip': 'Armas de fogo recolhidas e retiradas de circulação na UF',
            'ranking': f'{pos_armas}º no Brasil',
            'pct_nacional': f'{pct_armas_br}% do país',
            'cor': 'emerald',
            'tipo_icone': 'armas'
        },
    ]

    # ==========================================================================
    # GRÁFICOS ANALÍTICOS ESPECÍFICOS DA UF (POLICIAIS/CRIMINAIS)
    # ==========================================================================
    
    # 1. Evolução Temporal Mensal da UF (Chart.js)
    df_mensal_uf = (
        df_uf_seguranca.groupby('mes_num')['quantidade_real']
        .sum()
        .reindex(range(1, 13), fill_value=0)
    )
    chart_linhas_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    chart_linhas_values = [int(v) for v in df_mensal_uf.tolist()]

    # 2. Top Crimes / Indicadores Policiais na UF (Chart.js)
    top_crimes_serie = df_uf_seguranca.groupby('evento')['quantidade_real'].sum().sort_values(ascending=False)
    top_crimes_uf = top_crimes_serie.head(10).reset_index()
    chart_crimes_labels = top_crimes_uf['evento'].tolist() if not top_crimes_uf.empty else []
    chart_crimes_values = [int(v) for v in top_crimes_uf['quantidade_real'].tolist()] if not top_crimes_uf.empty else []

    # ==========================================================================
    # TABELA DE OCORRÊNCIAS DE SEGURANÇA PÚBLICA (EXCLUI BOMBEIROS/ADMINISTRATIVOS)
    # ==========================================================================
    tabela_registros_uf = (
        df_uf_seguranca.groupby(['evento'])[['quantidade_real', 'feminino', 'masculino']]
        .sum()
        .sort_values(by='quantidade_real', ascending=False)
        .reset_index()
    )
    tabela_linhas = []
    for _, row in tabela_registros_uf.iterrows():
        tabela_linhas.append({
            'evento': row['evento'],
            'total': int(row['quantidade_real']),
            'total_fmt': f"{int(row['quantidade_real']):,}".replace(",", "."),
            'feminino': int(row['feminino']),
            'feminino_fmt': f"{int(row['feminino']):,}".replace(",", "."),
            'masculino': int(row['masculino']),
            'masculino_fmt': f"{int(row['masculino']):,}".replace(",", "."),
        })

    total_geral_seguranca = int(df_uf_seguranca['quantidade_real'].sum())

    context = {
        'uf': uf_upper,
        'nome_estado': nome_estado,
        'lista_ufs': lista_ufs,
        'lista_eventos': sorted(df_completo['evento'].dropna().unique()),
        'kpis_estado': kpis_estado,
        'total_cvli_fmt': f"{total_cvli:,}".replace(",", "."),
        'pos_cvli': pos_cvli,
        'pct_cvli_br': pct_cvli_br,
        'total_cvp_fmt': f"{total_cvp:,}".replace(",", "."),
        'pos_cvp': pos_cvp,
        'pct_cvp_br': pct_cvp_br,
        'total_mandados_fmt': f"{total_mandados:,}".replace(",", "."),
        'pos_mandados': pos_mandados,
        'pct_mandados_br': pct_mandados_br,
        'total_armas_fmt': f"{total_armas:,}".replace(",", "."),
        'pos_armas': pos_armas,
        'pct_armas_br': pct_armas_br,
        'cvli_itens': cvli_itens,
        'cvp_itens': cvp_itens,
        'chart_linhas_labels_json': json.dumps(chart_linhas_labels),
        'chart_linhas_values_json': json.dumps(chart_linhas_values),
        'chart_crimes_labels_json': json.dumps(chart_crimes_labels, ensure_ascii=False),
        'chart_crimes_values_json': json.dumps(chart_crimes_values),
        'tabela_linhas': tabela_linhas,
        'total_registros_tabela': len(tabela_linhas),
        'total_geral_seguranca_fmt': f"{total_geral_seguranca:,}".replace(",", "."),
    }

    return render(request, 'dashboard/detalhe_estado.html', context)


def exportar_csv(request):
    """
    Download em CSV respeitando o filtro de evento selecionado e com quantidades unificadas.
    """
    df = obter_dataframe_cache()
    evento_selecionado = request.GET.get('evento', '').strip()
    
    if evento_selecionado and evento_selecionado in df['evento'].unique():
        df_filtrado = df[df['evento'] == evento_selecionado]
        nome_arquivo = f"dados_seguranca_2025_{evento_selecionado}.csv"
    else:
        df_filtrado = df
        nome_arquivo = "dados_seguranca_2025_brasil.csv"
        
    resumo_export = (
        df_filtrado.groupby(['uf', 'evento', 'mes_nome'])['quantidade_real']
        .sum()
        .reset_index()
        .rename(columns={'quantidade_real': 'total_registros'})
    )
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    resumo_export.to_csv(path_or_buf=response, index=False, sep=';', encoding='utf-8-sig')
    return response


def malha_estados_geojson(request):
    """
    Retorna a malha GeoJSON oficial dos 27 estados do Brasil (IBGE) para o Leaflet.
    Garante renderização instantânea mesmo offline ou com bloqueio de CDN.
    """
    caminho = Path(__file__).resolve().parent / 'static' / 'dashboard' / 'geo' / 'brasil_estados.json'
    if caminho.exists():
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        return HttpResponse(conteudo, content_type='application/json')
    raise Http404("Arquivo GeoJSON dos estados não encontrado.")
