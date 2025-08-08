# Dashboard OSCs Paraná

Dashboard web para visualização e exportação de dados de Organizações da Sociedade Civil (OSCs) do Paraná.

## 🚀 Funcionalidades

- **Visualização de dados**: Tabela interativa com 18.620 OSCs do Paraná
- **Filtros avançados**:
  - Por município (399 municípios disponíveis)
  - Por natureza jurídica
  - Por palavras-chave no nome da OSC
  - Exclusão de naturezas jurídicas específicas
- **Exportação**: Download dos dados filtrados em formato Excel (.xlsx)
- **Interface moderna**: Design responsivo com Bootstrap 5
- **Paginação**: Navegação eficiente pelos resultados

## 📊 Dados Disponíveis

- **18.620 OSCs** do Paraná
- **399 municípios** únicos
- **Informações completas**: Nome, email, endereço, telefone, natureza jurídica, município

## 🛠️ Tecnologias

- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5, jQuery, DataTables
- **Dados**: Pandas, OpenPyXL
- **Hospedagem**: Render (compatível)

## 📦 Instalação Local

### Pré-requisitos
- Python 3.8+
- pip

### Passos

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd dashboard_prospeccao
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
cp env_example.txt .env

# Edite o arquivo .env com suas configurações
```

4. **Execute as migrações**
```bash
python manage.py migrate
```

5. **Inicie o servidor**
```bash
python manage.py runserver
```

6. **Acesse a aplicação**
```
http://localhost:8000
```

## 🚀 Deploy no Render

### 1. Preparação
- Faça push do código para um repositório Git (GitHub, GitLab, etc.)

### 2. Configuração no Render
1. Acesse [render.com](https://render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório
4. Configure o serviço:
   - **Name**: `dashboard-oscs-parana`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn dashboard_osc.wsgi:application`

### 3. Variáveis de Ambiente
Configure as seguintes variáveis no Render:
```
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com
```

### 4. Deploy
- Clique em "Create Web Service"
- Aguarde o build e deploy automático

## 📁 Estrutura do Projeto

```
dashboard_prospeccao/
├── dashboard_osc/          # Configurações do Django
├── osc_dashboard/          # Aplicação principal
├── templates/              # Templates HTML
├── data/                   # Dados CSV
├── core/utils/             # Scripts de processamento
├── requirements.txt        # Dependências Python
├── build.sh               # Script de build para Render
└── README.md              # Este arquivo
```

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SECRET_KEY` | Chave secreta do Django | `django-insecure-your-secret-key-here` |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |

### Arquivo de Dados

O sistema utiliza o arquivo `data/dados_osc_PR_completo.csv` que contém:
- 18.620 registros de OSCs
- 9 colunas: id_osc, nome, email, endereco, telefone, natureza_juridica, situacao_cadastral, edmu_cd_municipio, edmu_nm_municipio

## 🎯 Uso

### Filtros Disponíveis

1. **Município**: Selecione um município específico
2. **Natureza Jurídica**: Filtre por tipo de organização
3. **Palavras-chave**: Busque no nome da OSC
4. **Naturezas a Ignorar**: Exclua tipos específicos de organização

### Exportação

- Clique em "Exportar Excel" para baixar os dados filtrados
- O arquivo será gerado com timestamp no nome
- Colunas renomeadas para melhor visualização

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório do projeto.
