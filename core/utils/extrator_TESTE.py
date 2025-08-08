import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Lê o arquivo CSV e obtém os IDs
df = pd.read_csv('ocs_PR.CSV', encoding='latin1', sep=';', on_bad_lines='skip')
ids = df['id_osc'].dropna().astype(int).tolist()[:5]

resultados = []

for id_osc in ids:
    url = f'https://mapaosc.ipea.gov.br/detalhar/{id_osc}'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Nome
        nome = soup.find('h1').get_text(strip=True) if soup.find('h1') else ''

        # Email
        email_tag = soup.find('a', href=lambda x: x and x.startswith('mailto:'))
        email = ''
        if email_tag and 'href' in email_tag.attrs:
            email = email_tag['href'].replace('mailto:', '').strip()

        # Telefone
        telefone = ''
        phone_svg = soup.find('svg', {'data-icon': 'phone-alt'})
        if phone_svg and phone_svg.next_sibling:
            telefone = phone_svg.next_sibling.strip()

        # Endereço
        endereco = ''
        for br in soup.find_all('br'):
            if br.previous_sibling and isinstance(br.previous_sibling, str):
                endereco = br.previous_sibling.strip()
                if endereco:
                    break

        # Situação cadastral
        situacao = ''
        sit_h4 = soup.find('h4', string=lambda x: x and 'Situação cadastral' in x)
        if sit_h4:
            p = sit_h4.find_next('p')
            if p:
                situacao = p.get_text(strip=True)

        # Natureza jurídica
        natureza = ''
        nat_strong = soup.find('strong', string=lambda x: x and 'Natureza jurídica:' in x)
        if nat_strong and nat_strong.next_sibling:
            natureza = nat_strong.next_sibling.strip()

        resultados.append({
            'id_osc': id_osc,
            'nome': nome,
            'email': email,
            'endereco': endereco,
            'telefone': telefone,
            'natureza_juridica': natureza,
            'situacao_cadastral': situacao
        })
    except Exception as e:
        print(f'Erro ao processar {id_osc}: {e}')
    time.sleep(1)  # Respeita o servidor

# Salva os resultados em um novo CSV
pd.DataFrame(resultados).to_csv('dados_osc_PR.csv', index=False)