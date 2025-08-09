#!/usr/bin/env python3
"""
Script para testar o fluxo completo da UI
"""

import os
import sys
import django
import json
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_osc.settings')
django.setup()

from django.test import RequestFactory
from django.http import JsonResponse
from osc_dashboard.views import filter_data

def test_ui_simulation():
    """Simula exatamente o que a UI faz"""
    print("🧪 Simulando fluxo completo da UI...")
    
    # Simular dados que o JavaScript enviaria
    # Cenário: usuário selecionou Palmeira e adicionou palavra-chave "rural"
    
    # 1. Usuário digita "rural" e clica no botão +
    keywords_array = ['rural']  # Array JavaScript
    keywords_string = ' '.join(keywords_array)  # getKeywordsString()
    
    # 2. Usuário seleciona município "Palmeira"
    municipios_array = ['Palmeira']  # Array JavaScript
    municipios_string = ','.join(municipios_array)  # getMunicipiosString()
    
    # 3. Dados enviados via AJAX
    request_data = {
        'municipio': municipios_string,
        'natureza_juridica': '',
        'palavras_chave': keywords_string,
        'naturezas_ver': [],
        'page': 1,
        'per_page': 50
    }
    
    print(f"\n📤 Dados enviados pela UI:")
    print(f"   municipio: '{request_data['municipio']}'")
    print(f"   palavras_chave: '{request_data['palavras_chave']}'")
    print(f"   natureza_juridica: '{request_data['natureza_juridica']}'")
    print(f"   naturezas_ver: {request_data['naturezas_ver']}")
    
    # 4. Simular requisição POST
    factory = RequestFactory()
    request = factory.post(
        '/filter/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    # 5. Chamar a view
    try:
        response = filter_data(request)
        
        if isinstance(response, JsonResponse):
            response_data = json.loads(response.content.decode('utf-8'))
            
            print(f"\n📥 Resposta do backend:")
            print(f"   Status: {response.status_code}")
            print(f"   Total encontrado: {response_data.get('total', 'N/A')}")
            print(f"   Registros na página: {len(response_data.get('data', []))}")
            print(f"   Página atual: {response_data.get('page', 'N/A')}")
            print(f"   Total de páginas: {response_data.get('total_pages', 'N/A')}")
            
            if 'error' in response_data:
                print(f"   ❌ Erro: {response_data['error']}")
                return False
            
            # Mostrar alguns resultados
            data = response_data.get('data', [])
            if data:
                print(f"\n📋 Primeiros resultados:")
                for i, osc in enumerate(data[:3], 1):
                    nome = osc.get('nome', 'N/A')
                    municipio = osc.get('edmu_nm_municipio', 'N/A')
                    print(f"   {i}. {nome[:50]}... - {municipio}")
                
                return True
            else:
                print(f"\n❌ Nenhum resultado retornado!")
                return False
        else:
            print(f"\n❌ Resposta inválida: {type(response)}")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro na requisição: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_empty_keywords():
    """Testa com array de palavras-chave vazio"""
    print("\n🧪 Testando com palavras-chave vazias...")
    
    request_data = {
        'municipio': 'Palmeira',
        'natureza_juridica': '',
        'palavras_chave': '',  # String vazia
        'naturezas_ver': [],
        'page': 1,
        'per_page': 50
    }
    
    factory = RequestFactory()
    request = factory.post(
        '/filter/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    try:
        response = filter_data(request)
        response_data = json.loads(response.content.decode('utf-8'))
        
        print(f"   Total OSCs em Palmeira (sem filtro de palavra): {response_data.get('total', 'N/A')}")
        
        return response_data.get('total', 0) == 171  # Esperado: 171 OSCs em Palmeira
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_multiple_keywords():
    """Testa com múltiplas palavras-chave"""
    print("\n🧪 Testando com múltiplas palavras-chave...")
    
    # Simular: usuário adicionou "rural" e "agua"
    keywords_array = ['rural', 'agua']
    keywords_string = ' '.join(keywords_array)
    
    request_data = {
        'municipio': 'Palmeira',
        'natureza_juridica': '',
        'palavras_chave': keywords_string,  # "rural agua"
        'naturezas_ver': [],
        'page': 1,
        'per_page': 50
    }
    
    print(f"   Palavras-chave: '{keywords_string}'")
    
    factory = RequestFactory()
    request = factory.post(
        '/filter/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    try:
        response = filter_data(request)
        response_data = json.loads(response.content.decode('utf-8'))
        
        total = response_data.get('total', 0)
        print(f"   Total encontrado: {total}")
        
        # Deve encontrar OSCs que tenham "rural" OU "agua" no nome
        return total > 0
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_case_variations():
    """Testa variações de maiúsculas/minúsculas"""
    print("\n🧪 Testando variações de case...")
    
    test_cases = ['rural', 'Rural', 'RURAL']
    
    for case in test_cases:
        request_data = {
            'municipio': 'Palmeira',
            'natureza_juridica': '',
            'palavras_chave': case,
            'naturezas_ver': [],
            'page': 1,
            'per_page': 50
        }
        
        factory = RequestFactory()
        request = factory.post(
            '/filter/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        try:
            response = filter_data(request)
            response_data = json.loads(response.content.decode('utf-8'))
            total = response_data.get('total', 0)
            print(f"   '{case}': {total} OSCs")
            
        except Exception as e:
            print(f"   '{case}': Erro - {e}")

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 TESTE DO FLUXO COMPLETO DA UI")
    print("=" * 60)
    
    success1 = test_ui_simulation()
    success2 = test_empty_keywords()
    success3 = test_multiple_keywords()
    test_case_variations()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("   O sistema está funcionando corretamente")
        print("   Se o usuário não vê resultados, pode ser problema na interface")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("   Há problema no backend")
    print("=" * 60)

if __name__ == "__main__":
    main()
