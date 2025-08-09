import sqlite3
import os
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
import pandas as pd

def get_db_connection():
    """Retorna conexão com o banco SQLite"""
    db_path = os.path.join(settings.BASE_DIR, 'data', 'oscs_parana_novo.db')
    return sqlite3.connect(db_path)

def load_osc_data():
    """Carrega os dados do banco SQLite das OSCs"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM oscs", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Erro ao carregar dados do banco: {e}")
        return pd.DataFrame()

def get_oscs_por_municipio():
    """Retorna a contagem de OSCs por município"""
    try:
        conn = get_db_connection()
        query = """
            SELECT 
                edmu_nm_municipio as municipio,
                COUNT(*) as total_oscs
            FROM oscs 
            WHERE edmu_nm_municipio != ''
            GROUP BY edmu_nm_municipio
            ORDER BY edmu_nm_municipio
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict('records')
    except Exception as e:
        print(f"Erro ao obter contagem de OSCs por município: {e}")
        return []

def get_municipios_data(request):
    """API endpoint para retornar dados de OSCs por município"""
    dados = get_oscs_por_municipio()
    return JsonResponse({'data': dados})

def mapa_teste(request):
    """View para testar o mapa isoladamente"""
    return render(request, 'osc_dashboard/mapa_teste.html')

def get_filter_options():
    """Obtém as opções de filtro disponíveis do banco"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtém municípios únicos
        cursor.execute("SELECT DISTINCT edmu_nm_municipio FROM oscs WHERE edmu_nm_municipio != '' ORDER BY edmu_nm_municipio")
        municipios = [row[0] for row in cursor.fetchall()]
        
        # Obtém naturezas jurídicas únicas
        cursor.execute("SELECT DISTINCT natureza_juridica FROM oscs WHERE natureza_juridica != '' ORDER BY natureza_juridica")
        naturezas_juridicas = [row[0] for row in cursor.fetchall()]
        
        # Obtém total de registros
        cursor.execute("SELECT COUNT(*) FROM oscs")
        total_registros = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'municipios': municipios,
            'naturezas_juridicas': naturezas_juridicas,
            'total_registros': total_registros
        }
    except Exception as e:
        print(f"Erro ao obter opções de filtro: {e}")
        return {
            'municipios': [],
            'naturezas_juridicas': [],
            'total_registros': 0
        }

def dashboard(request):
    """View principal do dashboard"""
    filter_options = get_filter_options()

    context = {
        'municipios': filter_options['municipios'],  # Lista para contagem no template
        'municipios_json': json.dumps(filter_options['municipios']),  # JSON para JavaScript
        'naturezas_juridicas': filter_options['naturezas_juridicas'],
        'total_registros': filter_options['total_registros']
    }

    return render(request, 'osc_dashboard/dashboard.html', context)

@csrf_exempt
def export_data(request):
    """Exporta dados filtrados para Excel usando SQLite"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Parâmetros de filtro
            municipio = data.get('municipio', '')
            natureza_juridica = data.get('natureza_juridica', '')
            palavras_chave = data.get('palavras_chave', '')
            naturezas_ver = data.get('naturezas_ver', [])  # Mudança: agora são as naturezas que quer ver
            
            # Conecta ao banco
            conn = get_db_connection()
            
            # Constrói query SQL
            query = "SELECT * FROM oscs WHERE 1=1"
            params = []
            
            if municipio:
                # Separa os municípios e faz busca OR com igualdade exata
                municipios = [m.strip() for m in municipio.split(',') if m.strip()]
                if municipios:
                    municipio_conditions = []
                    for mun in municipios:
                        municipio_conditions.append("edmu_nm_municipio = ?")
                        params.append(mun)
                    query += f" AND ({' OR '.join(municipio_conditions)})"
            
            if natureza_juridica:
                # Separa as naturezas jurídicas e faz busca OR com igualdade exata
                naturezas = [n.strip() for n in natureza_juridica.split(',') if n.strip()]
                if naturezas:
                    natureza_conditions = []
                    for natureza in naturezas:
                        natureza_conditions.append("natureza_juridica = ?")
                        params.append(natureza)
                    query += f" AND ({' OR '.join(natureza_conditions)})"
            
            if palavras_chave:
                # Separa as palavras-chave e faz busca OR (OSC deve conter QUALQUER uma das palavras)
                keywords = [kw.strip() for kw in palavras_chave.split() if kw.strip()]
                if keywords:
                    keyword_conditions = []
                    for keyword in keywords:
                        keyword_conditions.append("nome LIKE ?")
                        params.append(f'%{keyword}%')
                    query += f" AND ({' OR '.join(keyword_conditions)})"
            
            # Filtra apenas as naturezas jurídicas selecionadas
            if naturezas_ver:
                placeholders = ','.join(['?' for _ in naturezas_ver])
                query += f" AND natureza_juridica IN ({placeholders})"
                params.extend(naturezas_ver)
            
            # Executa query
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()

            if df.empty:
                return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

            # Substitui NaN por string vazia para Excel
            df = df.fillna('')
            
            # Renomeia colunas para melhor visualização
            df_export = df.copy()
            df_export.columns = [
                'ID OSC', 'Nome', 'Email', 'Endereço', 'Telefone', 
                'Natureza Jurídica', 'Situação Cadastral', 'Código Município', 'Município'
            ]
            
            # Gera nome do arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'OSCs_Parana_{timestamp}.xlsx'
            
            # Cria resposta HTTP com arquivo Excel
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # Salva no Excel
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df_export.to_excel(writer, sheet_name='OSCs Paraná', index=False)
                
                # Ajusta largura das colunas
                worksheet = writer.sheets['OSCs Paraná']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return response
            
        except Exception as e:
            return JsonResponse({'error': f'Erro ao exportar dados: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def filter_data(request):
    """Filtra dados usando SQLite e retorna resultados em JSON"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Parâmetros de filtro
            municipio = data.get('municipio', '')
            natureza_juridica = data.get('natureza_juridica', '')
            palavras_chave = data.get('palavras_chave', '')
            naturezas_ver = data.get('naturezas_ver', [])  # Mudança: agora são as naturezas que quer ver
            page = data.get('page', 1)
            per_page = data.get('per_page', 50)
            
            # Conecta ao banco
            conn = get_db_connection()
            
            # Constrói query SQL para contagem total
            count_query = "SELECT COUNT(*) FROM oscs WHERE 1=1"
            params = []
            
            if municipio:
                # Separa os municípios e faz busca OR com igualdade exata
                municipios = [m.strip() for m in municipio.split(',') if m.strip()]
                if municipios:
                    municipio_conditions = []
                    for mun in municipios:
                        municipio_conditions.append("edmu_nm_municipio = ?")
                        params.append(mun)
                    count_query += f" AND ({' OR '.join(municipio_conditions)})"
            
            if natureza_juridica:
                # Separa as naturezas jurídicas e faz busca OR com igualdade exata
                naturezas = [n.strip() for n in natureza_juridica.split(',') if n.strip()]
                if naturezas:
                    natureza_conditions = []
                    for natureza in naturezas:
                        natureza_conditions.append("natureza_juridica = ?")
                        params.append(natureza)
                    count_query += f" AND ({' OR '.join(natureza_conditions)})"
            
            if palavras_chave:
                # Separa as palavras-chave e faz busca OR (OSC deve conter QUALQUER uma das palavras)
                keywords = [kw.strip() for kw in palavras_chave.split() if kw.strip()]
                if keywords:
                    keyword_conditions = []
                    for keyword in keywords:
                        keyword_conditions.append("nome LIKE ?")
                        params.append(f'%{keyword}%')
                    count_query += f" AND ({' OR '.join(keyword_conditions)})"
            
            # Filtra apenas as naturezas jurídicas selecionadas
            if naturezas_ver:
                placeholders = ','.join(['?' for _ in naturezas_ver])
                count_query += f" AND natureza_juridica IN ({placeholders})"
                params.extend(naturezas_ver)
            
            # Executa contagem
            cursor = conn.cursor()
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Constrói query para dados com paginação
            data_query = count_query.replace("SELECT COUNT(*)", "SELECT *")
            data_query += " LIMIT ? OFFSET ?"
            data_params = params + [per_page, (page - 1) * per_page]
            
            # Executa query de dados
            df = pd.read_sql_query(data_query, conn, params=data_params)
            conn.close()

            # Converte para lista de dicionários e trata NaN
            data_list = []
            for _, row in df.iterrows():
                row_dict = {}
                for col, value in row.items():
                    # Converte NaN para None
                    if pd.isna(value):
                        row_dict[col] = None
                    else:
                        row_dict[col] = value
                data_list.append(row_dict)
            
            return JsonResponse({
                'data': data_list,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Erro ao filtrar dados: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
