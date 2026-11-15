"""
Script de Análise dos Meios Empregados (Armas), Forças de Segurança (Agentes) e Faixa Etária
Dataset: BancoVDE 2025.xlsx
Autor: Especialista em Análise de Dados com Python & Pandas
"""

from pathlib import Path
import pandas as pd

# Configurações visuais do Pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ==============================================================================
# 1. CARREGAMENTO DOS DADOS
# ==============================================================================
caminhos = [
    Path("data/BancoVDE 2025.xlsx"),
    Path("projeto_vde_jp/data/BancoVDE 2025.xlsx"),
]
caminho = next((p for p in caminhos if p.exists()), Path("data/BancoVDE 2025.xlsx"))
print(f"Carregando {caminho}...\n")
df = pd.read_excel(caminho)

# ==============================================================================
# 2. ANÁLISE DE ARMAS (MEIOS EMPREGADOS)
# ==============================================================================
print("=" * 80)
print("1. DISTRIBUIÇÃO POR TIPO DE ARMA (ARMA DE FOGO / MEIO EMPREGADO)")
print("=" * 80)

# Filtrando linhas onde o campo 'arma' está preenchido
df_armas = df[df['arma'].notnull() & (df['arma'] != '')].copy()

resumo_armas = (
    df_armas.groupby('arma')['total']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={'total': 'Total_Ocorrencias'})
)

# Adiciona coluna de porcentagem (%)
resumo_armas['% Participacao'] = (resumo_armas['Total_Ocorrencias'] / resumo_armas['Total_Ocorrencias'].sum() * 100).round(2)
resumo_armas['Total_Ocorrencias'] = resumo_armas['Total_Ocorrencias'].apply(lambda x: f"{int(x):,}".replace(",", "."))
resumo_armas['% Participacao'] = resumo_armas['% Participacao'].apply(lambda x: f"{x:.2f}%")

print(resumo_armas.to_string(index=False))
print()

# ==============================================================================
# 3. ANÁLISE DE FAIXA ETÁRIA (MAIORIDADE VS MENORIDADE)
# ==============================================================================
print("=" * 80)
print("2. DISTRIBUIÇÃO DAS VÍTIMAS POR FAIXA ETÁRIA")
print("=" * 80)

df_faixa = df[df['faixa_etaria'].notnull() & (df['faixa_etaria'] != '')].copy()

resumo_faixa = (
    df_faixa.groupby('faixa_etaria')['total_vitima']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={'total_vitima': 'Total_Vitimas'})
)

resumo_faixa['% Participacao'] = (resumo_faixa['Total_Vitimas'] / resumo_faixa['Total_Vitimas'].sum() * 100).round(2)
resumo_faixa['Total_Vitimas'] = resumo_faixa['Total_Vitimas'].apply(lambda x: f"{int(x):,}".replace(",", "."))
resumo_faixa['% Participacao'] = resumo_faixa['% Participacao'].apply(lambda x: f"{x:.2f}%")

print(resumo_faixa.to_string(index=False))
print()

# ==============================================================================
# 4. ANÁLISE DE ATUAÇÃO POR AGENTE / FORÇA DE SEGURANÇA
# ==============================================================================
print("=" * 80)
print("3. REGISTROS POR FORÇA POLICIAL / AGENTE DE SEGURANÇA")
print("=" * 80)

df_agentes = df[df['agente'].notnull() & (df['agente'] != '')].copy()

resumo_agentes = (
    df_agentes.groupby('agente')['total']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={'total': 'Total_Registros'})
)

resumo_agentes['% Participacao'] = (resumo_agentes['Total_Registros'] / resumo_agentes['Total_Registros'].sum() * 100).round(2)
resumo_agentes['Total_Registros'] = resumo_agentes['Total_Registros'].apply(lambda x: f"{int(x):,}".replace(",", "."))
resumo_agentes['% Participacao'] = resumo_agentes['% Participacao'].apply(lambda x: f"{x:.2f}%")

print(resumo_agentes.to_string(index=False))
print()

# ==============================================================================
# 5. TABELA DE CONTINGÊNCIA COM pd.crosstab() (ARMA VS FAIXA ETÁRIA)
# ==============================================================================
print("=" * 80)
print("4. TABELA DE CONTINGÊNCIA (pd.crosstab): ARMA VS FAIXA ETÁRIA")
print("=" * 80)

# O crosstab cruza a frequência de duas variáveis categóricas
tabela_cruzada = pd.crosstab(
    index=df['arma'].fillna('Não especificado'),
    columns=df['faixa_etaria'].fillna('Não especificado'),
    values=df['total'],
    aggfunc='sum'
).fillna(0)

# Formatando para exibição limpa
tabela_cruzada_formatada = tabela_cruzada.map(lambda x: f"{int(x):,}".replace(",", "."))
print(tabela_cruzada_formatada)
print("=" * 80)
