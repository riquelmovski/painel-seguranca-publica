"""
Script de Enriquecimento de Dados, Taxas por 100k Habitantes e Detecção de Anomalias
Autor: Especialista em Análise de Dados com Python & Pandas
"""

from pathlib import Path
import pandas as pd
import numpy as np

# Configuração de visualização
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ==============================================================================
# 1. CARREGAMENTO DOS DADOS ORIGINAIS
# ==============================================================================
caminhos = [
    Path("data/BancoVDE 2025.xlsx"),
    Path("projeto_vde_jp/data/BancoVDE 2025.xlsx"),
]
caminho = next((p for p in caminhos if p.exists()), Path("data/BancoVDE 2025.xlsx"))
df = pd.read_excel(caminho)

# ==============================================================================
# 2. O PROBLEMA DOS NÚMEROS ABSOLUTOS: POR QUE PRECISAMOS DE TAXAS?
# ==============================================================================
# Um estado populoso como SP terá mais mortes em números brutos do que o AC.
# Porém, para comparar a violência real, a ONU e o Ministério da Justiça usam:
# Taxa por 100 mil hab = (Total de Crimes / População) * 100.000

# Criamos uma base de referência populacional por UF (Estimativas IBGE)
populacao_uf = pd.DataFrame({
    'uf': ['SP', 'MG', 'RJ', 'BA', 'PR', 'RS', 'PE', 'CE', 'PA', 'SC',
           'MA', 'GO', 'PB', 'ES', 'AM', 'RN', 'AL', 'PI', 'MT', 'DF',
           'MS', 'SE', 'RO', 'TO', 'AC', 'AP', 'RR'],
    'populacao': [
        44411238, 20538718, 16054524, 14141626, 11444380, 10882965, 9058931,
        8794957, 8121025, 7610361, 6776699, 7056495, 3974687, 3833712, 3941613,
        3302729, 3127683, 3271199, 3658649, 2817342, 2757013, 2210004, 1581196,
        1511460, 830018, 733759, 636707
    ]
})

# ==============================================================================
# 3. ENRIQUECIMENTO DE DADOS COM pd.merge()
# ==============================================================================
# Filtramos apenas os crimes de CVLI (Homicídio doloso, Feminicídio, Latrocínio, Lesão seg. morte)
termos_cvli = ['homicídio doloso', 'feminicídio', 'latrocínio', 'roubo seguido de morte', 'lesão corporal seguida de morte']
df_cvli = df[df['evento'].astype(str).str.lower().str.contains('|'.join(termos_cvli), na=False)]

# Total de CVLI por Estado
cvli_por_uf = df_cvli.groupby('uf')['total_vitima'].sum().reset_index()

# Cruzando os dados de CVLI com a População usando MERGE (semelhante ao INNER JOIN do SQL)
dados_consolidados = pd.merge(cvli_por_uf, populacao_uf, on='uf', how='inner')

# Cálculo da Taxa por 100 mil habitantes
dados_consolidados['taxa_por_100k'] = (
    (dados_consolidados['total_vitima'] / dados_consolidados['populacao']) * 100000
).round(2)

# Ordenando pelo ranking de violência real (Taxa por 100 mil habitantes)
ranking_taxas = dados_consolidados.sort_values(by='taxa_por_100k', ascending=False).reset_index(drop=True)

print("=" * 80)
print("RANKING REAL DE CVLI: NÚMEROS ABSOLUTOS VS TAXA POR 100 MIL HABITANTES")
print("=" * 80)
print(ranking_taxas.head(10).to_string(index=True))
print()

# ==============================================================================
# 4. DETECÇÃO DE ANOMALIAS E OUTLIERS (ALERTA VERMELHO COM Z-SCORE)
# ==============================================================================
# O Z-score mede quantos desvios-padrão um valor está distante da média:
# Z = (X - Média) / Desvio_Padrão
# Valores com Z > 2 indicam uma criminalidade significativamente acima do padrão nacional.

media_taxa = ranking_taxas['taxa_por_100k'].mean()
desvio_taxa = ranking_taxas['taxa_por_100k'].std()

ranking_taxas['z_score'] = ((ranking_taxas['taxa_por_100k'] - media_taxa) / desvio_taxa).round(2)

# Identificando Estados em Alerta Crítico (Anomalias estatísticas)
alertas_criticos = ranking_taxas[ranking_taxas['z_score'] > 1.5]

print("=" * 80)
print(f"Média Nacional da Taxa: {media_taxa:.2f} por 100k | Desvio Padrão: {desvio_taxa:.2f}")
print("🚨 ESTADOS EM ALERTA CRÍTICO (Z-Score > 1.5):")
print("=" * 80)
if not alertas_criticos.empty:
    print(alertas_criticos[['uf', 'total_vitima', 'populacao', 'taxa_por_100k', 'z_score']].to_string(index=False))
else:
    print("Nenhum estado ultrapassou o limiar crítico de anomalia.")
print("=" * 80)
