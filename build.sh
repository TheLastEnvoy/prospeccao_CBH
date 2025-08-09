#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Iniciando build do Dashboard OSCs Paraná..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verificar se o banco de dados existe
echo "🗄️ Verificando banco de dados..."
if [ ! -f "data/oscs_parana_novo.db" ]; then
    echo "⚠️ Banco de dados não encontrado em data/oscs_parana_novo.db"
    echo "   Certifique-se de que o arquivo está no repositório"
fi

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
echo "   Diretório static source: $(ls -la static/ | wc -l) arquivos"
python manage.py collectstatic --no-input --verbosity=2
echo "   Diretório staticfiles: $(ls -la staticfiles/ | wc -l) arquivos coletados"

# Executar migrações (se necessário)
echo "🔄 Executando migrações..."
python manage.py migrate

echo "✅ Build concluído com sucesso!"
