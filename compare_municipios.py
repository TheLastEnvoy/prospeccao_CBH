#!/usr/bin/env python3
"""
Script para comparar municípios entre banco de dados e GeoJSON
"""

import json
import sqlite3
import os

def get_municipios_banco():
    """Obtém lista de municípios do banco"""
    conn = sqlite3.connect('data/oscs_parana_novo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT edmu_nm_municipio FROM oscs WHERE edmu_nm_municipio != "" ORDER BY edmu_nm_municipio')
    municipios = [row[0] for row in cursor.fetchall()]
    conn.close()
    return municipios

def get_municipios_geojson():
    """Obtém lista de municípios do GeoJSON"""
    geojson_path = os.path.join('static', 'geojson', 'PR_Municipios_2023_optimized.geojson')
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    municipios = [feature['properties']['NM_MUN'] for feature in data['features']]
    return sorted(municipios)

def compare_municipios():
    """Compara municípios entre banco e GeoJSON"""
    print("🔍 Comparando municípios entre banco de dados e GeoJSON...")
    
    municipios_banco = get_municipios_banco()
    municipios_geojson = get_municipios_geojson()
    
    print(f"\n📊 Estatísticas:")
    print(f"   Municípios no banco: {len(municipios_banco)}")
    print(f"   Municípios no GeoJSON: {len(municipios_geojson)}")
    
    # Municípios no banco mas não no GeoJSON
    banco_nao_geojson = set(municipios_banco) - set(municipios_geojson)
    
    # Municípios no GeoJSON mas não no banco
    geojson_nao_banco = set(municipios_geojson) - set(municipios_banco)
    
    print(f"\n❌ Municípios no BANCO mas NÃO no GeoJSON ({len(banco_nao_geojson)}):")
    for municipio in sorted(banco_nao_geojson):
        print(f"   - {municipio}")
    
    print(f"\n❌ Municípios no GeoJSON mas NÃO no BANCO ({len(geojson_nao_banco)}):")
    for municipio in sorted(geojson_nao_banco):
        print(f"   - {municipio}")
    
    # Buscar possíveis correspondências por similaridade
    print(f"\n🔍 Buscando possíveis correspondências...")
    
    for municipio_banco in banco_nao_geojson:
        # Buscar nomes similares no GeoJSON
        palavras_banco = municipio_banco.lower().split()
        candidatos = []
        
        for municipio_geo in geojson_nao_banco:
            palavras_geo = municipio_geo.lower().split()
            
            # Verificar se há palavras em comum
            palavras_comuns = set(palavras_banco) & set(palavras_geo)
            if palavras_comuns:
                candidatos.append((municipio_geo, len(palavras_comuns)))
        
        if candidatos:
            # Ordenar por número de palavras em comum
            candidatos.sort(key=lambda x: x[1], reverse=True)
            print(f"   '{municipio_banco}' pode corresponder a:")
            for candidato, score in candidatos[:3]:  # Top 3
                print(f"      - '{candidato}' (score: {score})")
    
    return banco_nao_geojson, geojson_nao_banco

if __name__ == "__main__":
    compare_municipios()
