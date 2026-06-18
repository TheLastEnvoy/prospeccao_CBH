import sqlite3
import unicodedata
import os
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
import pandas as pd

def get_municipio_cbh_map():
    """Retorna dict {municipio: 'CBH Nome 1 / CBH Nome 2'} para enriquecimento dos dados"""
    cbh_map = get_cbh_data()
    municipio_cbh = {}
    for cbh_id, cbh in cbh_map.items():
        for mun in cbh['municipios']:
            if mun not in municipio_cbh:
                municipio_cbh[mun] = cbh['nome']
            else:
                municipio_cbh[mun] += f" / {cbh['nome']}"
    return municipio_cbh

def get_db_connection():
    """Retorna conexão com o banco SQLite"""
    db_path = os.path.join(settings.BASE_DIR, 'data', 'oscs_parana_novo.db')
    return sqlite3.connect(db_path)

def get_cbh_data():
    """Carrega o mapeamento CBH → municípios do banco de dados preservando a ordem de inserção"""
    cbh_map = {}  # {cbh_id: {'nome': str, 'municipios': list}}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.cbh_id, c.cbh_nome, cm.municipio "
            "FROM cbh c JOIN cbh_municipio cm ON c.cbh_id = cm.cbh_id "
            "ORDER BY c.cbh_id, cm.rowid"
        )
        for cbh_id, cbh_nome, municipio in cursor.fetchall():
            if cbh_id not in cbh_map:
                cbh_map[cbh_id] = {'nome': cbh_nome, 'municipios': []}
            cbh_map[cbh_id]['municipios'].append(municipio)
        conn.close()
    except Exception as e:
        print(f"Erro ao carregar dados CBH do banco: {e}")
    return cbh_map

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

def mapa_outorgas(request):
    """View do mapa interativo de outorgas"""
    classification_fields = [
        {
            'value': 'outorgas_IAT_agrupado_CBH_COMITE',
            'label': 'Comitê de bacia',
        },
        {
            'value': 'outorgas_IAT_agrupado_ATV_MACRO',
            'label': 'Atividade macro',
        },
        {
            'value': 'bac_nome',
            'label': 'Bacia hidrográfica',
        },
    ]
    return render(
        request,
        'osc_dashboard/mapa_outorgas.html',
        {
            'classification_fields': classification_fields,
        },
    )

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

        # Obtém situações cadastrais únicas
        cursor.execute("SELECT DISTINCT situacao_cadastral FROM oscs WHERE situacao_cadastral != '' ORDER BY situacao_cadastral")
        situacoes_cadastrais = [row[0] for row in cursor.fetchall()]

        # Obtém total de registros
        cursor.execute("SELECT COUNT(*) FROM oscs")
        total_registros = cursor.fetchone()[0]

        conn.close()

        return {
            'municipios': municipios,
            'naturezas_juridicas': naturezas_juridicas,
            'situacoes_cadastrais': situacoes_cadastrais,
            'total_registros': total_registros
        }
    except Exception as e:
        print(f"Erro ao obter opções de filtro: {e}")
        return {
            'municipios': [],
            'naturezas_juridicas': [],
            'situacoes_cadastrais': [],
            'total_registros': 0
        }

def dashboard(request):
    """View principal do dashboard"""
    filter_options = get_filter_options()
    cbh_map = get_cbh_data()

    context = {
        'municipios': filter_options['municipios'],
        'municipios_json': json.dumps(filter_options['municipios']),
        'naturezas_juridicas': filter_options['naturezas_juridicas'],
        'situacoes_cadastrais': filter_options['situacoes_cadastrais'],
        'total_registros': filter_options['total_registros'],
        'cbh_list': [{'cbh_id': k, 'cbh_nome': v['nome']} for k, v in cbh_map.items()],
        'cbh_data_json': json.dumps(cbh_map),
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
            palavras_excluir = data.get('palavras_excluir', '')
            situacao_cadastral = data.get('situacao_cadastral', '')
            
            # Conecta ao banco
            conn = get_db_connection()
            
            # Constrói query SQL
            query = "SELECT id_osc, nome, email, endereco, telefone, natureza_juridica, situacao_cadastral, edmu_cd_municipio, edmu_nm_municipio FROM oscs WHERE 1=1"
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
                # Busca por palavras separadas por espaço ou vírgula, ignorando acentos e case
                def normalize(text):
                    return unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('ASCII').lower()

                import re
                keywords = [kw.strip() for kw in re.split(r'[ ,]+', palavras_chave) if kw.strip()]
                # Pré-filtra no SQL com LIKE (sem normalização de acentos) para reduzir
                # os dados trazidos para memória; a filtragem precisa com normalização
                # de acentos é feita depois em Python sobre o subconjunto já reduzido.
                if keywords:
                    keyword_conditions = []
                    for keyword in keywords:
                        keyword_conditions.append("nome LIKE ?")
                        params.append(f'%{keyword}%')
                    query += f" AND ({' OR '.join(keyword_conditions)})"

            if palavras_excluir:
                # Separa as palavras para excluir e faz busca NOT LIKE
                exclude_keywords = [kw.strip() for kw in palavras_excluir.split() if kw.strip()]
                if exclude_keywords:
                    exclude_conditions = []
                    for keyword in exclude_keywords:
                        exclude_conditions.append("nome NOT LIKE ?")
                        params.append(f'%{keyword}%')
                    query += f" AND ({' AND '.join(exclude_conditions)})"

            if situacao_cadastral:
                # Separa as situações cadastrais e faz busca OR com igualdade exata
                situacoes = [s.strip() for s in situacao_cadastral.split(',') if s.strip()]
                if situacoes:
                    situacao_conditions = []
                    for situacao in situacoes:
                        situacao_conditions.append("situacao_cadastral = ?")
                        params.append(situacao)
                    query += f" AND ({' OR '.join(situacao_conditions)})"
            
            # Filtra apenas as naturezas jurídicas selecionadas
            if naturezas_ver:
                placeholders = ','.join(['?' for _ in naturezas_ver])
                query += f" AND natureza_juridica IN ({placeholders})"
                params.extend(naturezas_ver)
            
            # Executa query
            df = pd.read_sql_query(query, conn, params=params)
            # Filtra por palavras-chave no Python, ignorando acentos e case
            if palavras_chave:
                keywords_norm = [normalize(kw) for kw in keywords]
                mask = df['nome'].apply(lambda x: any(kw in normalize(x) for kw in keywords_norm))
                df = df[mask]
            conn.close()

            if df.empty:
                return JsonResponse({'error': 'Nenhum dado encontrado'}, status=404)

            # Adiciona coluna CBH com base no município
            municipio_cbh = get_municipio_cbh_map()
            df['cbh'] = df['edmu_nm_municipio'].map(lambda m: municipio_cbh.get(str(m), '-') if m else '-')

            # Substitui NaN por string vazia para Excel
            df = df.fillna('')
            
            # Renomeia colunas para melhor visualização
            df_export = df.copy()
            if len(df_export.columns) == 10:
                df_export.columns = [
                    'ID OSC', 'Nome', 'Email', 'Endereço', 'Telefone',
                    'Natureza Jurídica', 'Situação Cadastral', 'Código Município', 'Município', 'Comitê de Bacia'
                ]
            else:
                return JsonResponse({'error': f'Erro: número de colunas inesperado ({len(df_export.columns)}). Não foi possível exportar.'}, status=500)
            
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
            palavras_excluir = data.get('palavras_excluir', '')  # Novo: palavras para excluir
            situacao_cadastral = data.get('situacao_cadastral', '')  # Novo: situação cadastral
            naturezas_ver = data.get('naturezas_ver', [])  # Mudança: agora são as naturezas que quer ver
            page = data.get('page', 1)
            per_page = data.get('per_page', 50)
            
            # Conecta ao banco
            conn = get_db_connection()
            
            # Constrói a cláusula WHERE separadamente para reusar em COUNT e SELECT
            where_clause = "WHERE 1=1"
            params = []
            
            if municipio:
                # Separa os municípios e faz busca OR com igualdade exata
                municipios = [m.strip() for m in municipio.split(',') if m.strip()]
                if municipios:
                    municipio_conditions = []
                    for mun in municipios:
                        municipio_conditions.append("edmu_nm_municipio = ?")
                        params.append(mun)
                    where_clause += f" AND ({' OR '.join(municipio_conditions)})"
            
            if natureza_juridica:
                # Separa as naturezas jurídicas e faz busca OR com igualdade exata
                naturezas = [n.strip() for n in natureza_juridica.split(',') if n.strip()]
                if naturezas:
                    natureza_conditions = []
                    for natureza in naturezas:
                        natureza_conditions.append("natureza_juridica = ?")
                        params.append(natureza)
                    where_clause += f" AND ({' OR '.join(natureza_conditions)})"
            
            if palavras_chave:
                # Separa as palavras-chave e faz busca OR (OSC deve conter QUALQUER uma das palavras)
                keywords = [kw.strip() for kw in palavras_chave.split() if kw.strip()]
                if keywords:
                    keyword_conditions = []
                    for keyword in keywords:
                        keyword_conditions.append("nome LIKE ?")
                        params.append(f'%{keyword}%')
                    where_clause += f" AND ({' OR '.join(keyword_conditions)})"

            if palavras_excluir:
                # Separa as palavras para excluir e faz busca NOT LIKE
                exclude_keywords = [kw.strip() for kw in palavras_excluir.split() if kw.strip()]
                if exclude_keywords:
                    exclude_conditions = []
                    for keyword in exclude_keywords:
                        exclude_conditions.append("nome NOT LIKE ?")
                        params.append(f'%{keyword}%')
                    where_clause += f" AND ({' AND '.join(exclude_conditions)})"

            if situacao_cadastral:
                # Separa as situações cadastrais e faz busca OR com igualdade exata
                situacoes = [s.strip() for s in situacao_cadastral.split(',') if s.strip()]
                if situacoes:
                    situacao_conditions = []
                    for situacao in situacoes:
                        situacao_conditions.append("situacao_cadastral = ?")
                        params.append(situacao)
                    where_clause += f" AND ({' OR '.join(situacao_conditions)})"
            
            # Filtra apenas as naturezas jurídicas selecionadas
            if naturezas_ver:
                placeholders = ','.join(['?' for _ in naturezas_ver])
                where_clause += f" AND natureza_juridica IN ({placeholders})"
                params.extend(naturezas_ver)
            
            # Executa contagem reutilizando a mesma cláusula WHERE
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM oscs {where_clause}", params)
            total = cursor.fetchone()[0]
            
            # Constrói query para dados com paginação
            data_query = f"SELECT * FROM oscs {where_clause} ORDER BY edmu_nm_municipio LIMIT ? OFFSET ?"
            data_params = params + [per_page, (page - 1) * per_page]
            
            # Executa query de dados
            df = pd.read_sql_query(data_query, conn, params=data_params)
            conn.close()

            # Converte para lista de dicionários e trata NaN
            municipio_cbh = get_municipio_cbh_map()
            data_list = []
            for _, row in df.iterrows():
                row_dict = {}
                for col, value in row.items():
                    # Converte NaN para None
                    if pd.isna(value):
                        row_dict[col] = None
                    else:
                        row_dict[col] = value
                # Adiciona campo CBH com base no município
                mun = row_dict.get('edmu_nm_municipio') or ''
                row_dict['cbh'] = municipio_cbh.get(mun, '-')
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
