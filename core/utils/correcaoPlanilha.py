"""
Script para correção de problemas de encoding em planilhas Excel/CSV
Corrige caracteres acentuados mal codificados
"""

import pandas as pd
import re
from typing import Dict, Any
import chardet
import logging
import os

class FixEncodingSpreadsheet:
    """Classe para correção de problemas de encoding em planilhas"""

    def __init__(self):
        # Mapeamento de caracteres mal codificados mais comuns
        # Usando códigos Unicode para evitar problemas de interpretação
        self.encoding_fixes = {
            # Caracteres minúsculos com acento
            '\u00c3\u00a1': 'á',  # Ã¡ -> á
            '\u00c3\u00a9': 'é',  # Ã© -> é
            '\u00c3\u00ad': 'í',  # Ã­ -> í
            '\u00c3\u00b3': 'ó',  # Ã³ -> ó
            '\u00c3\u00ba': 'ú',  # Ãº -> ú
            '\u00c3\u00a0': 'à',  # Ã  -> à
            '\u00c3\u00aa': 'ê',  # Ãª -> ê
            '\u00c3\u00b4': 'ô',  # Ã´ -> ô
            '\u00c3\u00a2': 'â',  # Ã¢ -> â
            '\u00c3\u00a3': 'ã',  # Ã£ -> ã
            '\u00c3\u00a7': 'ç',  # Ã§ -> ç

            # Caracteres maiúsculos com acento
            '\u00c3\u0081': 'Á',  # Ã -> Á
            '\u00c3\u0089': 'É',  # Ã‰ -> É
            '\u00c3\u008d': 'Í',  # Ã -> Í
            '\u00c3\u0093': 'Ó',  # Ã" -> Ó
            '\u00c3\u009a': 'Ú',  # Ãš -> Ú
            '\u00c3\u0080': 'À',  # Ã€ -> À
            '\u00c3\u008a': 'Ê',  # ÃŠ -> Ê
            '\u00c3\u0094': 'Ô',  # Ã" -> Ô
            '\u00c3\u0082': 'Â',  # Ã‚ -> Â
            '\u00c3\u0083': 'Ã',  # Ãƒ -> Ã
            '\u00c3\u0087': 'Ç',  # Ã‡ -> Ç
        }

        # Mapeamento adicional usando strings literais simples
        self.simple_fixes = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
            'Ã ': 'à', 'Ãª': 'ê', 'Ã´': 'ô', 'Ã¢': 'â', 'Ã£': 'ã',
            'Ã§': 'ç', 'Ã±': 'ñ', 'Ãµ': 'õ', 'Ã¼': 'ü',
            'Ã': 'Á', 'Ã‰': 'É', 'Ã"': 'Ó', 'Ãš': 'Ú',
            'Ã€': 'À', 'ÃŠ': 'Ê', 'Ã"': 'Ô', 'Ã‚': 'Â', 'Ãƒ': 'Ã',
            'Ã‡': 'Ç', 'Ã•': 'Õ', 'Ãœ': 'Ü',

            # Casos específicos da planilha
            'nÃ£o': 'não',
            'cÃ£o': 'ção',
            'sÃ£o': 'são',
            'organizaçÃµes': 'organizações',
            'associaçÃµes': 'associações',
            'religiosas': 'religiosas',
            'AlmiranteÂ TamandaÃrÃ©': 'Almirante Tamandaré',
        }

        # Combina os dois dicionários
        self.all_fixes = {**self.encoding_fixes, **self.simple_fixes}

        # Configuração de logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def detect_encoding(self, file_path: str) -> str:
        """Detecta automaticamente o encoding de um arquivo"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Lê apenas os primeiros 10KB
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')
                confidence = result.get('confidence', 0)

                self.logger.info(f"Encoding detectado: {encoding} (confiança: {confidence:.2f})")
                return encoding
        except Exception as e:
            self.logger.warning(f"Erro ao detectar encoding: {e}")
            return 'utf-8'

    def fix_text_encoding(self, text: str) -> str:
        """Corrige problemas de encoding em uma string"""
        if pd.isna(text) or not isinstance(text, str):
            return text

        fixed_text = text

        # Aplica todas as correções
        for wrong, correct in self.all_fixes.items():
            if wrong in fixed_text:
                fixed_text = fixed_text.replace(wrong, correct)

        # Padrões regex para casos mais complexos
        patterns = [
            (r'([A-Za-z])Ã£o', r'\1ão'),      # qualquerÃ£o -> qualquerão
            (r'([A-Za-z])Ã§Ã£o', r'\1ção'),   # organizaÃ§Ã£o -> organização  
            (r'nÃ£o', 'não'),
            (r'sÃ£o', 'são'),
            (r'([A-Za-z])Ãµes', r'\1ões'),     # organizaçÃµes -> organizações
        ]

        for pattern, replacement in patterns:
            fixed_text = re.sub(pattern, replacement, fixed_text)

        return fixed_text

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processa todas as colunas de texto do DataFrame"""
        df_fixed = df.copy()

        for column in df_fixed.columns:
            if df_fixed[column].dtype == 'object':  # Colunas de texto
                self.logger.info(f"Processando coluna: {column}")
                original_values = df_fixed[column].dropna().astype(str)
                fixed_values = original_values.apply(self.fix_text_encoding)

                # Conta quantas correções foram feitas
                changes = sum(1 for orig, fixed in zip(original_values, fixed_values) if orig != fixed)
                if changes > 0:
                    self.logger.info(f"  -> {changes} correções aplicadas em '{column}'")
                    df_fixed[column] = df_fixed[column].apply(self.fix_text_encoding)
                else:
                    self.logger.info(f"  -> Nenhuma correção necessária em '{column}'")

        return df_fixed

    def fix_excel_file(self, input_path: str, output_path: str = None, 
                      sheet_name: str = 0) -> None:
        """Corrige arquivo Excel e salva a versão corrigida"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_corrigido.xlsx"

        try:
            # Lê o arquivo Excel
            self.logger.info(f"Lendo arquivo: {input_path}")
            df = pd.read_excel(input_path, sheet_name=sheet_name)
            self.logger.info(f"Planilha carregada: {df.shape[0]} linhas, {df.shape[1]} colunas")

            # Mostra algumas amostras dos dados originais
            self.logger.info("Amostra dos dados originais:")
            self._show_sample_data(df)

            # Corrige os problemas de encoding
            self.logger.info("Aplicando correções de encoding...")
            df_fixed = self.process_dataframe(df)

            # Mostra algumas amostras dos dados corrigidos
            self.logger.info("Amostra dos dados corrigidos:")
            self._show_sample_data(df_fixed)

            # Salva o arquivo corrigido
            self.logger.info(f"Salvando arquivo corrigido: {output_path}")
            df_fixed.to_excel(output_path, index=False, engine='openpyxl')

            self.logger.info("Correção concluída com sucesso!")
            return output_path

        except Exception as e:
            self.logger.error(f"Erro ao processar arquivo Excel: {e}")
            raise

    def fix_csv_file(self, input_path: str, output_path: str = None, 
                    delimiter: str = ',', encoding: str = None) -> None:
        """Corrige arquivo CSV e salva a versão corrigida"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_corrigido.csv"

        if encoding is None:
            encoding = self.detect_encoding(input_path)

        try:
            # Lê o arquivo CSV
            self.logger.info(f"Lendo arquivo CSV: {input_path}")
            df = pd.read_csv(input_path, delimiter=delimiter, encoding=encoding)
            self.logger.info(f"CSV carregado: {df.shape[0]} linhas, {df.shape[1]} colunas")

            # Corrige os problemas de encoding
            self.logger.info("Aplicando correções de encoding...")
            df_fixed = self.process_dataframe(df)

            # Salva o arquivo corrigido
            self.logger.info(f"Salvando arquivo corrigido: {output_path}")
            df_fixed.to_csv(output_path, index=False, encoding='utf-8')

            self.logger.info("Correção concluída com sucesso!")
            return output_path

        except Exception as e:
            self.logger.error(f"Erro ao processar arquivo CSV: {e}")
            raise

    def _show_sample_data(self, df: pd.DataFrame, num_samples: int = 3) -> None:
        """Mostra algumas amostras dos dados para verificação"""
        text_columns = df.select_dtypes(include=['object']).columns

        for col in text_columns[:3]:  # Mostra apenas 3 colunas
            sample_data = df[col].dropna().head(num_samples).tolist()
            for i, item in enumerate(sample_data):
                # Trunca strings muito longas
                display_item = str(item)[:50] + "..." if len(str(item)) > 50 else str(item)
                self.logger.info(f"  {col}[{i}]: {display_item}")

def fix_spreadsheet_encoding(input_file: str, output_file: str = None, 
                           file_type: str = 'auto') -> str:
    """
    Função principal para corrigir encoding de planilhas

    Args:
        input_file: Caminho do arquivo de entrada
        output_file: Caminho do arquivo de saída (opcional)
        file_type: Tipo do arquivo ('excel', 'csv', 'auto')

    Returns:
        str: Caminho do arquivo corrigido
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")

    fixer = FixEncodingSpreadsheet()

    # Detecta automaticamente o tipo de arquivo
    if file_type == 'auto':
        if input_file.lower().endswith(('.xlsx', '.xls')):
            file_type = 'excel'
        elif input_file.lower().endswith('.csv'):
            file_type = 'csv'
        else:
            raise ValueError("Tipo de arquivo não suportado. Use .xlsx, .xls ou .csv")

    # Processa o arquivo
    if file_type == 'excel':
        return fixer.fix_excel_file(input_file, output_file)
    elif file_type == 'csv':
        return fixer.fix_csv_file(input_file, output_file)
    else:
        raise ValueError("file_type deve ser 'excel' ou 'csv'")

# Exemplo de uso
if __name__ == "__main__":
    try:
        # Corrige o CSV 'dados_osc_PR_completo_corrigido.csv' por padrão
        arquivo_entrada = "data/dados_osc_PR_completo_corrigido.csv"
        arquivo_saida = "data/dados_osc_PR_completo_corrigido_utf8.csv"

        if not os.path.exists(arquivo_entrada):
            print(f"ERRO: Arquivo '{arquivo_entrada}' não encontrado!")
            print("Por favor, coloque o arquivo na pasta 'data' ou ajuste o caminho.")
        else:
            arquivo_saida = fix_spreadsheet_encoding(arquivo_entrada, arquivo_saida, file_type='csv')
            print(f"\nSUCESSO! Arquivo corrigido salvo como: {arquivo_saida}")

    except Exception as e:
        print(f"ERRO: {e}")
        input("Pressione Enter para continuar...")
