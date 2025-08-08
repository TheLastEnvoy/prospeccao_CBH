"""
Script para combinar dados extraídos do MapaOSC com informações municipais
Usa os arquivos 'dados_osc_PR_fast_corrigido.csv' e 'osc_PR.CSV'
"""

import pandas as pd
import os

def carregar_dados_extraidos(arquivo_extraido: str) -> pd.DataFrame:
    """Carrega dados do arquivo CSV extraído do MapaOSC"""
    df_extraido = pd.read_csv(arquivo_extraido, encoding='utf-8')
    df_extraido['id_osc'] = pd.to_numeric(df_extraido['id_osc'], errors='coerce').astype('Int64')
    df_extraido = df_extraido.dropna(subset=['id_osc'])
    return df_extraido

def carregar_dados_municipais(arquivo_municipal: str) -> pd.DataFrame:
    """Carrega dados do arquivo CSV original com informações municipais"""
    df = pd.read_csv(arquivo_municipal, encoding='latin1', sep=';', on_bad_lines='skip')
    # Corrige BOM na primeira coluna se necessário
    if df.columns[0].startswith('ï»¿'):
        df.columns = [col.replace('ï»¿', '') if col.startswith('ï»¿') else col for col in df.columns]
    # Seleciona colunas necessárias
    colunas_necessarias = ['id_osc', 'edmu_cd_municipio', 'edmu_nm_municipio']
    colunas_disponiveis = [col for col in colunas_necessarias if col in df.columns]
    df_municipal = df[colunas_disponiveis].copy()
    df_municipal['id_osc'] = pd.to_numeric(df_municipal['id_osc'], errors='coerce').astype('Int64')
    df_municipal = df_municipal.dropna(subset=['id_osc'])
    return df_municipal

def combinar_dados(df_extraido: pd.DataFrame, df_municipal: pd.DataFrame) -> pd.DataFrame:
    """Combina os dados dos dois DataFrames baseado no id_osc"""
    df_combinado = pd.merge(df_extraido, df_municipal, on='id_osc', how='left')
    return df_combinado

def salvar_resultado(df: pd.DataFrame, arquivo_saida: str) -> None:
    os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)
    df.to_csv(arquivo_saida, index=False, encoding='utf-8')
    print(f"Arquivo salvo: {arquivo_saida}")

def mostrar_estatisticas(df: pd.DataFrame) -> None:
    print(f"Total de OSCs combinadas: {len(df)}")
    print(f"Municípios únicos: {df['edmu_nm_municipio'].nunique() if 'edmu_nm_municipio' in df.columns else 'N/A'}")
    print(f"Naturezas jurídicas únicas: {df['natureza_juridica'].nunique() if 'natureza_juridica' in df.columns else 'N/A'}")

if __name__ == "__main__":
    arquivo_extraido = "data/dados_osc_PR_fast_corrigido.csv"
    arquivo_municipal = "data/osc_PR.CSV"
    arquivo_saida = "data/dados_osc_PR_completo.csv"

    print("Carregando dados extraídos...")
    df_extraido = carregar_dados_extraidos(arquivo_extraido)
    print("Carregando dados municipais...")
    df_municipal = carregar_dados_municipais(arquivo_municipal)
    print("Combinando dados...")
    df_combinado = combinar_dados(df_extraido, df_municipal)
    salvar_resultado(df_combinado, arquivo_saida)
    mostrar_estatisticas(df_combinado)
