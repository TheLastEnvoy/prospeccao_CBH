"""
Script para verificar se o banco SQLite está funcionando corretamente
"""

import sqlite3
import pandas as pd
from pathlib import Path

def verificar_banco():
    """Verifica se o banco está funcionando"""
    
    db_path = Path('data/oscs_parana_novo.db')
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return False
    
    try:
        # Conecta ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== VERIFICAÇÃO DO BANCO SQLITE ===")
        
        # Verifica estrutura da tabela
        cursor.execute("PRAGMA table_info(oscs)")
        colunas = cursor.fetchall()
        
        print(f"\n📋 Estrutura da tabela 'oscs':")
        for coluna in colunas:
            print(f"  - {coluna[1]} ({coluna[2]})")
        
        # Verifica total de registros
        cursor.execute("SELECT COUNT(*) FROM oscs")
        total_registros = cursor.fetchone()[0]
        print(f"\n📊 Total de registros: {total_registros}")
        
        # Verifica municípios únicos
        cursor.execute("SELECT COUNT(DISTINCT edmu_nm_municipio) FROM oscs WHERE edmu_nm_municipio != ''")
        total_municipios = cursor.fetchone()[0]
        print(f"🏙️  Total de municípios: {total_municipios}")
        
        # Verifica naturezas jurídicas únicas
        cursor.execute("SELECT COUNT(DISTINCT natureza_juridica) FROM oscs WHERE natureza_juridica != ''")
        total_naturezas = cursor.fetchone()[0]
        print(f"⚖️  Total de naturezas jurídicas: {total_naturezas}")
        
        # Verifica alguns exemplos
        cursor.execute("SELECT * FROM oscs LIMIT 3")
        exemplos = cursor.fetchall()
        
        print(f"\n📝 Exemplos de registros:")
        for i, exemplo in enumerate(exemplos, 1):
            print(f"  {i}. ID: {exemplo[0]}, Nome: {exemplo[1][:50]}..., Município: {exemplo[8]}")
        
        # Testa query de filtro
        print(f"\n🔍 Testando query de filtro...")
        query = "SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio LIKE ?"
        cursor.execute(query, ['%Curitiba%'])
        resultado = cursor.fetchone()[0]
        print(f"  OSCs em Curitiba: {resultado}")
        
        # Testa paginação
        print(f"\n📄 Testando paginação...")
        query = "SELECT * FROM oscs LIMIT 5 OFFSET 0"
        df = pd.read_sql_query(query, conn)
        print(f"  Primeiros 5 registros carregados: {len(df)}")
        
        conn.close()
        
        print(f"\n✅ Banco de dados funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

if __name__ == "__main__":
    verificar_banco()
