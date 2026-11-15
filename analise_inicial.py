"""
Script de Análise Inicial de Dados - Segurança Pública do Brasil 2025
Autor: Especialista em Análise de Dados com Python & Pandas
"""

import os
from pathlib import Path
import pandas as pd

# Ajuste opcional para visualização no terminal: exibe todas as colunas sem cortar com '...'
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ==============================================================================
# 1. CARREGAR O ARQUIVO USANDO PANDAS
# ==============================================================================
# Identifica o caminho do arquivo (funciona executando da raiz ou de dentro de projeto_vde_jp)
caminhos_possiveis = [
    Path("data/BancoVDE 2025.xlsx"),
    Path("projeto_vde_jp/data/BancoVDE 2025.xlsx"),
]

caminho_arquivo = next((p for p in caminhos_possiveis if p.exists()), Path("data/BancoVDE 2025.xlsx"))

print(f"Carregando o arquivo: '{caminho_arquivo}'...")
print("(Arquivos Excel grandes podem levar alguns segundos para carregar)\n")

# Lendo a planilha Excel
df = pd.read_excel(caminho_arquivo)
print("-> Arquivo carregado com sucesso!\n")

# ==============================================================================
# 2. EXIBIR O TOTAL DE LINHAS E COLUNAS
# ==============================================================================
linhas, colunas = df.shape
print("=" * 60)
print("2. DIMENSÕES DO CONJUNTO DE DADOS")
print("=" * 60)
print(f"Total de Linhas : {linhas:,}".replace(",", "."))
print(f"Total de Colunas: {colunas}")
print()

# ==============================================================================
# 3. LISTAR OS NOMES DAS COLUNAS E SEUS TIPOS DE DADOS
# ==============================================================================
print("=" * 60)
print("3. COLUNAS E SEUS TIPOS DE DADOS (dtypes)")
print("=" * 60)
print(df.dtypes)
print()

# ==============================================================================
# 4. VERIFICAR A QUANTIDADE DE VALORES NULOS/VAZIOS EM CADA COLUNA
# ==============================================================================
print("=" * 60)
print("4. QUANTIDADE DE VALORES NULOS/VAZIOS POR COLUNA")
print("=" * 60)
nulos = df.isnull().sum()
# Criamos um resumo mostrando a contagem e a porcentagem de nulos
resumo_nulos = pd.DataFrame({
    'Valores Nulos': nulos,
    'Porcentagem (%)': (nulos / linhas * 100).round(2)
})
print(resumo_nulos)
print()

# ==============================================================================
# 5. IMPRIMIR AS 5 PRIMEIRAS LINHAS DA TABELA DE FORMA FORMATADA
# ==============================================================================
print("=" * 60)
print("5. PRIMEIRAS 5 LINHAS DA TABELA (df.head())")
print("=" * 60)
print(df.head(5))
print("=" * 60)
