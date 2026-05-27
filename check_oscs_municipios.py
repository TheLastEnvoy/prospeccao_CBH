import sqlite3

conn = sqlite3.connect('data/oscs_parana_novo.db')
cur = conn.cursor()

# Confirmar contagens antes
cur.execute("SELECT edmu_nm_municipio, COUNT(*) FROM oscs WHERE edmu_nm_municipio IN ('Diamante do Oeste', 'Diamante D\u2019Oeste', \"Diamante D'Oeste\") GROUP BY edmu_nm_municipio")
print("Antes:")
for row in cur.fetchall():
    print(f"  {repr(row[0])}: {row[1]}")

# Corrigir: unificar para 'Diamante do Oeste' (forma usada no CSV/CBH)
cur.execute("UPDATE oscs SET edmu_nm_municipio = 'Diamante do Oeste' WHERE edmu_nm_municipio = 'Diamante D\u2019Oeste'")
cur.execute("UPDATE oscs SET edmu_nm_municipio = 'Diamante do Oeste' WHERE edmu_nm_municipio = \"Diamante D'Oeste\"")
affected = cur.rowcount
conn.commit()

print(f"\nRegistros atualizados: {affected}")

# Confirmar depois
cur.execute("SELECT edmu_nm_municipio, COUNT(*) FROM oscs WHERE edmu_nm_municipio LIKE '%Diamante%' GROUP BY edmu_nm_municipio")
print("\nDepois:")
for row in cur.fetchall():
    print(f"  {repr(row[0])}: {row[1]}")

# Confirmar total municipios
cur.execute("SELECT COUNT(DISTINCT edmu_nm_municipio) FROM oscs WHERE edmu_nm_municipio != ''")
print(f"\nTotal municípios distintos em oscs: {cur.fetchone()[0]}")

conn.close()
