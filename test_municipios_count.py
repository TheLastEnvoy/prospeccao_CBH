#!/usr/bin/env python3
"""
Script para testar a contagem correta de municípios
"""

import os
import sys
import django
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_osc.settings')
django.setup()

from osc_dashboard.views import get_filter_options
import json

def test_municipios_count():
    """Testa a contagem de municípios"""
    print("🧪 Testando contagem de municípios...")
    
    try:
        # Obter opções de filtro
        filter_options = get_filter_options()
        
        municipios_list = filter_options['municipios']
        municipios_json = json.dumps(municipios_list)
        
        print(f"\n📊 Resultados:")
        print(f"   Municípios únicos (lista): {len(municipios_list)}")
        print(f"   Municípios únicos (esperado): 399")
        print(f"   JSON string length: {len(municipios_json)} caracteres")
        
        # Verificar se a contagem está correta
        if len(municipios_list) == 399:
            print("   ✅ Contagem correta!")
        else:
            print(f"   ❌ Contagem incorreta! Esperado: 399, Obtido: {len(municipios_list)}")
        
        # Mostrar alguns exemplos
        print(f"\n📝 Primeiros 10 municípios:")
        for i, municipio in enumerate(municipios_list[:10], 1):
            print(f"   {i:2d}. {municipio}")
        
        # Verificar se há duplicatas
        municipios_set = set(municipios_list)
        if len(municipios_set) == len(municipios_list):
            print(f"\n✅ Não há municípios duplicados")
        else:
            print(f"\n❌ Há municípios duplicados!")
            print(f"   Lista: {len(municipios_list)} itens")
            print(f"   Set: {len(municipios_set)} itens únicos")
            
            # Encontrar duplicatas
            duplicatas = []
            seen = set()
            for municipio in municipios_list:
                if municipio in seen:
                    duplicatas.append(municipio)
                else:
                    seen.add(municipio)
            
            if duplicatas:
                print(f"   Duplicatas encontradas: {duplicatas[:5]}...")
        
        # Verificar se há municípios vazios
        municipios_vazios = [m for m in municipios_list if not m or m.strip() == '']
        if municipios_vazios:
            print(f"\n⚠️  Municípios vazios encontrados: {len(municipios_vazios)}")
        else:
            print(f"\n✅ Não há municípios vazios")
        
        return len(municipios_list) == 399
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_context():
    """Simula o contexto que seria passado para o template"""
    print("\n🧪 Testando contexto do template...")
    
    try:
        filter_options = get_filter_options()
        
        # Simular o contexto da view dashboard
        context = {
            'municipios': filter_options['municipios'],  # Lista para contagem no template
            'municipios_json': json.dumps(filter_options['municipios']),  # JSON para JavaScript
            'naturezas_juridicas': filter_options['naturezas_juridicas'],
            'total_registros': filter_options['total_registros']
        }
        
        print(f"\n📊 Contexto do template:")
        print(f"   municipios (lista): {len(context['municipios'])} itens")
        print(f"   municipios_json (string): {len(context['municipios_json'])} caracteres")
        print(f"   naturezas_juridicas: {len(context['naturezas_juridicas'])} itens")
        print(f"   total_registros: {context['total_registros']}")
        
        # Simular o que aconteceria no template
        municipios_length = len(context['municipios'])  # {{ municipios|length }}
        print(f"\n🎯 No template:")
        print(f"   {{{{ municipios|length }}}} = {municipios_length}")
        
        if municipios_length == 399:
            print("   ✅ Card mostrará 399 municípios (correto!)")
        else:
            print(f"   ❌ Card mostrará {municipios_length} municípios (incorreto!)")
        
        return municipios_length == 399
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 TESTE DA CORREÇÃO DA CONTAGEM DE MUNICÍPIOS")
    print("=" * 60)
    
    success1 = test_municipios_count()
    success2 = test_template_context()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("   O card de municípios agora mostrará 399 (correto)")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("   Verifique os problemas acima")
    print("=" * 60)

if __name__ == "__main__":
    main()
