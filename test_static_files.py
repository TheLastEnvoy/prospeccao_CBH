#!/usr/bin/env python3
"""
Script para testar a coleta de arquivos estáticos
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_osc.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.contrib.staticfiles import finders

def check_static_dirs():
    """Verifica diretórios de arquivos estáticos"""
    print("📁 Verificando diretórios de arquivos estáticos...")
    
    # Diretório source
    static_dir = settings.BASE_DIR / 'static'
    if static_dir.exists():
        files = list(static_dir.rglob('*'))
        print(f"   ✅ static/ : {len(files)} arquivos")
        
        # Listar principais arquivos
        css_files = list(static_dir.rglob('*.css'))
        js_files = list(static_dir.rglob('*.js'))
        print(f"      - CSS: {len(css_files)} arquivos")
        print(f"      - JS: {len(js_files)} arquivos")
        
        for css in css_files[:3]:
            print(f"        📄 {css.relative_to(static_dir)}")
        for js in js_files[:3]:
            print(f"        📄 {js.relative_to(static_dir)}")
    else:
        print(f"   ❌ static/ não encontrado")
    
    # Diretório de destino
    static_root = Path(settings.STATIC_ROOT)
    if static_root.exists():
        files = list(static_root.rglob('*'))
        print(f"   ✅ staticfiles/ : {len(files)} arquivos coletados")
    else:
        print(f"   ⚠️  staticfiles/ não existe (será criado no collectstatic)")

def test_collectstatic():
    """Testa o comando collectstatic"""
    print("\n🔄 Testando collectstatic...")
    
    try:
        # Executar collectstatic
        call_command('collectstatic', '--no-input', '--verbosity=2')
        
        # Verificar resultado
        static_root = Path(settings.STATIC_ROOT)
        if static_root.exists():
            files = list(static_root.rglob('*'))
            print(f"   ✅ Coletados {len(files)} arquivos em {static_root}")
            
            # Verificar arquivos específicos importantes
            important_files = [
                'css/dashboard.css',
                'js/dashboard.js',
                'admin/css/base.css',  # Django admin
            ]
            
            for file_path in important_files:
                full_path = static_root / file_path
                if full_path.exists():
                    size = full_path.stat().st_size
                    print(f"      ✅ {file_path} ({size} bytes)")
                else:
                    print(f"      ❌ {file_path} não encontrado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no collectstatic: {e}")
        return False

def test_finders():
    """Testa os finders de arquivos estáticos"""
    print("\n🔍 Testando finders de arquivos estáticos...")
    
    test_files = [
        'css/dashboard.css',
        'js/dashboard.js',
        'admin/css/base.css',
    ]
    
    for file_path in test_files:
        found = finders.find(file_path)
        if found:
            print(f"   ✅ {file_path} encontrado em: {found}")
        else:
            print(f"   ❌ {file_path} não encontrado")

def check_whitenoise_config():
    """Verifica configuração do WhiteNoise"""
    print("\n⚪ Verificando configuração WhiteNoise...")
    
    # Verificar middleware
    if 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE:
        print("   ✅ WhiteNoiseMiddleware configurado")
    else:
        print("   ❌ WhiteNoiseMiddleware não encontrado")
    
    # Verificar storage
    if 'whitenoise' in settings.STATICFILES_STORAGE:
        print(f"   ✅ Storage: {settings.STATICFILES_STORAGE}")
    else:
        print(f"   ⚠️  Storage: {settings.STATICFILES_STORAGE}")
    
    # Verificar configurações
    print(f"   📁 STATIC_URL: {settings.STATIC_URL}")
    print(f"   📁 STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"   📁 STATICFILES_DIRS: {settings.STATICFILES_DIRS}")

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 TESTE DE ARQUIVOS ESTÁTICOS")
    print("=" * 60)
    
    check_static_dirs()
    check_whitenoise_config()
    test_finders()
    success = test_collectstatic()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ARQUIVOS ESTÁTICOS CONFIGURADOS CORRETAMENTE!")
        print("   Pronto para deploy no Render")
    else:
        print("❌ PROBLEMAS COM ARQUIVOS ESTÁTICOS!")
        print("   Verifique os erros acima")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
