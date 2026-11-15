"""
Script de Análise de Eventos e Ocorrências - Segurança Pública 2025
Autor: Especialista em Análise de Dados com Python & Pandas
"""

from pathlib import Path
import pandas as pd

# Ajustes de exibição do Pandas para tabelas legíveis
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# 1. Carregamento do arquivo
caminhos_possiveis = [
    Path("data/BancoVDE 2025.xlsx"),
    Path("projeto_vde_jp/data/BancoVDE 2025.xlsx"),
]
caminho_arquivo = next((p for p in caminhos_possiveis if p.exists()), Path("data/BancoVDE 2025.xlsx"))

print(f"Carregando dataset de: {caminho_arquivo}...")
df = pd.read_excel(caminho_arquivo)
print("Dados carregados com sucesso!\n")

# ==============================================================================
# 1. LISTAR TODOS OS TIPOS ÚNICOS DE EVENTOS REGISTRADOS
# ==============================================================================
print("=" * 70)
print("1. TIPOS ÚNICOS DE EVENTOS REGISTRADOS NA COLUNA 'evento'")
print("=" * 70)

# unique() retorna os valores sem repetição
eventos_unicos = df['evento'].dropna().unique()
print(f"Total de tipos de eventos catalogados: {len(eventos_unicos)}\n")

for i, ev in enumerate(sorted(eventos_unicos), 1):
    print(f"  {i:02d}. {ev}")
print()

# ==============================================================================
# 2. CALCULAR A SOMA DE OCORRÊNCIAS ('total') E VÍTIMAS ('total_vitima') POR EVENTO
# ==============================================================================
print("=" * 70)
print("2. SOMA DE OCORRÊNCIAS E VÍTIMAS POR EVENTO")
print("=" * 70)

# Agrupando por 'evento' e somando as colunas 'total' e 'total_vitima'
resumo_eventos = df.groupby('evento')[['total', 'total_vitima']].sum()

# ==============================================================================
# 3. ORDENAR DO MAIOR VOLUME PARA O MENOR
# ==============================================================================
# Ordenamos pela coluna 'total' (ocorrências) em ordem decrescente
resumo_ordenado = resumo_eventos.sort_values(by='total', ascending=False).reset_index()

# ==============================================================================
# 4. TABELA LEGÍVEL E DESTAQUE DOS 3 MAIORES EVENTOS
# ==============================================================================
print("=" * 70)
print("3 & 4. TABELA GERAL ORDENADA (Top Eventos)")
print("=" * 70)

# Criando uma cópia formatada para visualização amigável
tabela_formatada = resumo_ordenado.copy()
tabela_formatada.columns = ['Evento', 'Total Ocorrências', 'Total Vítimas']
tabela_formatada['Total Ocorrências'] = tabela_formatada['Total Ocorrências'].apply(lambda x: f"{int(x):,}".replace(",", "."))
tabela_formatada['Total Vítimas'] = tabela_formatada['Total Vítimas'].apply(lambda x: f"{int(x):,}".replace(",", "."))

print(tabela_formatada.to_string(index=False))
print()

# Destacando o TOP 3 Geral
print("*" * 70)
print("🔥 DESTAQUE: TOP 3 EVENTOS COM MAIOR NÚMERO DE OCORRÊNCIAS (GERAL)")
print("*" * 70)
top3_geral = resumo_ordenado.head(3)
for pos, (_, row) in enumerate(top3_geral.iterrows(), 1):
    print(f"  🏆 {pos}º Lugar: {row['evento']} -> {int(row['total']):,} ocorrências ({int(row['total_vitima']):,} vítimas)".replace(",", "."))
print()

# ==============================================================================
# 4.1 DESTAQUE DOS 3 MAIORES EVENTOS NO MUNICÍPIO ESPECÍFICO
# ==============================================================================
print("=" * 70)
print("4.1 FILTRO POR MUNICÍPIO ESPECÍFICO (Exemplo: JOÃO PESSOA ou personalizável)")
print("=" * 70)

def top3_por_municipio(dataframe, nome_municipio):
    # Filtra ignorando maiúsculas/minúsculas
    filtro = dataframe['municipio'].astype(str).str.upper() == nome_municipio.upper()
    df_muni = dataframe[filtro]
    
    if df_muni.empty:
        print(f"Nenhum registro encontrado para o município '{nome_municipio}'.")
        return
        
    resumo_muni = (
        df_muni.groupby('evento')[['total', 'total_vitima']]
        .sum()
        .sort_values(by='total', ascending=False)
        .reset_index()
    )
    
    print(f"\n--- TOP 3 EVENTOS DE MAIOR VOLUME EM: {nome_municipio.upper()} ---")
    for pos, (_, row) in enumerate(resumo_muni.head(3).iterrows(), 1):
        print(f"  {pos}º Lugar: {row['evento']} | {int(row['total']):,} ocorrências | {int(row['total_vitima']):,} vítimas".replace(",", "."))

# Exemplo de execução para um município:
# top3_por_municipio(df, "JOÃO PESSOA")
