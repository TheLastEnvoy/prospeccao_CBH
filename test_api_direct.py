#!/usr/bin/env python3
"""
Script para testar diretamente a API e identificar o problema JSON
"""

import requests
import json

def test_api_call():
    """Testa a API diretamente"""
    url = "http://127.0.0.1:8000/filter/"
    
    # Dados que estão causando erro
    data = {
        "municipio": "Palmeira",
        "natureza_juridica": "",
        "palavras_chave": "rural",
        "naturezas_ver": [],
        "page": 1,
        "per_page": 50
    }
    
    print("🧪 Testando API diretamente...")
    print(f"URL: {url}")
    print(f"Dados: {data}")
    
    try:
        # Fazer requisição POST
        response = requests.post(
            url,
            json=data,
            headers={
                'Content-Type': 'application/json',
            }
        )
        
        print(f"\n📊 Resposta:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content Length: {len(response.content)}")
        
        # Tentar decodificar como texto primeiro
        response_text = response.text
        print(f"\n📝 Resposta como texto (primeiros 1000 chars):")
        print(response_text[:1000])
        
        if len(response_text) > 1000:
            print(f"... (truncado, total: {len(response_text)} chars)")
        
        # Verificar se há caracteres problemáticos
        print(f"\n🔍 Análise da resposta:")
        print(f"Encoding: {response.encoding}")
        
        # Procurar por caracteres problemáticos na posição 815
        if len(response_text) > 815:
            print(f"Caractere na posição 815: '{response_text[814]}' (ord: {ord(response_text[814])})")
            print(f"Contexto (810-820): '{response_text[810:820]}'")
        
        # Tentar fazer parse do JSON
        try:
            json_data = response.json()
            print(f"\n✅ JSON válido!")
            print(f"Chaves: {list(json_data.keys())}")
            if 'total' in json_data:
                print(f"Total encontrado: {json_data['total']}")
            if 'data' in json_data:
                print(f"Registros retornados: {len(json_data['data'])}")
        except json.JSONDecodeError as e:
            print(f"\n❌ Erro no JSON: {e}")
            print(f"Posição do erro: {e.pos}")
            if e.pos < len(response_text):
                start = max(0, e.pos - 50)
                end = min(len(response_text), e.pos + 50)
                print(f"Contexto do erro: '{response_text[start:end]}'")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")

def test_without_keywords():
    """Testa sem palavras-chave para comparação"""
    url = "http://127.0.0.1:8000/filter/"
    
    data = {
        "municipio": "Palmeira",
        "natureza_juridica": "",
        "palavras_chave": "",  # Sem palavras-chave
        "naturezas_ver": [],
        "page": 1,
        "per_page": 50
    }
    
    print("\n🧪 Testando sem palavras-chave (para comparação)...")
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        print(f"Status Code: {response.status_code}")
        
        try:
            json_data = response.json()
            print(f"✅ JSON válido sem palavras-chave!")
            print(f"Total encontrado: {json_data.get('total', 'N/A')}")
        except json.JSONDecodeError as e:
            print(f"❌ Erro no JSON mesmo sem palavras-chave: {e}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")

def test_different_keywords():
    """Testa com diferentes palavras-chave"""
    url = "http://127.0.0.1:8000/filter/"
    
    test_cases = [
        "rural",
        "agua",
        "test",
        "associacao",
        "fundacao"
    ]
    
    print("\n🧪 Testando diferentes palavras-chave...")
    
    for keyword in test_cases:
        data = {
            "municipio": "Palmeira",
            "natureza_juridica": "",
            "palavras_chave": keyword,
            "naturezas_ver": [],
            "page": 1,
            "per_page": 50
        }
        
        try:
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
            
            try:
                json_data = response.json()
                total = json_data.get('total', 'N/A')
                print(f"  '{keyword}': {total} OSCs - ✅")
            except json.JSONDecodeError as e:
                print(f"  '{keyword}': Erro JSON - ❌ ({e})")
                
        except requests.exceptions.RequestException as e:
            print(f"  '{keyword}': Erro requisição - ❌ ({e})")

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 TESTE DIRETO DA API - DEBUG JSON")
    print("=" * 60)
    
    test_api_call()
    test_without_keywords()
    test_different_keywords()
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")
    print("=" * 60)

if __name__ == "__main__":
    main()
