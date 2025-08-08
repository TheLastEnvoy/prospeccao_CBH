"""
Script para migrar dados do CSV para SQLite3
"""

import pandas as pd
import sqlite3
import os
from pathlib import Path
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def migrar_csv_para_sqlite():
    """Migra dados do CSV para SQLite3"""
    
    # Caminhos dos arquivos
    csv_path = Path('data/dados_osc_PR_completo.csv')
    db_path = Path('data/oscs_parana_novo.db')
    
    try:
        logger.info("Iniciando migração de dados CSV para SQLite3...")
        
        # Verifica se o arquivo CSV existe
        if not csv_path.exists():
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_path}")
        
        # Carrega dados do CSV
        logger.info("Carregando dados do CSV...")
        df = pd.read_csv(csv_path, encoding='utf-8')
        logger.info(f"Dados carregados: {len(df)} registros")
        
        # Cria conexão com SQLite
        logger.info("Criando conexão com SQLite...")
        conn = sqlite3.connect(db_path)
        
        # Cria tabela e insere dados
        logger.info("Criando tabela e inserindo dados...")
        df.to_sql('oscs', conn, if_exists='replace', index=False)
        
        # Cria índices para melhor performance
        logger.info("Criando índices para otimização...")
        cursor = conn.cursor()
        
        # Índices para filtros comuns
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_municipio ON oscs(edmu_nm_municipio)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_natureza ON oscs(natureza_juridica)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_id_osc ON oscs(id_osc)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nome ON oscs(nome)")
        
        # Commit das alterações
        conn.commit()
        
        # Verifica os dados inseridos
        cursor.execute("SELECT COUNT(*) FROM oscs")
        total_registros = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT edmu_nm_municipio) FROM oscs WHERE edmu_nm_municipio != ''")
        total_municipios = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT natureza_juridica) FROM oscs WHERE natureza_juridica != ''")
        total_naturezas = cursor.fetchone()[0]
        
        # Fecha conexão
        conn.close()
        
        logger.info("=== MIGRAÇÃO CONCLUÍDA ===")
        logger.info(f"Total de registros: {total_registros}")
        logger.info(f"Total de municípios: {total_municipios}")
        logger.info(f"Total de naturezas jurídicas: {total_naturezas}")
        logger.info(f"Banco de dados criado: {db_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante a migração: {e}")
        return False

def verificar_banco():
    """Verifica se o banco de dados foi criado corretamente"""
    
    db_path = Path('data/oscs_parana.db')
    
    if not db_path.exists():
        logger.error("Banco de dados não encontrado!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica estrutura da tabela
        cursor.execute("PRAGMA table_info(oscs)")
        colunas = cursor.fetchall()
        
        logger.info("=== ESTRUTURA DO BANCO ===")
        logger.info("Colunas da tabela 'oscs':")
        for coluna in colunas:
            logger.info(f"  - {coluna[1]} ({coluna[2]})")
        
        # Verifica alguns dados de exemplo
        cursor.execute("SELECT * FROM oscs LIMIT 3")
        exemplos = cursor.fetchall()
        
        logger.info("\n=== EXEMPLOS DE DADOS ===")
        for i, exemplo in enumerate(exemplos, 1):
            logger.info(f"Registro {i}: {exemplo}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Erro ao verificar banco: {e}")
        return False

if __name__ == "__main__":
    print("=== MIGRADOR CSV PARA SQLITE3 ===")
    
    # Executa migração
    sucesso = migrar_csv_para_sqlite()
    
    if sucesso:
        print("\n✅ Migração concluída com sucesso!")
        
        # Verifica o banco criado
        print("\n=== VERIFICANDO BANCO CRIADO ===")
        verificar_banco()
        
    else:
        print("\n❌ Erro na migração!")
