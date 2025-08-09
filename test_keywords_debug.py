#!/usr/bin/env python3
"""
Script para debugar o problema com palavras-chave
"""

import sqlite3
import os
import sys
import json

def get_db_connection():
    """Retorna conexão com o banco SQLite"""
    db_path = os.path.join('data', 'oscs_parana_novo.db')
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return None
    return sqlite3.connect(db_path)

def test_palmeira_rural():
    """Testa especificamente Palmeira + rural"""
    print("🧪 Testando Palmeira + 'rural'...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # 1. Primeiro, verificar OSCs em Palmeira
    print("\n1. OSCs em Palmeira:")
    cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", ['Palmeira'])
    count_palmeira = cursor.fetchone()[0]
    print(f"   Total: {count_palmeira}")
    
    # 2. Verificar OSCs com 'rural' no nome
    print("\n2. OSCs com 'rural' no nome:")
    cursor.execute("SELECT COUNT(*) FROM oscs WHERE nome LIKE ?", ['%rural%'])
    count_rural = cursor.fetchone()[0]
    print(f"   Total: {count_rural}")
    
    # 3. Verificar OSCs em Palmeira com 'rural' no nome
    print("\n3. OSCs em Palmeira com 'rural' no nome:")
    cursor.execute("""
        SELECT COUNT(*) FROM oscs 
        WHERE edmu_nm_municipio = ? AND nome LIKE ?
    """, ['Palmeira', '%rural%'])
    count_combined = cursor.fetchone()[0]
    print(f"   Total: {count_combined}")
    
    # 4. Se encontrou, mostrar exemplos
    if count_combined > 0:
        print("\n4. Exemplos encontrados:")
        cursor.execute("""
            SELECT nome, edmu_nm_municipio FROM oscs 
            WHERE edmu_nm_municipio = ? AND nome LIKE ?
            LIMIT 5
        """, ['Palmeira', '%rural%'])
        examples = cursor.fetchall()
        for i, (nome, municipio) in enumerate(examples, 1):
            print(f"   {i}. {nome} - {municipio}")
    else:
        print("\n4. ❌ Nenhuma OSC encontrada!")
        
        # Vamos verificar se há OSCs em Palmeira com nomes que contenham variações
        print("\n   Verificando variações de 'rural':")
        variations = ['rural', 'Rural', 'RURAL', 'agr', 'campo', 'fazend']
        for var in variations:
            cursor.execute("""
                SELECT COUNT(*) FROM oscs 
                WHERE edmu_nm_municipio = ? AND nome LIKE ?
            """, ['Palmeira', f'%{var}%'])
            count_var = cursor.fetchone()[0]
            if count_var > 0:
                print(f"     '{var}': {count_var} OSCs")
                # Mostrar um exemplo
                cursor.execute("""
                    SELECT nome FROM oscs 
                    WHERE edmu_nm_municipio = ? AND nome LIKE ?
                    LIMIT 1
                """, ['Palmeira', f'%{var}%'])
                example = cursor.fetchone()
                if example:
                    print(f"       Exemplo: {example[0][:60]}...")
    
    conn.close()

def test_javascript_format():
    """Testa como o JavaScript está enviando os dados"""
    print("\n🧪 Testando formato JavaScript...")
    
    # Simular como o JavaScript envia os dados
    keywords_array = ['rural']  # Array de palavras-chave
    keywords_string = ' '.join(keywords_array)  # Como getKeywordsString() faz
    
    print(f"   Array de palavras-chave: {keywords_array}")
    print(f"   String enviada: '{keywords_string}'")
    
    # Simular como o backend processa
    keywords_processed = [kw.strip() for kw in keywords_string.split() if kw.strip()]
    print(f"   Processado no backend: {keywords_processed}")
    
    # Testar a query que seria gerada
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Simular a query exata do backend
    query = "SELECT COUNT(*) FROM oscs WHERE 1=1"
    params = []
    
    # Adicionar filtro de município
    municipio = 'Palmeira'
    if municipio:
        query += " AND edmu_nm_municipio = ?"
        params.append(municipio)
    
    # Adicionar filtro de palavras-chave
    palavras_chave = keywords_string
    if palavras_chave:
        keywords = [kw.strip() for kw in palavras_chave.split() if kw.strip()]
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append("nome LIKE ?")
                params.append(f'%{keyword}%')
            query += f" AND ({' OR '.join(keyword_conditions)})"
    
    print(f"\n   Query gerada: {query}")
    print(f"   Parâmetros: {params}")
    
    cursor.execute(query, params)
    result = cursor.fetchone()[0]
    print(f"   Resultado: {result} OSCs")
    
    conn.close()

def test_case_sensitivity():
    """Testa sensibilidade a maiúsculas/minúsculas"""
    print("\n🧪 Testando sensibilidade a maiúsculas/minúsculas...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Testar diferentes variações de case
    test_cases = [
        'rural',
        'Rural', 
        'RURAL',
        'rURAL'
    ]
    
    for case in test_cases:
        cursor.execute("""
            SELECT COUNT(*) FROM oscs 
            WHERE edmu_nm_municipio = ? AND nome LIKE ?
        """, ['Palmeira', f'%{case}%'])
        count = cursor.fetchone()[0]
        print(f"   '{case}': {count} OSCs")
    
    # Testar com COLLATE NOCASE (case insensitive)
    print("\n   Testando com COLLATE NOCASE:")
    cursor.execute("""
        SELECT COUNT(*) FROM oscs 
        WHERE edmu_nm_municipio = ? AND nome LIKE ? COLLATE NOCASE
    """, ['Palmeira', '%rural%'])
    count_nocase = cursor.fetchone()[0]
    print(f"   'rural' (case insensitive): {count_nocase} OSCs")
    
    if count_nocase > 0:
        print("\n   Exemplos com case insensitive:")
        cursor.execute("""
            SELECT nome FROM oscs 
            WHERE edmu_nm_municipio = ? AND nome LIKE ? COLLATE NOCASE
            LIMIT 3
        """, ['Palmeira', '%rural%'])
        examples = cursor.fetchall()
        for i, (nome,) in enumerate(examples, 1):
            print(f"     {i}. {nome}")
    
    conn.close()

def test_actual_names_in_palmeira():
    """Mostra nomes reais de OSCs em Palmeira para análise"""
    print("\n🧪 Analisando nomes reais de OSCs em Palmeira...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Buscar todas as OSCs de Palmeira
    cursor.execute("""
        SELECT nome FROM oscs 
        WHERE edmu_nm_municipio = ?
        ORDER BY nome
        LIMIT 20
    """, ['Palmeira'])
    
    oscs = cursor.fetchall()
    print(f"\n   Primeiras 20 OSCs em Palmeira:")
    for i, (nome,) in enumerate(oscs, 1):
        print(f"     {i:2d}. {nome}")
        # Verificar se contém palavras relacionadas a rural
        nome_lower = nome.lower()
        rural_words = ['rural', 'agr', 'campo', 'fazend', 'produtor', 'pecuar']
        found_words = [word for word in rural_words if word in nome_lower]
        if found_words:
            print(f"         🎯 Contém: {', '.join(found_words)}")
    
    conn.close()

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 DEBUG DO PROBLEMA COM PALAVRAS-CHAVE")
    print("=" * 60)
    
    test_palmeira_rural()
    test_javascript_format()
    test_case_sensitivity()
    test_actual_names_in_palmeira()
    
    print("\n" + "=" * 60)
    print("✅ Debug concluído!")
    print("=" * 60)

if __name__ == "__main__":
    main()
