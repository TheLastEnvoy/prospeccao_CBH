import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def extrair_dados(id_osc):
    url = f'https://mapaosc.ipea.gov.br/detalhar/{id_osc}'
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        nome = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''
        email_tag = soup.find('a', href=lambda x: x and x.startswith('mailto:'))
        email = email_tag['href'].replace('mailto:', '').strip() if email_tag and 'href' in email_tag.attrs else ''
        telefone = ''
        phone_svg = soup.find('svg', {'data-icon': 'phone-alt'})
        if phone_svg and phone_svg.next_sibling:
            telefone = phone_svg.next_sibling.strip()
        endereco = ''
        for br in soup.find_all('br'):
            if br.previous_sibling and isinstance(br.previous_sibling, str):
                endereco = br.previous_sibling.strip()
                if endereco:
                    break
        situacao = ''
        sit_h4 = soup.find('h4', string=lambda x: x and 'Situação cadastral' in x)
        if sit_h4:
            p = sit_h4.find_next('p')
            if p:
                situacao = p.get_text(strip=True)
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

df = pd.read_csv('ocs_PR.CSV', encoding='latin1', sep=';', on_bad_lines='skip')
ids = df['id_osc'].dropna().astype(int).tolist()

resultados = []
start_time = time.time()
save_interval = 60  # segundos

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(extrair_dados, id_osc): id_osc for id_osc in ids}
    for i, future in enumerate(as_completed(futures)):
        resultado = future.result()
        resultados.append(resultado)
        # Salva a cada 1 minuto de execução
        if time.time() - start_time > save_interval:
            pd.DataFrame(resultados).to_csv('dados_osc_PR_fast.csv', index=False)
            print(f'Salvo progresso após {i+1} OSCs.')
            start_time = time.time()

# Salva os resultados finais
pd.DataFrame(resultados).to_csv('dados_osc_PR_fast.csv', index=False)