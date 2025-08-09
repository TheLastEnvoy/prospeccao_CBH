#!/usr/bin/env python3
"""
Script para testar a estratégia de aproximação do mapa
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

from osc_dashboard.views import get_oscs_por_municipio

def test_aproximacao_municipios():
    """Testa a estratégia de aproximação para municípios"""
    print("🗺️ Testando estratégia de aproximação do mapa...")
    
    # Obter dados do banco
    dados_banco = get_oscs_por_municipio()
    municipios_banco = {item['municipio']: item['total_oscs'] for item in dados_banco}
    
    # Obter dados do GeoJSON
    geojson_path = os.path.join('static', 'geojson', 'PR_Municipios_2023_optimized.geojson')
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    municipios_geojson = [feature['properties']['NM_MUN'] for feature in geojson_data['features']]
    
    print(f"\n📊 Estatísticas:")
    print(f"   Municípios no banco: {len(municipios_banco)}")
    print(f"   Municípios no GeoJSON: {len(municipios_geojson)}")
    
    # Função de normalização (similar ao JavaScript)
    def normalizar_texto(texto):
        import unicodedata
        if not texto:
            return ''
        
        # Remove acentos e normaliza
        texto_normalizado = unicodedata.normalize('NFD', texto.lower())
        texto_sem_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
        
        # Remove caracteres especiais e normaliza espaços
        import re
        texto_limpo = re.sub(r'[^a-z0-9\s]', '', texto_sem_acentos)
        texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
        
        return texto_limpo
    
    # Função de similaridade
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
    
    # Testar correspondências
    print(f"\n🔍 Testando correspondências...")
    
    correspondencias_encontradas = 0
    municipios_sem_correspondencia = []
    
    for municipio_geo in municipios_geojson:
        melhor_match = None
        melhor_score = 0
        
        # Busca exata
        if municipio_geo in municipios_banco:
            correspondencias_encontradas += 1
            continue
        
        # Busca por similaridade
        for municipio_banco in municipios_banco.keys():
            score = calcular_similaridade(municipio_geo, municipio_banco)
            
            if score > melhor_score and score >= 0.7:
                melhor_score = score
                melhor_match = municipio_banco
        
        if melhor_match:
            correspondencias_encontradas += 1
            oscs_count = municipios_banco[melhor_match]
            print(f"   ✅ '{municipio_geo}' -> '{melhor_match}' ({oscs_count} OSCs, score: {melhor_score:.2f})")
        else:
            municipios_sem_correspondencia.append(municipio_geo)
    
    print(f"\n📈 Resultados:")
    print(f"   Correspondências encontradas: {correspondencias_encontradas}/{len(municipios_geojson)}")
    print(f"   Taxa de sucesso: {correspondencias_encontradas/len(municipios_geojson)*100:.1f}%")
    
    if municipios_sem_correspondencia:
        print(f"\n❌ Municípios sem correspondência ({len(municipios_sem_correspondencia)}):")
        for municipio in municipios_sem_correspondencia[:10]:  # Mostrar apenas os primeiros 10
            # Buscar os mais similares
            candidatos = []
            for municipio_banco in municipios_banco.keys():
                score = calcular_similaridade(municipio, municipio_banco)
                if score > 0.3:
                    candidatos.append((municipio_banco, score))
            
            candidatos.sort(key=lambda x: x[1], reverse=True)
            print(f"   - '{municipio}'")
            if candidatos:
                print(f"     Similares: {candidatos[:3]}")
    
    # Testar casos específicos
    print(f"\n🎯 Testando casos específicos:")
    
    casos_teste = [
        'Coronel Domingos Soares',
        'LONDRINA',
        'Foz do Iguaçu',
        'São José dos Pinhais'
    ]
    
    for caso in casos_teste:
        if caso in municipios_banco:
            oscs_count = municipios_banco[caso]
            print(f"   ✅ '{caso}': {oscs_count} OSCs (encontrado no banco)")
        else:
            # Buscar similar
            melhor_match = None
            melhor_score = 0
            
            for municipio_banco in municipios_banco.keys():
                score = calcular_similaridade(caso, municipio_banco)
                if score > melhor_score:
                    melhor_score = score
                    melhor_match = municipio_banco
            
            if melhor_match and melhor_score >= 0.7:
                oscs_count = municipios_banco[melhor_match]
                print(f"   ✅ '{caso}' -> '{melhor_match}': {oscs_count} OSCs (score: {melhor_score:.2f})")
            else:
                print(f"   ❌ '{caso}': Não encontrado")
    
    return correspondencias_encontradas / len(municipios_geojson)

if __name__ == "__main__":
    taxa_sucesso = test_aproximacao_municipios()
    
    print(f"\n" + "=" * 60)
    if taxa_sucesso >= 0.95:
        print("✅ ESTRATÉGIA DE APROXIMAÇÃO EXCELENTE!")
        print(f"   Taxa de sucesso: {taxa_sucesso*100:.1f}%")
    elif taxa_sucesso >= 0.90:
        print("✅ ESTRATÉGIA DE APROXIMAÇÃO BOA!")
        print(f"   Taxa de sucesso: {taxa_sucesso*100:.1f}%")
    else:
        print("⚠️ ESTRATÉGIA DE APROXIMAÇÃO PRECISA MELHORAR")
        print(f"   Taxa de sucesso: {taxa_sucesso*100:.1f}%")
    print("=" * 60)
