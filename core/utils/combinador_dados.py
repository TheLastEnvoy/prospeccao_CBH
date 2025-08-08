"""
Script para combinar dados de OSCs do Paraná
Combina dados extraídos do MapaOSC com informações municipais
"""

import pandas as pd
import logging
from typing import Optional
import os
import sys

# Adiciona o diretório utils ao path para importar a classe de correção
sys.path.append(os.path.join(os.path.dirname(__file__)))
from correcaoPlanilha import FixEncodingSpreadsheet

class CombinadorDadosOSC:
    """Classe para combinar dados de OSCs com informações municipais"""
    
    def __init__(self):
        # Configuração de logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
        # Inicializa o corretor de encoding
        self.corretor_encoding = FixEncodingSpreadsheet()
    
    def carregar_dados_originais(self, arquivo_original: str) -> pd.DataFrame:
        """Carrega dados do arquivo CSV original com informações municipais"""
        try:
            self.logger.info(f"Carregando dados originais de: {arquivo_original}")
            
            # Carrega o arquivo com encoding correto
            df = pd.read_csv(arquivo_original, encoding='latin1', sep=';', on_bad_lines='skip')
            
            # Corrige o nome da primeira coluna (remove BOM se presente)
            if df.columns[0].startswith('ï»¿'):
                df.columns = [col.replace('ï»¿', '') if col.startswith('ï»¿') else col for col in df.columns]
            
            self.logger.info(f"Colunas encontradas: {list(df.columns)}")
            
            # Seleciona apenas as colunas necessárias
            colunas_necessarias = ['id_osc', 'edmu_cd_municipio', 'edmu_nm_municipio']
            colunas_disponiveis = [col for col in colunas_necessarias if col in df.columns]
            
            if not colunas_disponiveis:
                raise ValueError(f"Nenhuma das colunas necessárias encontrada. Colunas disponíveis: {list(df.columns)}")
            
            df_original = df[colunas_disponiveis].copy()
            
            # Corrige problemas de encoding nos nomes dos municípios
            if 'edmu_nm_municipio' in df_original.columns:
                self.logger.info("Corrigindo encoding dos nomes dos municípios...")
                df_original['edmu_nm_municipio'] = df_original['edmu_nm_municipio'].apply(
                    lambda x: self.corretor_encoding.fix_text_encoding(x) if pd.notna(x) and isinstance(x, str) else x
                )
            
            # Converte id_osc para int para garantir compatibilidade
            df_original['id_osc'] = pd.to_numeric(df_original['id_osc'], errors='coerce').astype('Int64')
            
            # Remove linhas com id_osc nulo
            df_original = df_original.dropna(subset=['id_osc'])
            
            self.logger.info(f"Dados originais carregados: {len(df_original)} registros")
            return df_original
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados originais: {e}")
            raise
    
    def carregar_dados_extraidos(self, arquivo_extraido: str) -> pd.DataFrame:
        """Carrega dados do arquivo CSV extraído do MapaOSC"""
        try:
            self.logger.info(f"Carregando dados extraídos de: {arquivo_extraido}")
            
            df_extraido = pd.read_csv(arquivo_extraido, encoding='utf-8')
            
            # Converte id_osc para int para garantir compatibilidade
            df_extraido['id_osc'] = pd.to_numeric(df_extraido['id_osc'], errors='coerce').astype('Int64')
            
            # Remove linhas com id_osc nulo
            df_extraido = df_extraido.dropna(subset=['id_osc'])
            
            self.logger.info(f"Dados extraídos carregados: {len(df_extraido)} registros")
            return df_extraido
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados extraídos: {e}")
            raise
    
    def combinar_dados(self, df_original: pd.DataFrame, df_extraido: pd.DataFrame) -> pd.DataFrame:
        """Combina os dados dos dois DataFrames baseado no id_osc"""
        try:
            self.logger.info("Iniciando combinação dos dados...")
            
            # Faz o merge dos dados baseado no id_osc
            df_combinado = df_extraido.merge(
                df_original,
                on='id_osc',
                how='left',
                suffixes=('', '_original')
            )
            
            # Reorganiza as colunas na ordem solicitada
            colunas_finais = [
                'id_osc',
                'nome',
                'email',
                'endereco',
                'telefone',
                'natureza_juridica',
                'situacao_cadastral',
                'edmu_cd_municipio',
                'edmu_nm_municipio'
            ]
            
            # Filtra apenas as colunas que existem
            colunas_existentes = [col for col in colunas_finais if col in df_combinado.columns]
            df_final = df_combinado[colunas_existentes].copy()
            
            # Preenche valores nulos com string vazia
            df_final = df_final.fillna('')
            
            self.logger.info(f"Dados combinados: {len(df_final)} registros")
            self.logger.info(f"Colunas finais: {list(df_final.columns)}")
            
            return df_final
            
        except Exception as e:
            self.logger.error(f"Erro ao combinar dados: {e}")
            raise
    
    def salvar_resultado(self, df: pd.DataFrame, arquivo_saida: str) -> None:
        """Salva o DataFrame combinado em um novo arquivo CSV"""
        try:
            self.logger.info(f"Salvando resultado em: {arquivo_saida}")
            
            # Cria o diretório de saída se não existir
            os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)
            
            # Salva o arquivo CSV
            df.to_csv(arquivo_saida, index=False, encoding='utf-8')
            
            self.logger.info(f"Arquivo salvo com sucesso: {arquivo_saida}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar arquivo: {e}")
            raise
    
    def mostrar_estatisticas(self, df: pd.DataFrame) -> None:
        """Mostra estatísticas dos dados combinados"""
        try:
            self.logger.info("=== ESTATÍSTICAS DOS DADOS COMBINADOS ===")
            self.logger.info(f"Total de registros: {len(df)}")
            self.logger.info(f"Registros com email: {len(df[df['email'] != ''])}")
            self.logger.info(f"Registros com telefone: {len(df[df['telefone'] != ''])}")
            self.logger.info(f"Registros com município: {len(df[df['edmu_nm_municipio'] != ''])}")
            
            if 'edmu_nm_municipio' in df.columns:
                municipios_unicos = df[df['edmu_nm_municipio'] != '']['edmu_nm_municipio'].nunique()
                self.logger.info(f"Municípios únicos: {municipios_unicos}")
            
            # Mostra alguns exemplos
            self.logger.info("\n=== EXEMPLOS DE DADOS ===")
            for i, row in df.head(3).iterrows():
                self.logger.info(f"OSC {i+1}: {row['nome']} - {row['edmu_nm_municipio']}")
                
        except Exception as e:
            self.logger.error(f"Erro ao mostrar estatísticas: {e}")

def combinar_dados_osc(arquivo_original: str, arquivo_extraido: str, arquivo_saida: str) -> str:
    """
    Função principal para combinar dados de OSCs
    
    Args:
        arquivo_original: Caminho para o arquivo CSV original com dados municipais
        arquivo_extraido: Caminho para o arquivo CSV extraído do MapaOSC
        arquivo_saida: Caminho para o arquivo CSV de saída
    
    Returns:
        Caminho do arquivo de saída criado
    """
    try:
        combinador = CombinadorDadosOSC()
        
        # Carrega os dados
        df_original = combinador.carregar_dados_originais(arquivo_original)
        df_extraido = combinador.carregar_dados_extraidos(arquivo_extraido)
        
        # Combina os dados
        df_combinado = combinador.combinar_dados(df_original, df_extraido)
        
        # Salva o resultado
        combinador.salvar_resultado(df_combinado, arquivo_saida)
        
        # Mostra estatísticas
        combinador.mostrar_estatisticas(df_combinado)
        
        return arquivo_saida
        
    except Exception as e:
        print(f"Erro durante a combinação: {e}")
        raise

if __name__ == "__main__":
    # Configuração dos arquivos
    arquivo_original = "data/ocs_PR.CSV"
    arquivo_extraido = "data/dados_osc_PR_fast.csv"
    arquivo_saida = "data/dados_osc_PR_completo.csv"
    
    # Executa a combinação
    resultado = combinar_dados_osc(arquivo_original, arquivo_extraido, arquivo_saida)
    print(f"\nProcesso concluído! Arquivo criado: {resultado}")
