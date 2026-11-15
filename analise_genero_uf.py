"""
Script de Análise do Perfil Demográfico por Gênero e por Estado
Dataset: Segurança Pública do Brasil 2025 (BancoVDE 2025.csv / BancoVDE 2025.xlsx)
"""

from pathlib import Path
import pandas as pd
import numpy as np

# Configurações visuais do Pandas para o terminal
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def carregar_dados():
    """Carrega o dataset priorizando o CSV (muito mais rápido que Excel)."""
    caminhos_csv = [
        Path("data/BancoVDE 2025.csv"),
        Path("projeto_vde_jp/data/BancoVDE 2025.csv"),
        Path("../data/BancoVDE 2025.csv"),
    ]
    for p in caminhos_csv:
        if p.exists():
            print(f"Carregando dados via CSV: '{p}'...")
            return pd.read_csv(p, sep=";", encoding="utf-8-sig", low_memory=False)

    caminhos_xlsx = [
        Path("data/BancoVDE 2025.xlsx"),
        Path("projeto_vde_jp/data/BancoVDE 2025.xlsx"),
        Path("../data/BancoVDE 2025.xlsx"),
    ]
    for p in caminhos_xlsx:
        if p.exists():
            print(f"Carregando dados via Excel: '{p}'...")
            return pd.read_excel(p)

    raise FileNotFoundError("Base de dados BancoVDE 2025 não encontrada.")


def main():
    df = carregar_dados()

    # 1. Tratamento e conversão numérica
    df['feminino'] = pd.to_numeric(df['feminino'], errors='coerce').fillna(0)
    df['masculino'] = pd.to_numeric(df['masculino'], errors='coerce').fillna(0)

    # ==========================================================================
    # 2. ANÁLISE 1: PERFIL POR ESTADO (UF) E INDICADOR (EVENTO)
    # ==========================================================================
    print("\n" + "=" * 90)
    print("1. PERFIL DEMOGRÁFICO POR GÊNERO POR ESTADO E INDICADOR")
    print("=" * 90)

    df_uf_indicador = (
        df.groupby(['uf', 'evento'])[['feminino', 'masculino']]
        .sum()
        .reset_index()
    )

    # Total de vítimas/ocorrências com gênero registrado
    df_uf_indicador['total'] = df_uf_indicador['feminino'] + df_uf_indicador['masculino']

    # Porcentagens de cada gênero no total do indicador no estado
    df_uf_indicador['pct_feminino'] = np.where(
        df_uf_indicador['total'] > 0,
        (df_uf_indicador['feminino'] / df_uf_indicador['total']) * 100,
        0.0
    ).round(2)

    df_uf_indicador['pct_masculino'] = np.where(
        df_uf_indicador['total'] > 0,
        (df_uf_indicador['masculino'] / df_uf_indicador['total']) * 100,
        0.0
    ).round(2)

    # Filtrar registros com ocorrências para exibição limpa
    df_uf_com_vitimas = df_uf_indicador[df_uf_indicador['total'] > 0].copy()
    df_uf_com_vitimas = df_uf_com_vitimas.sort_values(by=['uf', 'total'], ascending=[True, False])

    # Formatação para o terminal
    amostra_exibicao = df_uf_com_vitimas.head(20).copy()
    amostra_exibicao['Feminino'] = amostra_exibicao['feminino'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    amostra_exibicao['Masculino'] = amostra_exibicao['masculino'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    amostra_exibicao['Total'] = amostra_exibicao['total'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    amostra_exibicao['% Feminino'] = amostra_exibicao['pct_feminino'].apply(lambda x: f"{x:.2f}%")
    amostra_exibicao['% Masculino'] = amostra_exibicao['pct_masculino'].apply(lambda x: f"{x:.2f}%")

    colunas_saida = ['uf', 'evento', 'Feminino', '% Feminino', 'Masculino', '% Masculino', 'Total']
    print(amostra_exibicao[colunas_saida].to_string(index=False))
    print(f"\nTotal de combinações [UF x Indicador] analisadas: {len(df_uf_com_vitimas)}")

    # ==========================================================================
    # 3. ANÁLISE 2: CONSOLIDADO GERAL POR INDICADOR (EVENTO)
    # ==========================================================================
    print("\n" + "=" * 90)
    print("2. CONSOLIDADO NACIONAL POR INDICADOR DE SEGURANÇA PÚBLICA")
    print("=" * 90)

    df_indicador = (
        df.groupby('evento')[['feminino', 'masculino']]
        .sum()
        .reset_index()
    )

    df_indicador['total'] = df_indicador['feminino'] + df_indicador['masculino']
    df_indicador = df_indicador[df_indicador['total'] > 0].sort_values(by='total', ascending=False).reset_index(drop=True)

    df_indicador['pct_feminino'] = ((df_indicador['feminino'] / df_indicador['total']) * 100).round(2)
    df_indicador['pct_masculino'] = ((df_indicador['masculino'] / df_indicador['total']) * 100).round(2)

    tabela_indicadores = df_indicador.copy()
    tabela_indicadores['Feminino'] = tabela_indicadores['feminino'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    tabela_indicadores['Masculino'] = tabela_indicadores['masculino'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    tabela_indicadores['Total'] = tabela_indicadores['total'].apply(lambda x: f"{int(x):,}".replace(",", "."))
    tabela_indicadores['% Feminino'] = tabela_indicadores['pct_feminino'].apply(lambda x: f"{x:.2f}%")
    tabela_indicadores['% Masculino'] = tabela_indicadores['pct_masculino'].apply(lambda x: f"{x:.2f}%")

    colunas_ind = ['evento', 'Feminino', '% Feminino', 'Masculino', '% Masculino', 'Total']
    print(tabela_indicadores[colunas_ind].to_string(index=False))

    # Exportação para CSV
    saida_uf = Path("perfil_genero_por_estado.csv")
    saida_ind = Path("perfil_genero_por_indicador.csv")
    df_uf_com_vitimas.to_csv(saida_uf, index=False, sep=";", encoding="utf-8-sig")
    df_indicador.to_csv(saida_ind, index=False, sep=";", encoding="utf-8-sig")
    print(f"\nArquivos exportados com sucesso:")
    print(f" -> {saida_uf}")
    print(f" -> {saida_ind}")

if __name__ == "__main__":
    main()
