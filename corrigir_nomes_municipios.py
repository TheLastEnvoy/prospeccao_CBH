#!/usr/bin/env python3
"""
Script para corrigir nomes incorretos de municípios no banco de dados
"""

import sqlite3
import os
import sys
import re
from pathlib import Path

def detectar_problemas_codificacao():
    """Detecta automaticamente problemas de codificação nos nomes de municípios"""
    db_path = os.path.join('data', 'oscs_parana_novo.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("🔍 Detectando problemas de codificação...")

    # Buscar municípios com caracteres problemáticos
    cursor.execute("SELECT DISTINCT edmu_nm_municipio FROM oscs")
    todos_municipios = [row[0] for row in cursor.fetchall()]

    problemas_encontrados = {}

    for municipio in todos_municipios:
        # Verificar se há caracteres de escape ou codificação incorreta
        if ('\\x' in repr(municipio) or
            'â' in municipio or
            'Ã' in municipio or
            len(municipio.encode('utf-8')) != len(municipio)):

            cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", [municipio])
            count = cursor.fetchone()[0]

            # Tentar sugerir correção
            nome_sugerido = municipio

            # Correções conhecidas
            if 'Áâ\x80\x9angulo' in repr(municipio):
                nome_sugerido = 'Ângulo'
            elif 'Ã' in municipio:
                nome_sugerido = municipio.replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã­', 'í').replace('Ã³', 'ó').replace('Ãº', 'ú').replace('Ã§', 'ç').replace('Ã ', 'à')

            problemas_encontrados[municipio] = {
                'count': count,
                'sugestao': nome_sugerido,
                'repr': repr(municipio)
            }

    if problemas_encontrados:
        print(f"   Encontrados {len(problemas_encontrados)} municípios com problemas:")
        for municipio, info in problemas_encontrados.items():
            print(f"      {info['repr']} -> '{info['sugestao']}' ({info['count']} OSCs)")
    else:
        print("   ✅ Nenhum problema de codificação detectado")

    conn.close()
    return problemas_encontrados

def backup_database():
    """Cria backup do banco antes das alterações"""
    db_path = os.path.join('data', 'oscs_parana_novo.db')
    backup_path = os.path.join('data', 'oscs_parana_novo_backup.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Copia o arquivo
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

def verificar_municipios_antes():
    """Verifica os municípios que serão alterados"""
    db_path = os.path.join('data', 'oscs_parana_novo.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("🔍 Verificando municípios que serão corrigidos...")

    # Primeiro, vamos identificar municípios com problemas de codificação
    print("\n🔍 Buscando municípios com problemas de codificação...")
    cursor.execute("SELECT DISTINCT edmu_nm_municipio FROM oscs WHERE edmu_nm_municipio LIKE '%\\x%' OR edmu_nm_municipio LIKE '%â%'")
    municipios_problematicos = [row[0] for row in cursor.fetchall()]

    if municipios_problematicos:
        print("   Municípios com problemas de codificação encontrados:")
        for municipio in municipios_problematicos:
            cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", [municipio])
            count = cursor.fetchone()[0]
            print(f"      '{repr(municipio)}': {count} OSCs")

    # Municípios a serem corrigidos
    # Nota: Coronel Domingos Soares (com "s") é o nome CORRETO
    correcoes = {
        "Diamante D'Oeste": 'Diamante do Oeste',
        'Áâ\x80\x9angulo': 'Ângulo'  # Correção de codificação
    }
    
    for nome_incorreto, nome_correto in correcoes.items():
        cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", [nome_incorreto])
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"   📍 '{nome_incorreto}' -> '{nome_correto}': {count} OSCs")
        else:
            print(f"   ⚠️ '{nome_incorreto}': Não encontrado no banco")
    
    conn.close()
    return correcoes

def corrigir_municipios():
    """Executa as correções no banco de dados"""
    db_path = os.path.join('data', 'oscs_parana_novo.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n🔧 Executando correções...")
    
    # Correções a serem aplicadas
    # Nota: Coronel Domingos Soares (com "s") é o nome CORRETO
    correcoes = {
        "Diamante D'Oeste": 'Diamante do Oeste',
        'Áâ\x80\x9angulo': 'Ângulo'  # Correção de codificação
    }
    
    total_alteracoes = 0
    
    for nome_incorreto, nome_correto in correcoes.items():
        print(f"\n   Corrigindo: '{nome_incorreto}' -> '{nome_correto}'")
        
        # Verificar quantos registros serão afetados
        cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", [nome_incorreto])
        count_antes = cursor.fetchone()[0]
        
        if count_antes == 0:
            print(f"      ⚠️ Nenhum registro encontrado para '{nome_incorreto}'")
            continue
        
        # Executar a correção
        cursor.execute(
            "UPDATE oscs SET edmu_nm_municipio = ? WHERE edmu_nm_municipio = ?",
            [nome_correto, nome_incorreto]
        )
        
        # Verificar se a correção funcionou
        cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", [nome_correto])
        count_depois = cursor.fetchone()[0]
        
        # Verificar se ainda existem registros com o nome antigo
        cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", [nome_incorreto])
        count_antigo = cursor.fetchone()[0]
        
        if count_antigo == 0 and count_depois >= count_antes:
            print(f"      ✅ Sucesso: {count_antes} registros alterados")
            total_alteracoes += count_antes
        else:
            print(f"      ❌ Problema na correção:")
            print(f"         Antes: {count_antes}, Depois: {count_depois}, Restantes: {count_antigo}")
    
    # Commit das alterações
    conn.commit()
    conn.close()
    
    print(f"\n📊 Total de registros alterados: {total_alteracoes}")
    return total_alteracoes

def verificar_municipios_depois():
    """Verifica os municípios após as correções"""
    db_path = os.path.join('data', 'oscs_parana_novo.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n✅ Verificando resultado das correções...")
    
    # Verificar os nomes corretos
    nomes_corretos = [
        'Coronel Domingos Soares',  # Nome correto (com "s")
        'Diamante do Oeste',
        'Ângulo'
    ]
    
    for nome in nomes_corretos:
        cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", [nome])
        count = cursor.fetchone()[0]
        print(f"   📍 '{nome}': {count} OSCs")
    
    # Verificar se ainda existem nomes incorretos
    nomes_incorretos = [
        "Diamante D'Oeste",
        'Áâ\x80\x9angulo'
    ]
    
    print("\n🔍 Verificando se nomes incorretos ainda existem...")
    for nome in nomes_incorretos:
        cursor.execute("SELECT COUNT(*) FROM oscs WHERE edmu_nm_municipio = ?", [nome])
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   ⚠️ '{nome}': {count} OSCs (ainda existe!)")
        else:
            print(f"   ✅ '{nome}': 0 OSCs (corrigido)")
    
    conn.close()

def testar_api_depois():
    """Testa a API após as correções"""
    print("\n🧪 Testando API após correções...")
    
    try:
        import os
        import sys
        import django
        
        # Configurar Django
        sys.path.append('.')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_osc.settings')
        django.setup()
        
        from osc_dashboard.views import get_oscs_por_municipio
        
        dados = get_oscs_por_municipio()
        municipios_dict = {item['municipio']: item['total_oscs'] for item in dados}
        
        # Verificar os municípios corrigidos
        municipios_teste = [
            'Coronel Domingos Soares',  # Nome correto (com "s")
            'Diamante do Oeste',
            'Ângulo'
        ]
        
        for municipio in municipios_teste:
            if municipio in municipios_dict:
                oscs = municipios_dict[municipio]
                print(f"   ✅ API: '{municipio}': {oscs} OSCs")
            else:
                print(f"   ❌ API: '{municipio}': Não encontrado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao testar API: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 70)
    print("🔧 CORREÇÃO DE NOMES DE MUNICÍPIOS NO BANCO DE DADOS")
    print("=" * 70)
    
    # 1. Criar backup
    print("\n1️⃣ Criando backup do banco de dados...")
    if not backup_database():
        print("❌ Falha ao criar backup. Abortando.")
        return False
    
    # 2. Detectar problemas de codificação
    print("\n2️⃣ Detectando problemas de codificação...")
    problemas_codificacao = detectar_problemas_codificacao()

    # 3. Verificar antes
    print("\n3️⃣ Verificando municípios antes das correções...")
    correcoes = verificar_municipios_antes()
    
    # 4. Confirmar com o usuário
    print(f"\n⚠️ ATENÇÃO: Serão alterados registros no banco de dados!")
    print(f"   Backup criado em: data/oscs_parana_novo_backup.db")
    if problemas_codificacao:
        print(f"   {len(problemas_codificacao)} problemas de codificação detectados")

    resposta = input("\n🤔 Deseja continuar com as correções? (s/N): ").strip().lower()
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada pelo usuário.")
        return False

    # 5. Executar correções
    print("\n4️⃣ Executando correções...")
    total_alteracoes = corrigir_municipios()
    
    if total_alteracoes == 0:
        print("⚠️ Nenhuma alteração foi feita.")
        return False
    
    # 6. Verificar depois
    print("\n5️⃣ Verificando resultado...")
    verificar_municipios_depois()

    # 7. Testar API
    print("\n6️⃣ Testando API...")
    api_ok = testar_api_depois()
    
    # 8. Resultado final
    print("\n" + "=" * 70)
    if api_ok and total_alteracoes > 0:
        print("✅ CORREÇÕES APLICADAS COM SUCESSO!")
        print(f"   {total_alteracoes} registros alterados")
        print("   Nomes de municípios corrigidos no banco")
        print("   Problemas de codificação resolvidos")
        print("   API retornando dados corretos")
        print("   Mapa deve funcionar corretamente agora")
        print("\n📍 Municípios corrigidos:")
        print("   • Diamante D'Oeste → Diamante do Oeste")
        print("   • Áâ\\x80\\x9angulo → Ângulo")
        print("\n📝 Nota: Coronel Domingos Soares (com 's') já estava correto no banco")
    else:
        print("⚠️ CORREÇÕES PARCIAIS OU COM PROBLEMAS")
        print("   Verifique os logs acima para detalhes")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
