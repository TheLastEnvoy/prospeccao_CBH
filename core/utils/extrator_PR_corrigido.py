"""
Extrator corrigido para dados do MapaOSC - IPEA
Versão com seletores atualizados para telefone e situação cadastral
"""

import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def extrair_dados(id_osc):
    """Extrai dados de uma OSC específica com seletores corrigidos"""
    url = f'https://mapaosc.ipea.gov.br/detalhar/{id_osc}'
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Nome da OSC
        nome = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''
        
        # Email
        email_tag = soup.find('a', href=lambda x: x and x.startswith('mailto:'))
        email = email_tag['href'].replace('mailto:', '').strip() if email_tag and 'href' in email_tag.attrs else ''
        
        # Telefone - CORRIGIDO
        telefone = ''
        phone_icon = soup.find('i', class_='fas fa-phone-alt')
        if phone_icon and phone_icon.parent:
            # Pega o texto do parent do ícone (que contém o telefone)
            telefone = phone_icon.parent.get_text(strip=True)
            # Remove o ícone e limpa o texto
            telefone = re.sub(r'[^\d\s\-\(\)]', '', telefone).strip()
        
        # Endereço
        endereco = ''
        for br in soup.find_all('br'):
            if br.previous_sibling and isinstance(br.previous_sibling, str):
                endereco = br.previous_sibling.strip()
                if endereco:
                    break
        
        # Situação Cadastral - CORRIGIDO
        situacao = ''
        # Procura por h4 que contenha "Situação cadastral"
        for h4 in soup.find_all('h4'):
            if h4.get_text(strip=True) == 'Situação cadastral:':
                # Pega o próximo elemento (que contém a situação)
                next_element = h4.find_next_sibling()
                if next_element:
                    situacao = next_element.get_text(strip=True)
                break
        
        # Natureza Jurídica
        natureza = ''
        nat_strong = soup.find('strong', string=lambda x: x and 'Natureza jurídica:' in x)
        if nat_strong and nat_strong.next_sibling:
            natureza = nat_strong.next_sibling.strip()

        return {
            'id_osc': id_osc,
            'nome': nome,
            'email': email,
            'endereco': endereco,
            'telefone': telefone,
            'natureza_juridica': natureza,
            'situacao_cadastral': situacao
        }
        
    except Exception as e:
        print(f'Erro ao processar {id_osc}: {e}')
        return {
            'id_osc': id_osc,
            'nome': '',
            'email': '',
            'endereco': '',
            'telefone': '',
            'natureza_juridica': '',
            'situacao_cadastral': ''
        }

def testar_extracao_corrigida():
    """Testa a extração corrigida com alguns IDs"""
    ids_teste = [547149, 538421, 463397, 585415]
    
    print("🧪 TESTE DA EXTRAÇÃO CORRIGIDA")
    print("=" * 60)
    
    for id_osc in ids_teste:
        print(f"\n🔍 Testando OSC ID: {id_osc}")
        resultado = extrair_dados(id_osc)
        
        print(f"  📝 Nome: {resultado['nome']}")
        print(f"  📧 Email: {resultado['email']}")
        print(f"  📱 Telefone: '{resultado['telefone']}'")
        print(f"  🏠 Endereço: {resultado['endereco']}")
        print(f"  ⚖️  Natureza: {resultado['natureza_juridica']}")
        print(f"  📋 Situação: '{resultado['situacao_cadastral']}'")
        
        time.sleep(1)  # Pausa entre requisições

def extrair_todas_oscs():
    """Extrai dados de todas as OSCs do arquivo"""
    
    print("🚀 INICIANDO EXTRAÇÃO COMPLETA")
    print("=" * 60)
    
    # Carrega os IDs das OSCs com delimitador correto
    try:
        
        df = pd.read_csv('data/osc_PR_novo.CSV', sep=';', on_bad_lines='skip')
        
        # Verifica as colunas disponíveis
        print(f"📋 Colunas encontradas: {list(df.columns)}")
        
        # Procura pela coluna id_osc (pode ter BOM)
        id_column = None
        for col in df.columns:
            if 'id_osc' in col.lower():
                id_column = col
                break
        
        if not id_column:
            print("❌ Coluna id_osc não encontrada!")
            print("Colunas disponíveis:")
            for i, col in enumerate(df.columns):
                print(f"  {i+1}. {col}")
            return
        
        print(f"✅ Usando coluna: {id_column}")
        
        # Remove valores nulos e converte para int
        ids = df[id_column].dropna().astype(int).tolist()
        print(f"📊 Total de OSCs para processar: {len(ids)}")
        
        # Mostra alguns IDs de exemplo
        print(f"🔍 Exemplos de IDs: {ids[:5]}")
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return
    
    # Carrega IDs já no banco (fonte de verdade única)
    resultados = []
    ids_processados = set()
    try:
        conn = sqlite3.connect('data/oscs_parana_novo.db')
        ids_processados = set(
            pd.read_sql('SELECT id_osc FROM oscs', conn)['id_osc'].astype(int).tolist()
        )
        conn.close()
        print(f"🗄️  Banco de dados: {len(ids_processados)} OSCs já inseridas.")
    except Exception as e:
        print(f"⚠️  Não foi possível ler o banco: {e}. Verificando CSVs...")
        # Fallback para CSVs caso o banco não esteja disponível
        for csv in ['data/dados_osc_PR_FINAL.csv', 'data/dados_osc_PR_fast_corrigido.csv']:
            try:
                df_tmp = pd.read_csv(csv, on_bad_lines='skip')
                if 'id_osc' in df_tmp.columns:
                    ids_processados.update(df_tmp['id_osc'].dropna().astype(int).tolist())
            except Exception:
                pass
        print(f"📂 Fallback CSVs: {len(ids_processados)} OSCs já processadas.")

    # Filtra apenas IDs ainda não processados
    ids_restantes = [id_osc for id_osc in ids if id_osc not in ids_processados]
    print(f"📊 OSCs restantes para processar: {len(ids_restantes)}")

    start_time = time.time()
    save_interval = 60  # segundos

    print(f"⏱️  Iniciando processamento com ThreadPoolExecutor...")

    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {executor.submit(extrair_dados, id_osc): id_osc for id_osc in ids_restantes}
        for i, future in enumerate(as_completed(futures)):
            resultado = future.result()
            resultados.append(resultado)

            # Mostra progresso a cada 100 OSCs
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                remaining = (len(ids_restantes) - (i + 1)) / rate if rate > 0 else 0
                print(f"📈 Progresso: {i+1}/{len(ids_restantes)} ({((i+1)/len(ids_restantes)*100):.1f}%) - Taxa: {rate:.1f} OSCs/s - Restante: {remaining/60:.1f} min")

            # Salva a cada intervalo
            if time.time() - start_time > save_interval:
                df_temp = pd.DataFrame(resultados)
                df_temp.to_csv('data/dados_osc_PR_fast_corrigido.csv', index=False)
                print(f"💾 Salvamento intermediário: {len(resultados)} OSCs processadas")
                start_time = time.time()
    
    # Salva os resultados finais
    df_final = pd.DataFrame(resultados)
    df_final.to_csv('data/dados_osc_PR_fast_corrigido.csv', index=False)
    
    print(f"\n✅ EXTRAÇÃO CONCLUÍDA!")
    print(f"📊 Total de OSCs processadas: {len(resultados)}")
    print(f"💾 Arquivo salvo: data/dados_osc_PR_fast_corrigido.csv")
    
    # Estatísticas
    telefones_coletados = sum(1 for r in resultados if r['telefone'])
    situacoes_coletadas = sum(1 for r in resultados if r['situacao_cadastral'])
    
    print(f"📱 Telefones coletados: {telefones_coletados}/{len(resultados)} ({telefones_coletados/len(resultados)*100:.1f}%)")
    print(f"📋 Situações coletadas: {situacoes_coletadas}/{len(resultados)} ({situacoes_coletadas/len(resultados)*100:.1f}%)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'teste':
        testar_extracao_corrigida()
    else:
        extrair_todas_oscs()
