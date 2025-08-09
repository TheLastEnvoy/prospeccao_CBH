#!/usr/bin/env python3
"""
Script para verificar nomes de municípios no GeoJSON
"""

import json
import os

def check_geojson_names():
    """Verifica nomes de municípios no GeoJSON"""
    geojson_path = os.path.join('static', 'geojson', 'PR_Municipios_2023_optimized.geojson')
    
    if not os.path.exists(geojson_path):
        print(f"❌ Arquivo GeoJSON não encontrado: {geojson_path}")
        return
    
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("🗺️ Verificando nomes no GeoJSON...")
        
        # Buscar municípios com "Coronel"
        coronel_features = [f for f in data['features'] if 'Coronel' in f['properties']['NM_MUN']]

        print(f"\n📍 Municípios com 'Coronel' no GeoJSON:")
        for feature in coronel_features:
            nome = feature['properties']['NM_MUN']
            print(f"   - '{nome}'")

        # Buscar municípios com "Domingos" ou "Domingo"
        domingos_features = [f for f in data['features'] if 'Domingos' in f['properties']['NM_MUN'] or 'Domingo' in f['properties']['NM_MUN']]

        print(f"\n📍 Municípios com 'Domingos/Domingo' no GeoJSON:")
        for feature in domingos_features:
            nome = feature['properties']['NM_MUN']
            print(f"   - '{nome}'")
        
        # Buscar alguns outros municípios importantes
        importantes = ['Curitiba', 'Londrina', 'Maringá', 'Foz do Iguaçu']
        print(f"\n📍 Municípios importantes no GeoJSON:")
        for municipio in importantes:
            found = [f for f in data['features'] if f['properties']['NM_MUN'] == municipio]
            if found:
                print(f"   ✅ '{municipio}' encontrado")
            else:
                # Buscar variações
                variations = [f for f in data['features'] if municipio.lower() in f['properties']['NM_MUN'].lower()]
                if variations:
                    print(f"   ⚠️ '{municipio}' não encontrado, mas há variações:")
                    for v in variations:
                        print(f"      - '{v['properties']['NM_MUN']}'")
                else:
                    print(f"   ❌ '{municipio}' não encontrado")
        
        print(f"\n📊 Total de municípios no GeoJSON: {len(data['features'])}")
        
        return data
        
    except Exception as e:
        print(f"❌ Erro ao ler GeoJSON: {e}")
        return None

if __name__ == "__main__":
    check_geojson_names()
