"""
Script para testar as views e identificar problemas
"""

import os
import sys
import django
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_osc.settings')
django.setup()

from osc_dashboard.views import get_filter_options, get_db_connection
import sqlite3

def testar_conexao_banco():
    """Testa a conexão com o banco"""
    print("=== TESTANDO CONEXÃO COM BANCO ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Testa query simples
        cursor.execute("SELECT COUNT(*) FROM oscs")
        total = cursor.fetchone()[0]
        print(f"✅ Conexão OK - Total de registros: {total}")
        
        # Testa query de filtro
        cursor.execute("SELECT DISTINCT natureza_juridica FROM oscs WHERE natureza_juridica != '' LIMIT 5")
        naturezas = cursor.fetchall()
        print(f"✅ Naturezas jurídicas encontradas: {[n[0] for n in naturezas]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def testar_filter_options():
    """Testa a função get_filter_options"""
    print("\n=== TESTANDO GET_FILTER_OPTIONS ===")
    
    try:
        options = get_filter_options()
        
        print(f"✅ Municípios: {len(options['municipios'])} encontrados")
        print(f"✅ Naturezas jurídicas: {len(options['naturezas_juridicas'])} encontradas")
        print(f"✅ Total de registros: {options['total_registros']}")
        
        # Mostra algumas opções
        if options['municipios']:
            print(f"   Primeiros municípios: {options['municipios'][:3]}")
        
        if options['naturezas_juridicas']:
            print(f"   Naturezas: {options['naturezas_juridicas']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro em get_filter_options: {e}")
        return False

def testar_query_filtro():
    """Testa uma query de filtro similar à usada na view"""
    print("\n=== TESTANDO QUERY DE FILTRO ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Simula a query da view filter_data
        query = "SELECT COUNT(*) FROM oscs WHERE 1=1"
        params = []
        
        # Testa com alguns filtros
        query += " AND edmu_nm_municipio LIKE ?"
        params.append('%Curitiba%')
        
        cursor.execute(query, params)
        total = cursor.fetchone()[0]
        print(f"✅ Query de filtro OK - OSCs em Curitiba: {total}")
        
        # Testa com naturezas jurídicas
        query2 = "SELECT COUNT(*) FROM oscs WHERE 1=1"
        params2 = []
        
        naturezas_ver = ['Associação Privada', 'Organização Religiosa']
        placeholders = ','.join(['?' for _ in naturezas_ver])
        query2 += f" AND natureza_juridica IN ({placeholders})"
        params2.extend(naturezas_ver)
        
        cursor.execute(query2, params2)
        total2 = cursor.fetchone()[0]
        print(f"✅ Query com naturezas jurídicas OK - Total: {total2}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na query de filtro: {e}")
        return False

def verificar_arquivo_banco():
    """Verifica se o arquivo do banco existe"""
    print("\n=== VERIFICANDO ARQUIVO DO BANCO ===")
    
    db_path = Path('data/oscs_parana_novo.db')
    
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"✅ Arquivo do banco encontrado: {db_path}")
        print(f"   Tamanho: {size:,} bytes")
        return True
    else:
        print(f"❌ Arquivo do banco não encontrado: {db_path}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DO PROBLEMA DE LOADING")
    print("=" * 50)
    
    # Verifica arquivo do banco
    banco_ok = verificar_arquivo_banco()
    
    if banco_ok:
        # Testa conexão
        conexao_ok = testar_conexao_banco()
        
        if conexao_ok:
            # Testa filter options
            filter_ok = testar_filter_options()
            
            if filter_ok:
                # Testa query de filtro
                query_ok = testar_query_filtro()
                
                if query_ok:
                    print("\n✅ TODOS OS TESTES PASSARAM!")
                    print("O problema pode estar no frontend ou na comunicação AJAX.")
                else:
                    print("\n❌ PROBLEMA NA QUERY DE FILTRO")
            else:
                print("\n❌ PROBLEMA EM GET_FILTER_OPTIONS")
        else:
            print("\n❌ PROBLEMA NA CONEXÃO COM BANCO")
    else:
        print("\n❌ PROBLEMA: ARQUIVO DO BANCO NÃO ENCONTRADO")
        print("Execute: python core/utils/migrar_para_sqlite.py")
