"""
Script para corrigir números de telefone no CSV, removendo o espaço entre o DDD e o número.
"""

import pandas as pd
import re
import os

def corrigir_telefone(telefone):
    if pd.isna(telefone):
        return telefone
    # Remove todos os espaços
    telefone = str(telefone).replace(' ', '')
    # Remove outros caracteres não numéricos, se necessário
    telefone = re.sub(r'[^\d]', '', telefone)
    return telefone

def corrigir_telefones_csv(arquivo_entrada, arquivo_saida):
    df = pd.read_csv(arquivo_entrada, encoding='utf-8')
    if 'telefone' in df.columns:
        df['telefone'] = df['telefone'].apply(corrigir_telefone)
        df.to_csv(arquivo_saida, index=False, encoding='utf-8')
        print(f"Arquivo corrigido salvo em: {arquivo_saida}")
    else:
        print("Coluna 'telefone' não encontrada no arquivo.")

if __name__ == "__main__":
    arquivo_entrada = "data/dados_osc_PR_completo.csv"
    arquivo_saida = "data/dados_osc_PR_completo_corrigido.csv"
    corrigir_telefones_csv(arquivo_entrada, arquivo_saida)
