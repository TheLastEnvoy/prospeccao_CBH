"""
Gera um GeoJSON com os polígonos dos Comitês de Bacia Hidrográfica (CBH) do Paraná,
obtidos pela união dos polígonos dos municípios membros de cada CBH.

Requisitos: geopandas, shapely (já instalados)
Saída: static/geojson/PR_CBH_polygons.geojson
"""

import os
import json
import sqlite3
import unicodedata
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_MUNICIPIOS = os.path.join(BASE_DIR, 'static', 'geojson', 'PR_Municipios_2023_optimized.geojson')
DB_PATH = os.path.join(BASE_DIR, 'data', 'oscs_parana_novo.db')
OUTPUT_PATH = os.path.join(BASE_DIR, 'static', 'geojson', 'PR_CBH_polygons.geojson')


def normalize_name(s: str) -> str:
    """Remove acentos, converte para minúsculas e remove espaços extras para comparação."""
    s = unicodedata.normalize('NFKD', s.strip().lower())
    s = s.encode('ascii', 'ignore').decode()
    # Normaliza espaços múltiplos e hífens
    s = ' '.join(s.split())
    return s


# Mapeamento manual para nomes que diferem entre o GeoJSON (IBGE) e a tabela cbh_municipio
# Chave: normalize_name(municipio da tabela cbh_municipio) → Valor: NM_MUN exato do GeoJSON
CORRECOES_NOMES = {
    # cbh_municipio tem 'Munhoz de Mello'; GeoJSON tem 'Munhoz de Melo'
    'munhoz de mello': 'Munhoz de Melo',
    # cbh_municipio tem 'Santa Cruz do Monte Castelo'; GeoJSON tem 'SANTA CRUZ DE MONTE CASTELO'
    'santa cruz do monte castelo': 'SANTA CRUZ DE MONTE CASTELO',
    # cbh_municipio tem 'São Jorge do Oeste'; GeoJSON tem "São Jorge d'Oeste"
    'sao jorge do oeste': "São Jorge d'Oeste",
    # cbh_municipio tem 'Capitão Leonidas Marques'; GeoJSON tem 'Capitão Leônidas Marques'
    'capitao leonidas marques': 'Capitão Leônidas Marques',
    # cbh_municipio tem 'Santa Izabel do Ivaí'; GeoJSON tem 'Santa Isabel do Ivaí'
    'santa izabel do ivai': 'Santa Isabel do Ivaí',
    # cbh_municipio tem 'Santa Terezinha do Itaipu'; GeoJSON tem 'Santa Terezinha de Itaipu'
    'santa terezinha do itaipu': 'Santa Terezinha de Itaipu',
    # cbh_municipio tem 'São Antonio do Caiuá'; GeoJSON tem 'Santo Antônio do Caiuá'
    'sao antonio do caiua': 'Santo Antônio do Caiuá',
    # cbh_municipio tem 'Guairaçá'; GeoJSON tem 'Guairaçá' (pode variar encoding)
    'guairaca': 'Guairaçá',
    # cbh_municipio tem 'Nova Cantú'; GeoJSON tem 'Nova Cantú'
    'nova cantu': 'Nova Cantú',
    # cbh_municipio tem 'Coronel Domingos Soares'; GeoJSON tem 'CORONEL DOMINGO SOARES' (sem 's' final)
    'coronel domingos soares': 'CORONEL DOMINGO SOARES',
}


def main():
    # ── 1. Carregar GeoJSON dos municípios ─────────────────────────────────────
    print(f"Carregando GeoJSON: {GEOJSON_MUNICIPIOS}")
    gdf = gpd.read_file(GEOJSON_MUNICIPIOS)
    print(f"  {len(gdf)} municípios carregados.")

    # Índice normalizado → NM_MUN original para busca eficiente
    gdf['_nome_norm'] = gdf['NM_MUN'].apply(normalize_name)
    norm_to_nm_mun = dict(zip(gdf['_nome_norm'], gdf['NM_MUN']))

    # ── 2. Carregar dados de CBH → municípios do banco ─────────────────────────
    print(f"\nCarregando dados CBH do banco: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cbh_municipios = pd.read_sql_query(
        """
        SELECT c.cbh_id, c.cbh_nome, cm.municipio
        FROM cbh c
        JOIN cbh_municipio cm ON c.cbh_id = cm.cbh_id
        ORDER BY c.cbh_id, cm.rowid
        """,
        conn,
    )
    conn.close()
    print(f"  {len(cbh_municipios)} entradas CBH-município carregadas.")
    print(f"  {cbh_municipios['cbh_id'].nunique()} CBHs distintos.")

    # ── 3. Resolver nomes dos municípios ───────────────────────────────────────
    # Para cada município da tabela cbh_municipio, encontrar o NM_MUN no GeoJSON
    nao_encontrados = []
    nm_mun_col = []

    for _, row in cbh_municipios.iterrows():
        norm = normalize_name(row['municipio'])

        # Tentativa 1: correspondência exata normalizada
        if norm in norm_to_nm_mun:
            nm_mun_col.append(norm_to_nm_mun[norm])
            continue

        # Tentativa 2: correção manual
        if norm in CORRECOES_NOMES:
            nome_corrigido = CORRECOES_NOMES[norm]
            nm_mun_col.append(nome_corrigido)
            continue

        # Não encontrado
        nao_encontrados.append(row['municipio'])
        nm_mun_col.append(None)

    cbh_municipios['NM_MUN'] = nm_mun_col

    if nao_encontrados:
        print(f"\n⚠  Municípios da tabela CBH NÃO encontrados no GeoJSON ({len(nao_encontrados)}):")
        for nome in sorted(set(nao_encontrados)):
            print(f"    - {nome!r}")
    else:
        print("\n✓ Todos os municípios foram encontrados no GeoJSON.")

    # Remover linhas sem correspondência
    cbh_municipios = cbh_municipios.dropna(subset=['NM_MUN'])

    # ── 4. Merge com as geometrias ─────────────────────────────────────────────
    merged = cbh_municipios.merge(
        gdf[['NM_MUN', 'geometry']],
        on='NM_MUN',
        how='left',
    )

    # Verificar municípios sem geometria após merge
    sem_geom = merged[merged['geometry'].isna()]
    if not sem_geom.empty:
        print(f"\n⚠  Municípios sem geometria após merge ({len(sem_geom)}):")
        for nome in sem_geom['municipio'].unique():
            print(f"    - {nome!r}")
        merged = merged.dropna(subset=['geometry'])

    # ── 5. Dissolver (union) geometrias por CBH ────────────────────────────────
    print("\nCalculando união de polígonos por CBH...")
    gdf_merged = gpd.GeoDataFrame(merged, geometry='geometry', crs=gdf.crs)

    # Para cada CBH: nome do CBH + lista de municípios + geometria unida
    cbh_resultados = []
    for cbh_id, grupo in gdf_merged.groupby('cbh_id'):
        cbh_nome = grupo['cbh_nome'].iloc[0]
        municipios_lista = sorted(grupo['municipio'].tolist())
        geom_unida = unary_union(grupo.geometry.values)

        cbh_resultados.append({
            'cbh_id': cbh_id,
            'cbh_nome': cbh_nome,
            'municipios_count': len(municipios_lista),
            'municipios': ', '.join(municipios_lista),
            'geometry': geom_unida,
        })

        print(f"  {cbh_nome}: {len(municipios_lista)} municípios")

    gdf_cbh = gpd.GeoDataFrame(cbh_resultados, crs=gdf.crs)

    # ── 6. Salvar GeoJSON de saída ─────────────────────────────────────────────
    gdf_cbh.to_file(OUTPUT_PATH, driver='GeoJSON', encoding='utf-8')
    print(f"\n✓ GeoJSON salvo em: {OUTPUT_PATH}")
    print(f"  {len(gdf_cbh)} CBHs exportados.")

    # ── 7. Resumo de cobertura ─────────────────────────────────────────────────
    total_municipios_cobertos = gdf_cbh['municipios_count'].sum()
    print(f"\nResumo:")
    print(f"  Total de municípios cobertos pelos CBHs: {total_municipios_cobertos}")
    print(f"  Total de municípios no GeoJSON:          {len(gdf)}")
    print(f"\n  Distribuição por CBH:")
    for _, row in gdf_cbh.sort_values('municipios_count', ascending=False).iterrows():
        print(f"    {row['cbh_nome']}: {row['municipios_count']} municípios")


if __name__ == '__main__':
    main()
