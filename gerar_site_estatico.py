#!/usr/bin/env python3
"""
Script de Exportação Estática para GitHub Pages
------------------------------------------------
Renderiza e exporta as páginas do Django (index e as 27 UFs) em arquivos HTML estáticos
compatíveis com o GitHub Pages, ajustando caminhos relativos para CSS, JS e GeoJSON.
"""

import os
import sys
import shutil
from pathlib import Path

# Configuração do ambiente Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import RequestFactory
from dashboard.views import index, detalhe_estado, NOMES_ESTADOS

def exportar():
    rf = RequestFactory()
    print("🚀 Iniciando exportação estática para o GitHub Pages...")

    # 1. Gerar index.html principal
    print("📄 Renderizando index.html...")
    req = rf.get('/')
    resp = index(req)
    html_index = resp.content.decode('utf-8')

    # Ajuste de rotas para navegação estática no GitHub Pages
    html_index = html_index.replace("window.location.href = '/estado/' + sigla + '/';", "window.location.href = 'estado/' + sigla + '/';")
    html_index = html_index.replace('href="/estado/', 'href="estado/')
    html_index = html_index.replace('href="/"', 'href="index.html"')
    html_index = html_index.replace('"{% url "dashboard:geojson_estados" %}"', '"geo/brasil_estados.json"')
    html_index = html_index.replace('"/api/geojson/estados/"', '"geo/brasil_estados.json"')
    html_index = html_index.replace('href="/exportar-csv/"', 'href="data/BancoVDE 2025.csv" download')

    index_path = BASE_DIR / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_index)
    print(f"✅ index.html gerado com sucesso ({index_path.stat().st_size:,} bytes)")

    # 2. Copiar malha geográfica GeoJSON para geo/brasil_estados.json
    geo_dir = BASE_DIR / 'geo'
    geo_dir.mkdir(exist_ok=True)
    origem_geo = BASE_DIR / 'dashboard' / 'static' / 'dashboard' / 'geo' / 'brasil_estados.json'
    if origem_geo.exists():
        shutil.copy(origem_geo, geo_dir / 'brasil_estados.json')
        print("✅ geo/brasil_estados.json atualizado com sucesso!")

    # 3. Gerar as 27 páginas de estados em estado/<UF>/index.html
    estado_dir = BASE_DIR / 'estado'
    estado_dir.mkdir(exist_ok=True)
    print(f"🏛️ Renderizando {len(NOMES_ESTADOS)} páginas individuais de estados...")

    for uf in NOMES_ESTADOS.keys():
        uf_dir = estado_dir / uf
        uf_dir.mkdir(exist_ok=True)

        req_uf = rf.get(f'/estado/{uf}/')
        resp_uf = detalhe_estado(req_uf, uf)
        html_uf = resp_uf.content.decode('utf-8')

        # Ajuste de rotas relativas nos subdiretórios estado/<UF>/
        html_uf = html_uf.replace('href="/"', 'href="../../index.html"')
        html_uf = html_uf.replace('href="/estado/', 'href="../../estado/')
        html_uf = html_uf.replace('href="/exportar-csv/"', 'href="../../data/BancoVDE 2025.csv" download')

        with open(uf_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html_uf)

    print("✅ Todas as 27 páginas de estados geradas em estado/<UF>/index.html com sucesso!")
    print("🎉 Exportação concluída! O projeto está pronto para o GitHub Pages.")

if __name__ == '__main__':
    exportar()
