# Dashboard de Prospecção - CBHs do Paraná

Aplicação Django para prospecção de Organizações da Sociedade Civil (OSCs) no Paraná e para exploração espacial de dados ligados aos Comitês de Bacias Hidrográficas.

Hoje o projeto possui dois focos principais:

1. **Painel de prospecção de OSCs** com filtros, tabela de resultados e exportação.
2. **Mapa interativo de outorgas** com classificação dinâmica da camada GeoJSON.

## Acesso online

- Produção: https://prospeccao-cbh.onrender.com

## O que existe no projeto hoje

### 1. Painel de prospecção de OSCs

Rota principal: `/`

Funcionalidades atuais:

- filtros por município, natureza jurídica, situação cadastral e palavras-chave
- leitura de dados a partir de banco SQLite local
- tabela de resultados no frontend
- exportação de resultados para Excel
- apoio territorial por CBH e municípios

### 2. Mapa interativo de outorgas

Rota: `/mapa-outorgas/`

Funcionalidades atuais:

- mapa Leaflet com base OpenStreetMap
- leitura da camada `static/geojson/outorgas2_IAT.geojson`
- classificação da camada por:
  - `outorgas_IAT_agrupado_CBH_COMITE`
  - `outorgas_IAT_agrupado_ATV_MACRO`
  - `bac_nome`
- legenda dinâmica
- popup com atributos principais da outorga
- tabela superior com quantitativos da classificação ativa
- tabela inferior com totais por CBH e atividade macro

## Stack atual

- **Backend:** Django 4.2.7
- **Linguagem:** Python
- **Dados tabulares:** SQLite + pandas
- **Exportação:** openpyxl
- **Frontend:** Bootstrap 5 + JavaScript
- **Mapas:** Leaflet
- **Arquivos estáticos em produção:** WhiteNoise
- **Deploy:** Render

## Estrutura relevante

```text
dashboard_osc/              Configuração do projeto Django
osc_dashboard/              App principal
templates/osc_dashboard/    Templates HTML
static/css/dashboard-theme.css  Tokens visuais e estilos reutilizáveis do dashboard
static/css/                 Estilos
static/js/                  Scripts do frontend
static/geojson/             Camadas GeoJSON usadas no app
data/oscs_parana_novo.db    Base SQLite consumida pelo dashboard de OSCs
render.yaml                 Configuração de deploy no Render
build.sh                    Script de build/deploy
```

## Rotas principais

- `/` - dashboard de prospecção de OSCs
- `/mapa-outorgas/` - mapa interativo de outorgas
- `/filter/` - endpoint de filtragem
- `/export/` - exportação de dados
- `/municipios-data/` - endpoint auxiliar de municípios
- `/mapa-teste/` - página de teste do mapa

## Dados esperados pelo projeto

### Banco SQLite

O dashboard principal usa o arquivo:

```text
data/oscs_parana_novo.db
```

Esse banco é lido diretamente pelas views para buscar:

- OSCs
- municípios
- naturezas jurídicas
- situações cadastrais
- relacionamento entre CBHs e municípios

### GeoJSON de outorgas

O mapa de outorgas usa:

```text
static/geojson/outorgas2_IAT.geojson
```

Esse arquivo já faz parte do repositório e é servido como arquivo estático pelo Django/WhiteNoise.

## Execução local

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd prospeccao_CBH
```

### 2. Criar e ativar ambiente virtual

No Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Você pode usar `env_example.txt` como referência. Exemplo mínimo:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Rodar o projeto

```bash
python manage.py runserver
```

Depois acesse:

- Dashboard OSCs: http://127.0.0.1:8000/
- Mapa de outorgas: http://127.0.0.1:8000/mapa-outorgas/

## Deploy no Render

O projeto já está preparado para deploy com:

- `render.yaml`
- `build.sh`
- WhiteNoise para servir arquivos estáticos

O build atual executa:

1. instalação de dependências
2. `collectstatic`
3. `migrate`

Comandos principais:

- **Build:** `./build.sh`
- **Start:** `gunicorn dashboard_osc.wsgi:application`

## Observações importantes

- O dashboard de OSCs depende da existência de `data/oscs_parana_novo.db`.
- O mapa de outorgas depende do GeoJSON versionado em `static/geojson/outorgas2_IAT.geojson`.
- O GeoJSON de outorgas é grande, então o carregamento no navegador pode ser mais pesado que o restante do sistema.
- A paleta de cores e os estilos-base reutilizáveis ficam em `static/css/dashboard-theme.css`.

## Desenvolvimento

Checagem rápida do projeto:

```bash
python manage.py check
```

## Suporte

Para ajustes, correções ou novas funcionalidades, abra uma issue ou uma pull request.
