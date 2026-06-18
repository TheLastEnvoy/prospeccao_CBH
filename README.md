# Dashboard de Prospeccao - CBHs do Parana

Aplicacao Django para prospeccao de Organizacoes da Sociedade Civil (OSCs) no Parana e para exploracao espacial de dados ligados aos Comites de Bacias Hidrograficas.

Hoje o projeto possui dois focos principais:

1. **Painel de prospeccao de OSCs** com filtros, tabela de resultados e exportacao.
2. **Mapa interativo de outorgas** com classificacao dinamica da camada GeoJSON.

## Acesso online

- Producao: https://prospeccao-cbh.onrender.com

## O que existe no projeto hoje

### 1. Painel de prospeccao de OSCs

Rota principal: `/`

Funcionalidades atuais:

- filtros por municipio, natureza juridica, situacao cadastral e palavras-chave
- leitura de dados a partir de banco SQLite local
- tabela de resultados no frontend
- exportacao de resultados para Excel
- apoio territorial por CBH e municipios

### 2. Mapa interativo de outorgas

Rota: `/mapa-outorgas/`

Funcionalidades atuais:

- mapa Leaflet com base OpenStreetMap
- leitura da camada `static/geojson/outorgas2_IAT.geojson`
- classificacao da camada por:
  - `outorgas_IAT_agrupado_CBH_COMITE`
  - `outorgas_IAT_agrupado_ATV_MACRO`
  - `bac_nome`
- legenda dinamica
- popup com atributos principais da outorga
- tabela superior com quantitativos da classificacao ativa
- tabela inferior com totais por CBH e atividade macro

## Stack atual

- **Backend:** Django 4.2.7
- **Linguagem:** Python
- **Dados tabulares:** SQLite + pandas
- **Exportacao:** openpyxl
- **Frontend:** Bootstrap 5 + JavaScript
- **Mapas:** Leaflet
- **Arquivos estaticos em producao:** WhiteNoise
- **Deploy:** Render

## Estrutura relevante

```text
dashboard_osc/              Configuracao do projeto Django
osc_dashboard/              App principal
templates/osc_dashboard/    Templates HTML
static/css/                 Estilos
static/js/                  Scripts do frontend
static/geojson/             Camadas GeoJSON usadas no app
data/oscs_parana_novo.db    Base SQLite consumida pelo dashboard de OSCs
render.yaml                 Configuracao de deploy no Render
build.sh                    Script de build/deploy
```

## Rotas principais

- `/` - dashboard de prospeccao de OSCs
- `/mapa-outorgas/` - mapa interativo de outorgas
- `/filter/` - endpoint de filtragem
- `/export/` - exportacao de dados
- `/municipios-data/` - endpoint auxiliar de municipios
- `/mapa-teste/` - pagina de teste do mapa

## Dados esperados pelo projeto

### Banco SQLite

O dashboard principal usa o arquivo:

```text
data/oscs_parana_novo.db
```

Esse banco e lido diretamente pelas views para buscar:

- OSCs
- municipios
- naturezas juridicas
- situacoes cadastrais
- relacionamento entre CBHs e municipios

### GeoJSON de outorgas

O mapa de outorgas usa:

```text
static/geojson/outorgas2_IAT.geojson
```

Esse arquivo ja faz parte do repositorio e e servido como arquivo estatico pelo Django/WhiteNoise.

## Execucao local

### 1. Clonar o repositorio

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

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variaveis de ambiente

Voce pode usar `env_example.txt` como referencia. Exemplo minimo:

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

O projeto ja esta preparado para deploy com:

- `render.yaml`
- `build.sh`
- WhiteNoise para servir arquivos estaticos

O build atual executa:

1. instalacao de dependencias
2. `collectstatic`
3. `migrate`

Comandos principais:

- **Build:** `./build.sh`
- **Start:** `gunicorn dashboard_osc.wsgi:application`

## Observacoes importantes

- O dashboard de OSCs depende da existencia de `data/oscs_parana_novo.db`.
- O mapa de outorgas depende do GeoJSON versionado em `static/geojson/outorgas2_IAT.geojson`.
- O GeoJSON de outorgas e grande, entao o carregamento no navegador pode ser mais pesado que o restante do sistema.

## Desenvolvimento

Checagem rapida do projeto:

```bash
python manage.py check
```

## Suporte

Para ajustes, correcoes ou novas funcionalidades, abra uma issue ou uma pull request.
