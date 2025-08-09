#!/usr/bin/env python3
"""
Script para testar os filtros corrigidos do dashboard
"""

import sqlite3
import os
import sys

def get_db_connection():
    """Retorna conexão com o banco SQLite"""
    db_path = os.path.join('data', 'oscs_parana_novo.db')
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return None
    return sqlite3.connect(db_path)

def test_municipio_filter():
    """Testa o filtro de município com igualdade exata"""
    print("🧪 Testando filtro de município...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Teste 1: Busca exata por "Palmeira"
    print("\n1. Buscando OSCs em 'Palmeira' (busca exata):")
    cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", ['Palmeira'])
    count_palmeira = cursor.fetchone()[0]
    print(f"   OSCs encontradas: {count_palmeira}")
    
    # Teste 2: Verificar se "São José das Palmeiras" não aparece
    print("\n2. Verificando se 'São José das Palmeiras' não aparece na busca por 'Palmeira':")
    cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", ['São José das Palmeiras'])
    count_sao_jose = cursor.fetchone()[0]
    print(f"   OSCs em 'São José das Palmeiras': {count_sao_jose}")
    
    # Teste 3: Busca com LIKE (método antigo) para comparação
    print("\n3. Comparação com busca LIKE (método antigo):")
    cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio LIKE ?", ['%Palmeira%'])
    count_like = cursor.fetchone()[0]
    print(f"   OSCs com LIKE '%Palmeira%': {count_like}")
    
    # Listar alguns municípios que contêm "Palmeira"
    print("\n4. Municípios que contêm 'Palmeira':")
    cursor.execute("SELECT DISTINCT edmu_nm_municipio FROM oscs WHERE edmu_nm_municipio LIKE ? ORDER BY edmu_nm_municipio", ['%Palmeira%'])
    municipios = cursor.fetchall()
    for municipio in municipios:
        print(f"   - {municipio[0]}")
    
    conn.close()

def test_keywords_filter():
    """Testa o filtro de palavras-chave"""
    print("\n🧪 Testando filtro de palavras-chave...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Teste com palavras-chave do exemplo do usuário
    keywords = ['agua', 'rural', 'ecológica', 'ambiental', 'ambiente', 'rios']
    
    print(f"\n1. Testando palavras-chave: {', '.join(keywords)}")
    
    # Construir query OR
    keyword_conditions = []
    params = []
    for keyword in keywords:
        keyword_conditions.append("nome LIKE ?")
        params.append(f'%{keyword}%')
    
    query = f"SELECT COUNT(*) FROM oscs WHERE ({' OR '.join(keyword_conditions)})"
    cursor.execute(query, params)
    count_total = cursor.fetchone()[0]
    print(f"   Total de OSCs com qualquer uma das palavras: {count_total}")
    
    # Testar cada palavra individualmente
    print("\n2. Contagem por palavra individual:")
    for keyword in keywords:
        cursor.execute("SELECT COUNT(*) FROM oscs WHERE nome LIKE ?", [f'%{keyword}%'])
        count = cursor.fetchone()[0]
        print(f"   '{keyword}': {count} OSCs")
    
    conn.close()

def test_combined_filters():
    """Testa filtros combinados: município + palavras-chave"""
    print("\n🧪 Testando filtros combinados...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Teste: Palmeira + palavras-chave ambientais
    municipio = 'Palmeira'
    keywords = ['agua', 'rural', 'ecológica', 'ambiental', 'ambiente', 'rios']
    
    print(f"\n1. Buscando OSCs em '{municipio}' com palavras-chave ambientais:")
    
    # Construir query combinada
    query = "SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?"
    params = [municipio]
    
    # Adicionar condições de palavras-chave
    keyword_conditions = []
    for keyword in keywords:
        keyword_conditions.append("nome LIKE ?")
        params.append(f'%{keyword}%')
    
    query += f" AND ({' OR '.join(keyword_conditions)})"
    
    cursor.execute(query, params)
    count_combined = cursor.fetchone()[0]
    print(f"   OSCs encontradas: {count_combined}")
    
    # Se encontrou resultados, mostrar alguns exemplos
    if count_combined > 0:
        print("\n2. Exemplos de OSCs encontradas:")
        query_examples = query.replace("COUNT(*)", "nome, edmu_nm_municipio") + " LIMIT 5"
        cursor.execute(query_examples, params)
        examples = cursor.fetchall()
        for i, (nome, municipio_osc) in enumerate(examples, 1):
            print(f"   {i}. {nome[:60]}... - {municipio_osc}")
    
    conn.close()

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 TESTE DOS FILTROS CORRIGIDOS DO DASHBOARD")
    print("=" * 60)
    
    # Verificar se o banco existe
    if not os.path.exists('data/oscs_parana_novo.db'):
        print("❌ Banco de dados não encontrado!")
        print("   Certifique-se de estar no diretório raiz do projeto.")
        return
    
    try:
        test_municipio_filter()
        test_keywords_filter()
        test_combined_filters()
        
        print("\n" + "=" * 60)
        print("✅ Testes concluídos com sucesso!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
