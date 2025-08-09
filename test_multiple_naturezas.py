#!/usr/bin/env python3
"""
Script para testar múltiplas naturezas jurídicas
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
from osc_dashboard.views import filter_data, get_filter_options

def test_single_natureza():
    """Testa com uma única natureza jurídica"""
    print("🧪 Testando uma única natureza jurídica...")
    
    request_data = {
        'municipio': '',
        'natureza_juridica': 'Associação Privada',
        'palavras_chave': '',
        'naturezas_ver': [],
        'page': 1,
        'per_page': 50
    }
    
    factory = RequestFactory()
    request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
    
    try:
        response = filter_data(request)
        response_data = json.loads(response.content.decode('utf-8'))
        
        total = response_data.get('total', 0)
        print(f"   'Associação Privada': {total} OSCs")
        return total > 0
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_multiple_naturezas():
    """Testa com múltiplas naturezas jurídicas"""
    print("\n🧪 Testando múltiplas naturezas jurídicas...")
    
    # Primeiro, vamos ver quais naturezas existem
    filter_options = get_filter_options()
    naturezas_disponiveis = filter_options['naturezas_juridicas']
    print(f"   Naturezas disponíveis: {naturezas_disponiveis}")
    
    # Testar com 2 naturezas
    if len(naturezas_disponiveis) >= 2:
        naturezas_teste = naturezas_disponiveis[:2]
        naturezas_string = ','.join(naturezas_teste)
        
        request_data = {
            'municipio': '',
            'natureza_juridica': naturezas_string,
            'palavras_chave': '',
            'naturezas_ver': [],
            'page': 1,
            'per_page': 50
        }
        
        factory = RequestFactory()
        request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
        
        try:
            response = filter_data(request)
            response_data = json.loads(response.content.decode('utf-8'))
            
            total = response_data.get('total', 0)
            print(f"   '{naturezas_string}': {total} OSCs")
            
            # Verificar se o total é maior que cada natureza individual
            totais_individuais = []
            for natureza in naturezas_teste:
                individual_data = {
                    'municipio': '',
                    'natureza_juridica': natureza,
                    'palavras_chave': '',
                    'naturezas_ver': [],
                    'page': 1,
                    'per_page': 50
                }
                
                individual_request = factory.post('/filter/', data=json.dumps(individual_data), content_type='application/json')
                individual_response = filter_data(individual_request)
                individual_response_data = json.loads(individual_response.content.decode('utf-8'))
                individual_total = individual_response_data.get('total', 0)
                totais_individuais.append(individual_total)
                print(f"     '{natureza}' individual: {individual_total} OSCs")
            
            # O total combinado deve ser >= ao maior individual (pode ser menor se houver sobreposição)
            max_individual = max(totais_individuais)
            if total >= max_individual:
                print(f"   ✅ Lógica OR funcionando: {total} >= {max_individual}")
                return True
            else:
                print(f"   ❌ Problema na lógica OR: {total} < {max_individual}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False
    else:
        print("   ⚠️ Não há naturezas suficientes para teste")
        return True

def test_combined_filters():
    """Testa filtros combinados: município + múltiplas naturezas"""
    print("\n🧪 Testando filtros combinados...")
    
    filter_options = get_filter_options()
    naturezas_disponiveis = filter_options['naturezas_juridicas']
    
    if len(naturezas_disponiveis) >= 2:
        naturezas_teste = naturezas_disponiveis[:2]
        naturezas_string = ','.join(naturezas_teste)
        
        request_data = {
            'municipio': 'Curitiba',
            'natureza_juridica': naturezas_string,
            'palavras_chave': '',
            'naturezas_ver': [],
            'page': 1,
            'per_page': 50
        }
        
        factory = RequestFactory()
        request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
        
        try:
            response = filter_data(request)
            response_data = json.loads(response.content.decode('utf-8'))
            
            total = response_data.get('total', 0)
            print(f"   Curitiba + '{naturezas_string}': {total} OSCs")
            
            # Mostrar alguns exemplos se encontrou resultados
            if total > 0:
                data = response_data.get('data', [])
                print(f"   Exemplos encontrados:")
                for i, osc in enumerate(data[:3], 1):
                    nome = osc.get('nome', 'N/A')
                    natureza = osc.get('natureza_juridica', 'N/A')
                    municipio = osc.get('edmu_nm_municipio', 'N/A')
                    print(f"     {i}. {nome[:40]}... - {natureza} - {municipio}")
            
            return total >= 0  # Qualquer resultado é válido
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False
    else:
        print("   ⚠️ Não há naturezas suficientes para teste")
        return True

def test_edge_cases():
    """Testa casos extremos"""
    print("\n🧪 Testando casos extremos...")
    
    # Teste 1: String vazia
    request_data = {
        'municipio': '',
        'natureza_juridica': '',
        'palavras_chave': '',
        'naturezas_ver': [],
        'page': 1,
        'per_page': 50
    }
    
    factory = RequestFactory()
    request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
    
    try:
        response = filter_data(request)
        response_data = json.loads(response.content.decode('utf-8'))
        total = response_data.get('total', 0)
        print(f"   Sem filtros: {total} OSCs")
        
        # Teste 2: Natureza inexistente
        request_data['natureza_juridica'] = 'Natureza Inexistente'
        request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
        response = filter_data(request)
        response_data = json.loads(response.content.decode('utf-8'))
        total_inexistente = response_data.get('total', 0)
        print(f"   Natureza inexistente: {total_inexistente} OSCs")
        
        return total > 0 and total_inexistente == 0
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 TESTE DE MÚLTIPLAS NATUREZAS JURÍDICAS")
    print("=" * 60)
    
    success1 = test_single_natureza()
    success2 = test_multiple_naturezas()
    success3 = test_combined_filters()
    success4 = test_edge_cases()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3 and success4:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("   Sistema de múltiplas naturezas jurídicas funcionando")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("   Verifique os problemas acima")
    print("=" * 60)

if __name__ == "__main__":
    main()
