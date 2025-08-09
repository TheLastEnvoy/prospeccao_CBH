#!/usr/bin/env python3
"""
Script para verificar situações cadastrais disponíveis
"""

import sqlite3
import os

def check_situacoes():
    """Verifica situações cadastrais no banco"""
    db_path = os.path.join('data', 'oscs_parana_novo.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Situações cadastrais únicas
    cursor.execute("SELECT DISTINCT situacao_cadastral FROM oscs WHERE situacao_cadastral != '' ORDER BY situacao_cadastral")
    situacoes = [row[0] for row in cursor.fetchall()]
    
    print("📋 Situações Cadastrais Disponíveis:")
    for i, situacao in enumerate(situacoes, 1):
        cursor.execute("SELECT COUNT(*) FROM oscs WHERE situacao_cadastral = ?", [situacao])
        count = cursor.fetchone()[0]
        print(f"   {i}. {situacao}: {count} OSCs")
    
    conn.close()
    return situacoes

if __name__ == "__main__":
    check_situacoes()
