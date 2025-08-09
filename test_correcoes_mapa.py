#!/usr/bin/env python3
"""
Script para testar as correções específicas do mapa
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

def test_correcoes_especificas():
    """Testa as correções específicas para os nomes incorretos do IPEA"""
    print("🔧 Testando correções específicas para nomes incorretos do IPEA...")
    
    # Obter dados do banco (IPEA)
    dados_banco = get_oscs_por_municipio()
    municipios_banco = {item['municipio']: item['total_oscs'] for item in dados_banco}
    
    # Obter dados do GeoJSON
    geojson_path = os.path.join('static', 'geojson', 'PR_Municipios_2023_optimized.geojson')
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    municipios_geojson = [feature['properties']['NM_MUN'] for feature in geojson_data['features']]
    
    print(f"\n📊 Estatísticas:")
    print(f"   Municípios no banco (IPEA): {len(municipios_banco)}")
    print(f"   Municípios no GeoJSON: {len(municipios_geojson)}")
    
    # Casos específicos para testar
    casos_teste = [
        {
            'nome_ipea': 'Coronel Domingos Soares',
            'nome_geojson_correto': 'CORONEL DOMINGO SOARES',
            'oscs_esperadas': 36
        },
        {
            'nome_ipea': "Diamante D'Oeste",
            'nome_geojson_correto': 'DIAMANTE DO OESTE',
            'oscs_esperadas': None  # Vamos descobrir
        }
    ]
    
    print(f"\n🎯 Testando casos específicos:")
    
    for caso in casos_teste:
        nome_ipea = caso['nome_ipea']
        nome_geojson = caso['nome_geojson_correto']
        
        print(f"\n   Caso: {nome_ipea} (IPEA) -> {nome_geojson} (GeoJSON)")
        
        # Verificar se existe no banco IPEA
        if nome_ipea in municipios_banco:
            oscs_count = municipios_banco[nome_ipea]
            print(f"      ✅ Encontrado no banco IPEA: {oscs_count} OSCs")
            caso['oscs_esperadas'] = oscs_count
        else:
            print(f"      ❌ NÃO encontrado no banco IPEA")
            continue
        
        # Verificar se existe no GeoJSON
        if nome_geojson in municipios_geojson:
            print(f"      ✅ Encontrado no GeoJSON: {nome_geojson}")
        else:
            # Buscar variações
            variações_encontradas = [m for m in municipios_geojson if nome_geojson.lower() in m.lower() or m.lower() in nome_geojson.lower()]
            if variações_encontradas:
                print(f"      ⚠️ Não encontrado exato no GeoJSON, mas há variações: {variações_encontradas}")
            else:
                print(f"      ❌ NÃO encontrado no GeoJSON")
    
    # Simular a lógica de mapeamento do JavaScript
    print(f"\n🔄 Simulando lógica de mapeamento JavaScript:")
    
    # Mapeamentos que serão aplicados
    mapeamentos = {
        'Coronel Domingos Soares': 'CORONEL DOMINGO SOARES',
        "Diamante D'Oeste": 'DIAMANTE DO OESTE'
    }
    
    for nome_ipea, nome_geojson_correto in mapeamentos.items():
        print(f"\n   Mapeamento: '{nome_ipea}' -> '{nome_geojson_correto}'")
        
        # Verificar se o nome IPEA existe
        if nome_ipea in municipios_banco:
            oscs_count = municipios_banco[nome_ipea]
            print(f"      📊 OSCs no banco IPEA: {oscs_count}")
            
            # Verificar se o nome GeoJSON correto existe
            if nome_geojson_correto in municipios_geojson:
                print(f"      ✅ Nome correto existe no GeoJSON")
                print(f"      🎯 Resultado: Mapa mostrará {oscs_count} OSCs para '{nome_geojson_correto}'")
            else:
                print(f"      ❌ Nome correto NÃO existe no GeoJSON")
        else:
            print(f"      ❌ Nome IPEA não encontrado no banco")
    
    # Verificar correspondência total após correções
    print(f"\n📈 Verificando correspondência total após correções:")
    
    correspondencias = 0
    municipios_sem_correspondencia = []
    
    for municipio_geo in municipios_geojson:
        # Busca direta
        if municipio_geo in municipios_banco:
            correspondencias += 1
            continue
        
        # Busca com mapeamentos inversos
        encontrado = False
        for nome_ipea, nome_geo_correto in mapeamentos.items():
            if municipio_geo == nome_geo_correto and nome_ipea in municipios_banco:
                correspondencias += 1
                encontrado = True
                break
        
        if not encontrado:
            municipios_sem_correspondencia.append(municipio_geo)
    
    print(f"   Correspondências encontradas: {correspondencias}/{len(municipios_geojson)}")
    print(f"   Taxa de sucesso: {correspondencias/len(municipios_geojson)*100:.1f}%")
    
    if municipios_sem_correspondencia:
        print(f"\n❌ Municípios ainda sem correspondência ({len(municipios_sem_correspondencia)}):")
        for municipio in municipios_sem_correspondencia[:5]:  # Mostrar apenas os primeiros 5
            print(f"      - {municipio}")
    
    return correspondencias / len(municipios_geojson)

if __name__ == "__main__":
    taxa_sucesso = test_correcoes_especificas()
    
    print(f"\n" + "=" * 60)
    if taxa_sucesso >= 0.99:
        print("✅ CORREÇÕES APLICADAS COM SUCESSO!")
        print(f"   Taxa de correspondência: {taxa_sucesso*100:.1f}%")
        print("   O mapa deve funcionar corretamente agora!")
    else:
        print("⚠️ AINDA HÁ PROBLEMAS DE CORRESPONDÊNCIA")
        print(f"   Taxa de correspondência: {taxa_sucesso*100:.1f}%")
    print("=" * 60)
