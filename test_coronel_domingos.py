#!/usr/bin/env python3
"""
Script para testar especificamente o caso do Coronel Domingos Soares
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_osc.settings')
django.setup()

from osc_dashboard.views import get_oscs_por_municipio

def test_coronel_domingos():
    """Testa especificamente o caso do Coronel Domingos Soares"""
    print("🎯 Testando caso específico: Coronel Domingos Soares")
    
    # Obter dados do banco
    dados_banco = get_oscs_por_municipio()
    
    # Buscar municípios com "Coronel"
    coronel_municipios = [item for item in dados_banco if 'Coronel' in item['municipio']]
    
    print(f"\n📍 Municípios com 'Coronel' no banco de dados:")
    for municipio in coronel_municipios:
        print(f"   - '{municipio['municipio']}': {municipio['total_oscs']} OSCs")
    
    # Verificar se o mapeamento funcionará
    nomes_geojson_teste = [
        'CORONEL DOMINGO SOARES',
        'Coronel Domingo Soares',
        'coronel domingo soares'
    ]
    
    print(f"\n🔍 Testando correspondências para variações do GeoJSON:")
    
    def normalizar_texto(texto):
        import unicodedata
        if not texto:
            return ''
        
        texto_normalizado = unicodedata.normalize('NFD', texto.lower())
        texto_sem_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
        
        import re
        texto_limpo = re.sub(r'[^a-z0-9\s]', '', texto_sem_acentos)
        texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
        
        return texto_limpo
    
    def calcular_similaridade(texto1, texto2):
        norm1 = normalizar_texto(texto1)
        norm2 = normalizar_texto(texto2)
        
        if norm1 == norm2:
            return 1.0
        
        if norm1 in norm2 or norm2 in norm1:
            return 0.8
        
        palavras1 = [p for p in norm1.split() if len(p) > 2]
        palavras2 = [p for p in norm2.split() if len(p) > 2]
        
        if not palavras1 or not palavras2:
            return 0
        
        palavras_comuns = set(palavras1) & set(palavras2)
        return len(palavras_comuns) / max(len(palavras1), len(palavras2))
    
    for nome_geo in nomes_geojson_teste:
        print(f"\n   Testando: '{nome_geo}'")
        
        # Buscar correspondência exata
        correspondencia_exata = None
        for municipio in dados_banco:
            if nome_geo.lower() == municipio['municipio'].lower():
                correspondencia_exata = municipio
                break
        
        if correspondencia_exata:
            print(f"      ✅ Correspondência exata: '{correspondencia_exata['municipio']}' ({correspondencia_exata['total_oscs']} OSCs)")
            continue
        
        # Buscar por similaridade
        melhor_match = None
        melhor_score = 0
        
        for municipio in dados_banco:
            score = calcular_similaridade(nome_geo, municipio['municipio'])
            if score > melhor_score:
                melhor_score = score
                melhor_match = municipio
        
        if melhor_match and melhor_score >= 0.6:
            print(f"      ✅ Correspondência por similaridade: '{melhor_match['municipio']}' ({melhor_match['total_oscs']} OSCs, score: {melhor_score:.2f})")
        else:
            print(f"      ❌ Nenhuma correspondência encontrada (melhor score: {melhor_score:.2f})")
    
    # Testar normalização específica
    print(f"\n🔧 Testando normalização de texto:")
    
    textos_teste = [
        'CORONEL DOMINGO SOARES',
        'Coronel Domingos Soares',
        'coronel domingo soares',
        'coronel domingos soares'
    ]
    
    for texto in textos_teste:
        normalizado = normalizar_texto(texto)
        print(f"   '{texto}' -> '{normalizado}'")
    
    # Verificar se as normalizações são iguais
    norm1 = normalizar_texto('CORONEL DOMINGO SOARES')
    norm2 = normalizar_texto('Coronel Domingos Soares')
    
    print(f"\n📊 Comparação de normalização:")
    print(f"   GeoJSON: '{norm1}'")
    print(f"   Banco:   '{norm2}'")
    print(f"   Iguais:  {norm1 == norm2}")
    
    if norm1 != norm2:
        # Calcular similaridade
        score = calcular_similaridade('CORONEL DOMINGO SOARES', 'Coronel Domingos Soares')
        print(f"   Score de similaridade: {score:.2f}")
        
        # Verificar palavras em comum
        palavras1 = norm1.split()
        palavras2 = norm2.split()
        palavras_comuns = set(palavras1) & set(palavras2)
        
        print(f"   Palavras GeoJSON: {palavras1}")
        print(f"   Palavras Banco:   {palavras2}")
        print(f"   Palavras comuns:  {list(palavras_comuns)}")
        print(f"   Proporção:        {len(palavras_comuns)}/{max(len(palavras1), len(palavras2))} = {len(palavras_comuns)/max(len(palavras1), len(palavras2)):.2f}")

if __name__ == "__main__":
    test_coronel_domingos()
