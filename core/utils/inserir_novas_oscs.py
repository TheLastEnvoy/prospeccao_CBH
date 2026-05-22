"""
Enriquece as novas OSCs coletadas com dados de município (via API)
e as insere no banco SQLite sem duplicatas e sem quebrar o formato existente.

Uso:
    python core/utils/inserir_novas_oscs.py
"""

import sqlite3
import pandas as pd
import requests
import time

API_BASE = 'https://mapaosc.ipea.gov.br/api/api'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json',
    'Referer': 'https://mapaosc.ipea.gov.br/',
}

NOVAS_OSCS_CSV = 'data/dados_osc_PR_fast_corrigido.csv'
DB_PATH = 'data/oscs_parana_novo.db'
ID_ESTADO_PR = 41


def buscar_municipios_pr():
    """Retorna dict {id_municipio: {cd_municipio, nm_municipio}} para o PR."""
    resp = requests.get(f'{API_BASE}/geo/municipios/estado/{ID_ESTADO_PR}', headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    municipios = {}
    items = data.values() if isinstance(data, dict) else data
    for m in items:
        id_mun = m.get('id_regiao')
        municipios[id_mun] = {
            'edmu_cd_municipio': m.get('id_regiao'),
            'edmu_nm_municipio': m.get('tx_nome_regiao'),
        }
    return municipios


def construir_mapa_osc_municipio(municipios: dict) -> dict:
    """Para cada município, busca as OSCs que pertencem a ele.
    Retorna dict {id_osc: {edmu_cd_municipio, edmu_nm_municipio}}.
    """
    mapa = {}
    total = len(municipios)
    for i, (id_mun, info_mun) in enumerate(municipios.items(), 1):
        if i % 50 == 0:
            print(f'  Municípios processados: {i}/{total}...')
        try:
            resp = requests.get(
                f'{API_BASE}/geo/oscs/municipio/{id_mun}',
                headers=HEADERS,
                timeout=20,
            )
            if resp.status_code != 200:
                continue
            oscs = resp.json()
            items = oscs.values() if isinstance(oscs, dict) else oscs
            for osc in items:
                id_osc = osc.get('id_osc')
                if id_osc:
                    mapa[int(id_osc)] = info_mun
        except Exception as e:
            print(f'  Aviso: erro no município {id_mun}: {e}')
        time.sleep(0.05)  # pequena pausa para não sobrecarregar o servidor
    return mapa


def main():
    # 1. Carrega as novas OSCs
    print('📂 Carregando novas OSCs...')
    df = pd.read_csv(NOVAS_OSCS_CSV)
    df['id_osc'] = pd.to_numeric(df['id_osc'], errors='coerce').astype('Int64')
    df = df.dropna(subset=['id_osc'])
    print(f'   {len(df)} registros carregados.')

    # 2. Verifica quais já estão no banco (evita duplicatas)
    conn = sqlite3.connect(DB_PATH)
    ids_no_banco = set(
        pd.read_sql('SELECT id_osc FROM oscs', conn)['id_osc'].astype(int).tolist()
    )
    df_novos = df[~df['id_osc'].astype(int).isin(ids_no_banco)].copy()
    print(f'   Já no banco: {len(ids_no_banco)} | Realmente novos: {len(df_novos)}')

    if df_novos.empty:
        print('✅ Nenhuma OSC nova para inserir.')
        conn.close()
        return

    # 3. Busca mapeamento município via API
    print('\n🗺️  Buscando municípios do PR via API...')
    municipios = buscar_municipios_pr()
    print(f'   {len(municipios)} municípios encontrados.')

    print('🔗 Construindo mapeamento id_osc → município...')
    mapa_osc_mun = construir_mapa_osc_municipio(municipios)
    print(f'   Mapeamento pronto: {len(mapa_osc_mun)} OSCs mapeadas.')

    # 4. Enriquece o DataFrame com dados de município
    df_novos['edmu_cd_municipio'] = df_novos['id_osc'].apply(
        lambda x: mapa_osc_mun.get(int(x), {}).get('edmu_cd_municipio')
    )
    df_novos['edmu_nm_municipio'] = df_novos['id_osc'].apply(
        lambda x: mapa_osc_mun.get(int(x), {}).get('edmu_nm_municipio')
    )

    sem_mun = df_novos['edmu_nm_municipio'].isna().sum()
    print(f'\n📊 Com município: {len(df_novos) - sem_mun} | Sem município: {sem_mun}')

    # 5. Garante ordem de colunas igual à tabela do banco
    colunas_banco = [
        'id_osc', 'nome', 'email', 'endereco', 'telefone',
        'natureza_juridica', 'situacao_cadastral',
        'edmu_cd_municipio', 'edmu_nm_municipio',
    ]
    df_inserir = df_novos[colunas_banco]

    # 6. Insere no banco (sem substituir dados existentes)
    print(f'\n💾 Inserindo {len(df_inserir)} registros no banco...')
    df_inserir.to_sql('oscs', conn, if_exists='append', index=False)
    conn.commit()

    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM oscs')
    total = cursor.fetchone()[0]
    conn.close()

    print(f'✅ Inserção concluída! Total no banco agora: {total} OSCs.')


if __name__ == '__main__':
    main()
