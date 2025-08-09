#!/usr/bin/env python3
"""
Script para verificar se o projeto está pronto para deploy no Render
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Verifica se um arquivo existe"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NÃO ENCONTRADO")
        return False

def check_file_content(file_path, required_content, description):
    """Verifica se um arquivo contém conteúdo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if required_content in content:
                print(f"✅ {description}: OK")
                return True
            else:
                print(f"❌ {description}: Conteúdo não encontrado")
                return False
    except FileNotFoundError:
        print(f"❌ {description}: Arquivo não encontrado")
        return False

def check_database():
    """Verifica o banco de dados"""
    db_path = "data/oscs_parana_novo.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        size_mb = size / (1024 * 1024)
        print(f"✅ Banco de dados: {db_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"❌ Banco de dados: {db_path} - NÃO ENCONTRADO")
        return False

def check_git_status():
    """Verifica status do Git"""
    try:
        import subprocess
        
        # Verificar se há mudanças não commitadas
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("⚠️  Git: Há mudanças não commitadas")
                print("   Execute: git add . && git commit -m 'Deploy ready'")
                return False
            else:
                print("✅ Git: Todas as mudanças commitadas")
                return True
        else:
            print("⚠️  Git: Não é um repositório Git ou Git não instalado")
            return False
    except FileNotFoundError:
        print("⚠️  Git: Comando git não encontrado")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 VERIFICAÇÃO PRÉ-DEPLOY PARA RENDER")
    print("=" * 60)
    
    checks = []
    
    # Verificar arquivos essenciais
    print("\n📁 Verificando arquivos essenciais...")
    checks.append(check_file_exists("render.yaml", "Configuração Render"))
    checks.append(check_file_exists("build.sh", "Script de build"))
    checks.append(check_file_exists("requirements.txt", "Dependências Python"))
    checks.append(check_file_exists("manage.py", "Django manage.py"))
    checks.append(check_file_exists("dashboard_osc/settings.py", "Configurações Django"))
    checks.append(check_file_exists("dashboard_osc/wsgi.py", "WSGI application"))
    
    # Verificar banco de dados
    print("\n🗄️ Verificando banco de dados...")
    checks.append(check_database())
    
    # Verificar conteúdo dos arquivos
    print("\n📝 Verificando conteúdo dos arquivos...")
    checks.append(check_file_content("requirements.txt", "gunicorn", "Gunicorn em requirements.txt"))
    checks.append(check_file_content("requirements.txt", "whitenoise", "WhiteNoise em requirements.txt"))
    checks.append(check_file_content("dashboard_osc/settings.py", "ALLOWED_HOSTS", "ALLOWED_HOSTS configurado"))
    checks.append(check_file_content("build.sh", "collectstatic", "collectstatic no build.sh"))
    
    # Verificar estrutura de diretórios
    print("\n📂 Verificando estrutura de diretórios...")
    checks.append(check_file_exists("static", "Diretório static"))
    checks.append(check_file_exists("templates", "Diretório templates"))
    checks.append(check_file_exists("data", "Diretório data"))
    checks.append(check_file_exists("osc_dashboard", "App osc_dashboard"))
    
    # Verificar Git
    print("\n🔄 Verificando Git...")
    git_ok = check_git_status()
    
    # Resumo
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total and git_ok:
        print("🎉 PROJETO PRONTO PARA DEPLOY!")
        print(f"   ✅ {passed}/{total} verificações passaram")
        print("   ✅ Git status OK")
        print("\n🚀 Próximos passos:")
        print("   1. Faça push para o repositório remoto")
        print("   2. Acesse render.com e crie um novo Web Service")
        print("   3. Conecte seu repositório")
        print("   4. O Render detectará render.yaml automaticamente")
    else:
        print("❌ PROJETO NÃO ESTÁ PRONTO!")
        print(f"   ❌ {passed}/{total} verificações passaram")
        if not git_ok:
            print("   ❌ Git status com problemas")
        print("\n🔧 Corrija os problemas acima antes do deploy")
    
    print("=" * 60)
    
    return passed == total and git_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
