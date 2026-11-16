# 🛡️ Painel de Inteligência e Estatísticas de Segurança Pública (VDE 2025/2026)

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Online_Demo-222222?style=for-the-badge&logo=github&logoColor=white)]([https://seu-usuario.github.io/seu-repositorio/](https://riquelmovski.github.io/painel-seguranca-publica/))

Painel analítico e georreferenciado de alto nível para exploração estatística de indicadores de segurança pública nas **27 Unidades Federativas do Brasil**, baseado nas estatísticas do Sistema VDE (Validação de Dados Estatísticos) do Ministério da Justiça e Segurança Pública (SINESP).

O projeto conta com interface moderna inspirada nas diretrizes do **Google Material 3**, mapa coroplético dinâmico em **Leaflet.js**, filtragem reativa e páginas individuais dedicadas a cada estado brasileiro.

---

<!-- Espaço reservado para screenshot do painel (salve uma imagem como preview.png na raiz do repositório) -->
## 📸 Demonstração Visual

![Preview do Dashboard](preview.png)

> 🔗 **Demonstração Online no GitHub Pages:**  
> [https://seu-usuario.github.io/seu-repositorio/](https://riquelmovski.github.io/painel-seguranca-publica/)

---

## 🔬 Metodologia e Indicadores Analíticos

Para garantir rigor estatístico e evitar distorções no diagnóstico da criminalidade, este painel aplica uma separação técnica estrita entre **ocorrências de segurança pública** e **atendimentos assistenciais/administrativos**.

### 1. Por que excluir bombeiros e atos administrativos?
Na base bruta unificada, registros de serviços do Corpo de Bombeiros (*Atendimento Pré-Hospitalar - APH, Busca e Salvamento, Combate a Incêndios*) e atos administrativos cartorários (*Emissão de Alvarás e Licenças, Vistorias*) representavam volumes que mascaravam os indicadores criminais. A inclusão desses dados criava falsas lideranças no ranking de estados que registram mais serviços civis. Neste painel, essas categorias são **excluídas das análises de criminalidade**.

### 2. Os 4 Grandes Eixos Estratégicos (Cards da UF)

| Indicador | Sigla | Critério e Composição | Regra de Exclusão Estrita |
|---|:---:|---|---|
| **Crimes Violentos Letais Intencionais** | **CVLI** | `Homicídio Doloso` + `Feminicídio` + `Roubo seguido de Morte (Latrocínio)` + `Lesão Corporal seguida de Morte`. | ❌ **NÃO** inclui tentativas, suicídios, sinistros de trânsito nem mortes por intervenção policial. |
| **Crimes Violentos contra o Patrimônio** | **CVP** | `Roubo de Veículo` + `Roubo de Carga` + `Roubo a Instituição Financeira` + `Roubo seguido de Morte (Latrocínio)`. | ❌ **NÃO** inclui `Furto de Veículo` (delito clandestino sem violência ou grave ameaça à pessoa). |
| **Mandados de Prisão Cumpridos** | **MP** | Quantitativo exato de prisões judiciais cumpridas pelas forças policiais. | Mede a produtividade e a repressão qualificada da polícia judiciária e ostensiva. |
| **Armas de Fogo Apreendidas** | **AP** | Volume de armamentos de fogo retirados de circulação em operações. | Indicador direto de enfrentamento ao crime organizado e desarmamento. |

---

## ✨ Funcionalidades Principais

- 🗺️ **Mapa Coroplético Interativo do Brasil:**
  - Renderização vetorial dos 27 estados sobre o basemap *CartoDB Positron* via **Leaflet.js**.
  - Malha oficial de fronteiras geográficas do **IBGE** (GeoJSON leve e otimizado).
  - Escala cromática estatística adaptativa recalibrada dinamicamente pelo valor máximo da métrica selecionada.
  - Tooltips suspensos interativos com visual de card Google Style exibindo UF, volume, ranking e percentual de participação nacional.
  - Clique em qualquer estado com redirecionamento direto para sua página dedicada.

- 🏛️ **27 Páginas Individuais por Unidade Federativa (`/estado/<UF>/`):**
  - **4 Cards Analíticos Principais:** Total de CVLI, Total de CVP, Mandados de Prisão Cumpridos e Armas de Fogo Apreendidas, com posição no ranking do país.
  - **Decomposição Analítica dos Sub-indicadores:** Painéis comparativos com barras de progresso mostrando o percentual de cada tipificação delituosa dentro do CVLI e do CVP.
  - **Série Temporal Mensal:** Gráfico de linha/área com gradiente suave demonstrando a evolução de janeiro a dezembro de 2025 (Chart.js).
  - **Top 10 Delitos Predominantes:** Gráfico de barras horizontais ranqueando a incidência local.
  - **Tabela Filtrável em Tempo Real:** Campo de busca rápida no cliente com decomposição de vítimas por gênero e quantitativo total.

- 🧭 **Navegação Eficiente e Minimalista:**
  - Mega Menu suspenso flutuante com as 27 UFs categorizadas nas 5 Grandes Regiões do Brasil (*Nordeste, Sudeste, Sul, Centro-Oeste e Norte*).
  - Menu dinâmico de indicadores para alternar instantaneamente o tipo de ocorrência no mapa nacional.
  - Botão de exportação dos dados tabulados em formato CSV.

---

## 🛠️ Tecnologias Utilizadas

### Frontend
- **HTML5 Semântico & CSS3 Moderno**
- **Tailwind CSS v3.4** (via CDN com personalização Google Material 3)
- **Tipografia:** Google Sans / Plus Jakarta Sans (Google Fonts)
- **Leaflet.js v1.9.4:** Renderização e interatividade de dados georreferenciados
- **CartoDB Positron:** Basemap elegante e minimalista em alta definição
- **Chart.js:** Visualizações estatísticas com gradientes e animações
- **GeoJSON do IBGE:** Malha cartográfica vetorial dos 27 estados

### Backend & Processamento de Dados
- **Python 3.9+**
- **Django 5.x:** Framework web robusto para rotas, renderização e controle de cache
- **Pandas & NumPy:** Ingestão de alto desempenho do CSV, tratamento analítico e agregação com `@lru_cache` na memória RAM

### Deploy & Compatibilidade
- **GitHub Pages:** Suporte completo via exportação estática (`index.html` e `estado/<UF>/`)
- **Django Runserver / WSGI:** Suporte completo para servidores locais e de produção

---

## 📂 Estrutura de Arquivos do Repositório

```text
├── index.html                  # Página inicial estática compilada para o GitHub Pages
├── gerar_site_estatico.py      # Script de automação que exporta o Django para o GitHub Pages
├── README.md                   # Documentação técnica e guia do repositório
├── .gitignore                  # Arquivos e diretórios ignorados pelo Git
├── manage.py                   # Gerenciador CLI do Django
│
├── config/                     # Configurações globais do Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── dashboard/                  # Aplicação principal do Painel
│   ├── views.py                # Lógica de cálculo dos KPIs, rankings e agregação com Pandas
│   ├── urls.py                 # Rotas do dashboard e endpoints da API
│   ├── static/dashboard/geo/   # Malha GeoJSON oficial dos estados do Brasil
│   └── templates/dashboard/    # Templates HTML com Tailwind e Chart.js
│       ├── index.html          # Template da Visão Nacional e Mapa Leaflet
│       └── detalhe_estado.html # Template da página dedicada por Estado (UF)
│
├── data/                       # Base de dados estatística oficial
│   └── BancoVDE 2025.csv       # Microdados oficiais de segurança pública
│
├── estado/                     # Páginas estáticas dos 27 estados pré-compiladas (GitHub Pages)
│   ├── AC/index.html
│   ├── AL/index.html
│   └── ... (27 UFs)
│
└── geo/                        # Arquivos geográficos públicos
    └── brasil_estados.json     # Malha vetorial para renderização offline no GitHub Pages
```

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
- Python 3.9 ou superior instalado ([python.org](https://www.python.org/downloads/))
- Git instalado ([git-scm.com](https://git-scm.com/))

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Criar e Ativar o Ambiente Virtual
```bash
# No macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# No Windows:
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar as Dependências
```bash
pip install django pandas numpy
```

### 4. Executar as Migrações e Iniciar o Servidor
```bash
python manage.py migrate
python manage.py runserver
```

Abra o seu navegador em: **`http://127.0.0.1:8000/`**

---

## ⚡ Como Atualizar a Versão Estática para o GitHub Pages

Sempre que você alterar dados ou modificar os templates do Django, execute o script de exportação automatizada para atualizar os arquivos estáticos:

```bash
python gerar_site_estatico.py
```

O script renderizará automaticamente o `index.html` e todas as 27 páginas em `estado/<UF>/index.html` com caminhos relativos prontos para o GitHub Pages.

---

## 📄 Licença

Este projeto é disponibilizado sob a licença **MIT**. Os dados estatísticos são de domínio público, providos pelo Ministério da Justiça e Segurança Pública através do SINESP / Sistema VDE.
