# 🚀 Deploy do Dashboard OSCs Paraná no Render

## 📋 **Pré-requisitos**

1. **Conta no Render:** [render.com](https://render.com)
2. **Repositório Git:** Código deve estar no GitHub, GitLab ou Bitbucket
3. **Banco de dados:** Arquivo `data/oscs_parana_novo.db` deve estar no repositório

## 🔧 **Preparação do Projeto**

### ✅ **Arquivos já configurados:**
- ✅ `render.yaml` - Configuração automática do Render
- ✅ `build.sh` - Script de build melhorado
- ✅ `requirements.txt` - Dependências Python
- ✅ `dashboard_osc/settings.py` - Configurações de produção
- ✅ `env_example.txt` - Exemplo de variáveis de ambiente

### 📁 **Estrutura necessária:**
```
dashboard_prospeccao/
├── data/
│   └── oscs_parana_novo.db    # ⚠️ IMPORTANTE: Banco de dados
├── static/                    # Arquivos CSS/JS
├── templates/                 # Templates HTML
├── dashboard_osc/            # Configurações Django
├── osc_dashboard/            # App principal
├── render.yaml               # Configuração Render
├── build.sh                  # Script de build
├── requirements.txt          # Dependências
└── manage.py                 # Django management
```

## 🚀 **Passo a Passo do Deploy**

### **1. Preparar o Repositório**

```bash
# 1. Adicionar todos os arquivos ao Git
git add .

# 2. Commit das mudanças
git commit -m "Preparação para deploy no Render"

# 3. Push para o repositório remoto
git push origin main
```

### **2. Criar Serviço no Render**

1. **Acesse:** [dashboard.render.com](https://dashboard.render.com)
2. **Clique:** "New +" → "Web Service"
3. **Conecte:** Seu repositório Git
4. **Configure:**
   - **Name:** `dashboard-oscs-parana`
   - **Environment:** `Python`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn dashboard_osc.wsgi:application`
   - **Plan:** `Free` (ou `Starter` para melhor performance)

### **3. Configurar Variáveis de Ambiente**

No painel do Render, adicione as seguintes variáveis:

```env
SECRET_KEY=sua-chave-secreta-aqui-muito-longa-e-aleatoria
DEBUG=false
ALLOWED_HOSTS=*
WEB_CONCURRENCY=4
PYTHON_VERSION=3.11.4
```

**⚠️ Importante:** O Render gerará automaticamente uma `SECRET_KEY` se você usar o `render.yaml`.

### **4. Deploy Automático**

O Render detectará o `render.yaml` e configurará automaticamente:
- ✅ Ambiente Python 3.11.4
- ✅ Build command: `./build.sh`
- ✅ Start command: `gunicorn dashboard_osc.wsgi:application`
- ✅ Variáveis de ambiente básicas

## 📊 **Verificação do Deploy**

### **Durante o Build:**
```bash
🚀 Iniciando build do Dashboard OSCs Paraná...
📦 Instalando dependências...
🗄️ Verificando banco de dados...
📁 Coletando arquivos estáticos...
🔄 Executando migrações...
✅ Build concluído com sucesso!
```

### **Após o Deploy:**
1. **URL:** `https://seu-app-name.onrender.com`
2. **Status:** Deve mostrar "Live"
3. **Logs:** Verificar se não há erros

## 🔍 **Troubleshooting**

### **Problema: Banco de dados não encontrado**
```bash
⚠️ Banco de dados não encontrado em data/oscs_parana_novo.db
```
**Solução:**
1. Certifique-se de que o arquivo `data/oscs_parana_novo.db` está no repositório
2. Verifique se o arquivo não está no `.gitignore`
3. Faça commit e push do arquivo

### **Problema: Erro de static files**
```bash
Error: collectstatic failed
```
**Solução:**
1. Verifique se `STATIC_ROOT` está configurado
2. Certifique-se de que `whitenoise` está instalado
3. Verifique permissões dos arquivos

### **Problema: Aplicação não inicia**
```bash
Error: Application failed to start
```
**Solução:**
1. Verifique logs no painel do Render
2. Confirme se `gunicorn` está em `requirements.txt`
3. Verifique se `ALLOWED_HOSTS` inclui o domínio do Render

## ⚡ **Otimizações de Performance**

### **1. Configurações de Produção**
```python
# Já configurado em settings.py
DEBUG = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### **2. Gunicorn Workers**
```env
WEB_CONCURRENCY=4  # Ajuste conforme o plano
```

### **3. Static Files**
- ✅ WhiteNoise configurado para servir arquivos estáticos
- ✅ Compressão automática habilitada
- ✅ Cache headers otimizados

## 💰 **Planos do Render**

### **Free Plan (Recomendado para teste):**
- ✅ 750 horas/mês
- ✅ Suspende após 15min de inatividade
- ✅ 512MB RAM
- ✅ Ideal para demonstração

### **Starter Plan ($7/mês):**
- ✅ Sempre ativo
- ✅ 1GB RAM
- ✅ Melhor performance
- ✅ Ideal para produção

## 🔄 **Deploy Contínuo**

Após configuração inicial:
1. **Push para main** → Deploy automático
2. **Logs em tempo real** no painel
3. **Rollback fácil** se necessário

## 📱 **Acesso ao Dashboard**

Após deploy bem-sucedido:
- **URL:** `https://seu-app-name.onrender.com`
- **Funcionalidades:**
  - ✅ Filtros múltiplos (municípios, naturezas, palavras-chave)
  - ✅ Tabela responsiva
  - ✅ Exportação Excel
  - ✅ Mapa interativo
  - ✅ 50.585 OSCs do Paraná

## 🎯 **Checklist Final**

Antes do deploy, verifique:
- [ ] Banco de dados `data/oscs_parana_novo.db` no repositório
- [ ] Código commitado e pushed
- [ ] Variáveis de ambiente configuradas
- [ ] `render.yaml` presente
- [ ] `build.sh` executável
- [ ] `requirements.txt` atualizado

## 🆘 **Suporte**

Se encontrar problemas:
1. **Logs do Render:** Painel → Logs
2. **Documentação:** [render.com/docs](https://render.com/docs)
3. **Status:** [status.render.com](https://status.render.com)

---

**🎉 Pronto! Seu Dashboard OSCs Paraná estará disponível globalmente no Render!**
