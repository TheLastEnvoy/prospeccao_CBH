"""
Coleta os IDs de todas as OSCs do Paraná via API do MapaOSC - IPEA
Endpoint: GET /api/geo/oscs/estado/{id_estado}

Uso:
    python coletar_ids_pr.py
"""

import requests
import pandas as pd

API_BASE = 'https://mapaosc.ipea.gov.br/api/api'


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json',
    'Referer': 'https://mapaosc.ipea.gov.br/',
}


def obter_id_estado_pr():
    """Busca o id_regiao do Paraná na API."""
    resp = requests.get(f'{API_BASE}/geo/estados', headers=HEADERS, timeout=30)
    resp.raise_for_status()
    estados = resp.json()

    # A resposta é um dict indexado por chave numérica
    items = estados.values() if isinstance(estados, dict) else estados
    for estado in items:
        sigla = estado.get('tx_sigla_regiao', '') or estado.get('sigla', '')
        nome = estado.get('tx_nome_regiao', '') or estado.get('nome', '')
        if sigla.upper() == 'PR' or 'PARAN' in nome.upper():
            qtd = estado.get('nr_quantidade_osc_regiao', '?')
            print(f"✅ Estado encontrado: {nome} ({sigla}) — {qtd} OSCs")
            return estado.get('id_regiao') or estado.get('id_estado')

    print("❌ Paraná não encontrado automaticamente. Estados disponíveis:")
    for e in items:
        print(f"   {e}")
    return None


def coletar_ids(id_estado: int):
    """Retorna lista de id_osc para o estado informado."""
    url = f'{API_BASE}/geo/oscs/estado/{id_estado}'
    print(f"🌐 Chamando: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=120)
    resp.raise_for_status()
    oscs = resp.json()
    return oscs


def main():
    print("🔍 Buscando ID do estado Paraná na API...")
    id_estado = obter_id_estado_pr()

    if id_estado is None:
        # Tenta com o código IBGE direto (41 = Paraná)
        print("⚠️  Tentando com código IBGE 41 diretamente...")
        id_estado = 41

    print(f"📍 Usando id_estado = {id_estado}")

    print("📥 Baixando lista de OSCs...")
    oscs = coletar_ids(id_estado)

    if not oscs:
        print("❌ Nenhuma OSC retornada pela API.")
        return

    print(f"✅ {len(oscs)} OSCs encontradas.")

    # Salva CSV compatível com o extrator (coluna id_osc)
    df = pd.DataFrame(oscs)
    print(f"📋 Colunas retornadas: {list(df.columns)}")

    # Garante que a coluna id_osc existe
    if 'id_osc' not in df.columns:
        print("❌ Coluna id_osc não encontrada na resposta da API.")
        print(df.head())
        return

    saida = 'data/osc_PR_novo.CSV'
    df[['id_osc']].drop_duplicates().to_csv(saida, sep=';', index=False)
    print(f"💾 IDs salvos em: {saida}")
    print(f"📊 Total de IDs únicos: {df['id_osc'].nunique()}")


if __name__ == '__main__':
    main()
