"""
Script de Análise Temporal e Indicadores Mensais - Segurança Pública 2025
Autor: Especialista em Análise de Dados com Python & Pandas
"""

from pathlib import Path
import pandas as pd

# Configurações visuais do Pandas para o terminal
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ==============================================================================
# CARREGAMENTO DO DATASET
# ==============================================================================
caminhos = [
    Path("data/BancoVDE 2025.xlsx"),
    Path("projeto_vde_jp/data/BancoVDE 2025.xlsx"),
]
caminho = next((p for p in caminhos if p.exists()), Path("data/BancoVDE 2025.xlsx"))
print(f"Carregando dados de '{caminho}'...")
df = pd.read_excel(caminho)
print("Dados carregados com sucesso!\n")

# ==============================================================================
# 1. CONVERSÃO DA COLUNA 'data_referencia' PARA O FORMATO DATETIME
# ==============================================================================
# O Pandas pode receber datas em formato numérico serial do Excel (ex: 45658) ou como texto.
# O tratamento abaixo garante a conversão correta em ambos os casos:
if pd.api.types.is_numeric_dtype(df['data_referencia']):
    # No Excel, datas começam a ser contadas a partir de 1899-12-30
    df['data_referencia'] = pd.to_datetime(df['data_referencia'], unit='D', origin='1899-12-30')
else:
    # Se for string ou formato padrão, to_datetime converte de forma segura
    df['data_referencia'] = pd.to_datetime(df['data_referencia'], errors='coerce')

# Criando a coluna de mês numérico (1 a 12)
df['numero_mes'] = df['data_referencia'].dt.month

# Dicionário para mapear o número do mês para o nome em português (Janeiro a Dezembro)
meses_pt = {
    1: '01 - Janeiro', 2: '02 - Fevereiro', 3: '03 - Março', 4: '04 - Abril',
    5: '05 - Maio', 6: '06 - Junho', 7: '07 - Julho', 8: '08 - Agosto',
    9: '09 - Setembro', 10: '10 - Outubro', 11: '11 - Novembro', 12: '12 - Dezembro'
}
df['mes_nome'] = df['numero_mes'].map(meses_pt)

# ==============================================================================
# 2. MAPEAMENTO DOS PRINCIPAIS INDICADORES
# ==============================================================================
# Classificamos os eventos em 3 grandes grupos de interesse:
# - CVLI: Crimes Violentos Letais Intencionais (Homicídio doloso, Feminicídio, Latrocínio, Lesão corporal seguida de morte)
# - Ocorrências de Trânsito: Mortes no trânsito
# - Mandados Cumpridos: Mandado de prisão cumprido
def classificar_indicador(evento):
    evento_str = str(evento).lower().strip()
    
    # 1. CVLI (Conceito oficial do Ministério da Justiça e Segurança Pública)
    if any(termo in evento_str for termo in [
        'homicídio doloso', 
        'feminicídio', 
        'latrocínio', 
        'roubo seguido de morte', 
        'lesão corporal seguida de morte'
    ]):
        return 'CVLI'
    
    # 2. Ocorrências de Trânsito
    elif 'trânsito' in evento_str:
        return 'Ocorrências de Trânsito'
    
    # 3. Mandados Cumpridos
    elif 'mandado de prisão cumprido' in evento_str or 'mandado' in evento_str:
        return 'Mandados Cumpridos'
    
    return None

# Aplica a classificação criando uma nova coluna
df['indicador'] = df['evento'].apply(classificar_indicador)

# Filtramos apenas os registros que pertencem aos 3 indicadores selecionados
df_indicadores = df[df['indicador'].notnull()].copy()

print("=" * 80)
print("EVOLUÇÃO MENSAL DOS INDICADORES EM 2025")
print("=" * 80)

# ==============================================================================
# ABORDAGEM A: USANDO GROUPBY
# ==============================================================================
# O groupby agrupa os dados por múltiplas colunas em formato hierárquico/vertical.
# Aqui agrupamos por [numero_mes, mes_nome, indicador] e somamos a coluna 'total'.
resumo_groupby = (
    df_indicadores.groupby(['numero_mes', 'mes_nome', 'indicador'])['total']
    .sum()
    .reset_index()
    .rename(columns={'total': 'Total_Ocorrencias'})
)

print("\n--- 1. RESULTADO COM GROUPBY (Formato Vertical / Tabela Longa) ---")
print(resumo_groupby.head(10).to_string(index=False))
print("... (dados continuam até dezembro)\n")

# ==============================================================================
# ABORDAGEM B: USANDO PIVOT_TABLE (TABELA DINÂMICA)
# ==============================================================================
# O pivot_table remodela os dados para formato horizontal (Tabela Dinâmica do Excel),
# colocando os meses nas linhas (index), os indicadores nas colunas (columns)
# e os valores calculados no centro (values).
tabela_pivo = pd.pivot_table(
    data=df_indicadores,
    values='total',          # Coluna numérica que queremos somar
    index='mes_nome',        # O que vai ficar nas linhas (Meses de Janeiro a Dezembro)
    columns='indicador',     # O que vai virar coluna (CVLI, Trânsito, Mandados)
    aggfunc='sum',           # Função de agregação matemática (soma)
    fill_value=0             # Substitui meses sem dados por 0 em vez de NaN
)

# Adiciona linha de total geral acumulado no ano
tabela_pivo.loc['TOTAL ANO 2025'] = tabela_pivo.sum()

print("=" * 80)
print("--- 2. RESULTADO COM PIVOT_TABLE (Formato Horizontal / Visão Executiva) ---")
print("=" * 80)
# Formatando com separador de milhar
tabela_pivo_formatada = tabela_pivo.map(lambda x: f"{int(x):,}".replace(",", "."))
print(tabela_pivo_formatada)
print("=" * 80)
