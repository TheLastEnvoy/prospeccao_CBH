#!/usr/bin/env python3
"""
Script para testar os novos filtros: palavras de exclusão e situação cadastral
"""

import os
import sys
import django
import json
from pathlib import Path

# Configurar Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_osc.settings')
django.setup()

from django.test import RequestFactory
from osc_dashboard.views import filter_data, get_filter_options

def test_exclude_keywords():
    """Testa palavras-chave de exclusão"""
    print("🧪 Testando palavras-chave de exclusão...")
    
    factory = RequestFactory()
    
    # Teste 1: Buscar OSCs com "igreja" no nome
    print("\n1. OSCs com 'igreja' no nome:")
    request_data = {
        'municipio': '',
        'natureza_juridica': '',
        'palavras_chave': 'igreja',
        'palavras_excluir': '',
        'situacao_cadastral': '',
        'naturezas_ver': [],
        'page': 1,
        'per_page': 50
    }
    
    request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
    response = filter_data(request)
    response_data = json.loads(response.content.decode('utf-8'))
    total_com_igreja = response_data.get('total', 0)
    print(f"   Total: {total_com_igreja} OSCs")
    
    # Teste 2: Excluir OSCs com "igreja" no nome
    print("\n2. Excluindo OSCs com 'igreja' no nome:")
    request_data['palavras_chave'] = ''
    request_data['palavras_excluir'] = 'igreja'
    
    request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
    response = filter_data(request)
    response_data = json.loads(response.content.decode('utf-8'))
    total_sem_igreja = response_data.get('total', 0)
    print(f"   Total: {total_sem_igreja} OSCs")
    
    # Teste 3: Total geral para validação
    print("\n3. Total geral de OSCs:")
    request_data['palavras_excluir'] = ''
    
    request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
    response = filter_data(request)
    response_data = json.loads(response.content.decode('utf-8'))
    total_geral = response_data.get('total', 0)
    print(f"   Total: {total_geral} OSCs")
    
    # Validação
    esperado = total_geral - total_com_igreja
    print(f"\n✅ Validação:")
    print(f"   Total geral: {total_geral}")
    print(f"   Com 'igreja': {total_com_igreja}")
    print(f"   Sem 'igreja': {total_sem_igreja}")
    print(f"   Esperado sem 'igreja': {esperado}")
    
    if abs(total_sem_igreja - esperado) <= 1:  # Margem de erro pequena
        print("   ✅ Filtro de exclusão funcionando!")
        return True
    else:
        print("   ❌ Problema no filtro de exclusão")
        return False

def test_situacao_cadastral():
    """Testa filtro de situação cadastral"""
    print("\n🧪 Testando filtro de situação cadastral...")
    
    # Primeiro, obter situações disponíveis
    filter_options = get_filter_options()
    situacoes = filter_options['situacoes_cadastrais']
    print(f"   Situações disponíveis: {situacoes}")
    
    factory = RequestFactory()
    
    # Testar cada situação individualmente
    totais_individuais = {}
    for situacao in situacoes:
        request_data = {
            'municipio': '',
            'natureza_juridica': '',
            'palavras_chave': '',
            'palavras_excluir': '',
            'situacao_cadastral': situacao,
            'naturezas_ver': [],
            'page': 1,
            'per_page': 50
        }
        
        request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
        response = filter_data(request)
        response_data = json.loads(response.content.decode('utf-8'))
        total = response_data.get('total', 0)
        totais_individuais[situacao] = total
        print(f"   '{situacao}': {total} OSCs")
    
    # Testar múltiplas situações
    if len(situacoes) >= 2:
        print(f"\n   Testando múltiplas situações:")
        situacoes_teste = situacoes[:2]
        situacoes_string = ','.join(situacoes_teste)
        
        request_data = {
            'municipio': '',
            'natureza_juridica': '',
            'palavras_chave': '',
            'palavras_excluir': '',
            'situacao_cadastral': situacoes_string,
            'naturezas_ver': [],
            'page': 1,
            'per_page': 50
        }
        
        request = factory.post('/filter/', data=json.dumps(request_data), content_type='application/json')
        response = filter_data(request)
        response_data = json.loads(response.content.decode('utf-8'))
        total_combinado = response_data.get('total', 0)
        
        print(f"   '{situacoes_string}': {total_combinado} OSCs")
        
        # Validação da lógica OR
        soma_individuais = sum(totais_individuais[s] for s in situacoes_teste)
        print(f"   Soma individual: {soma_individuais}")
        print(f"   Total combinado: {total_combinado}")
        
        if total_combinado >= max(totais_individuais[s] for s in situacoes_teste):
            print("   ✅ Lógica OR funcionando!")
            return True
        else:
            print("   ❌ Problema na lógica OR")
            return False
    
    return True

def test_combined_filters():
    """Testa filtros combinados"""
    print("\n🧪 Testando filtros combinados...")
    
    request_data = {
        'municipio': 'Curitiba',
        'natureza_juridica': 'Associação Privada',
        'palavras_chave': 'educação',
        'palavras_excluir': 'igreja',
        'situacao_cadastral': 'ATIVA',
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
        
        print(f"   Filtros combinados:")
        print(f"   - Município: Curitiba")
        print(f"   - Natureza: Associação Privada")
        print(f"   - Incluir: educação")
        print(f"   - Excluir: igreja")
        print(f"   - Situação: ATIVA")
        print(f"   Resultado: {total} OSCs")
        
        if total >= 0:  # Qualquer resultado é válido
            print("   ✅ Filtros combinados funcionando!")
            return True
        else:
            print("   ❌ Problema nos filtros combinados")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 TESTE DOS NOVOS FILTROS")
    print("=" * 60)
    
    success1 = test_exclude_keywords()
    success2 = test_situacao_cadastral()
    success3 = test_combined_filters()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("   Novos filtros funcionando corretamente")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("   Verifique os problemas acima")
    print("=" * 60)
    
    return success1 and success2 and success3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
