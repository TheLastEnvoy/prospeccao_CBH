"""
Script para migrar dados do CSV para um novo banco SQLite3
"""

import pandas as pd
import sqlite3
import os
from pathlib import Path

CSV_PATH = 'data/dados_osc_PR_FINAL.csv'
NEW_DB_PATH = 'data/oscs_parana_novo.db'
TABLE_NAME = 'oscs'


def migrar_csv_para_novo_sqlite():
    """Migra dados do CSV para um novo banco SQLite3"""
    csv_path = Path(CSV_PATH)
    db_path = Path(NEW_DB_PATH)

    if not csv_path.exists():
        print(f"Arquivo CSV não encontrado: {csv_path}")
        return False

    print(f"Carregando dados do CSV: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"Dados carregados: {len(df)} registros")

    print(f"Criando novo banco SQLite: {db_path}")
    conn = sqlite3.connect(db_path)

    print(f"Criando tabela '{TABLE_NAME}' e inserindo dados...")
    df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)

    # Cria índices para consultas rápidas
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_id_osc ON oscs(id_osc)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nome ON oscs(nome)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_municipio ON oscs(edmu_nm_municipio)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_natureza ON oscs(natureza_juridica)")
    conn.commit()

    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    total_registros = cursor.fetchone()[0]
    print(f"Total de registros inseridos: {total_registros}")

    conn.close()
    print("Migração concluída com sucesso!")
    return True


if __name__ == "__main__":
    migrar_csv_para_novo_sqlite()
