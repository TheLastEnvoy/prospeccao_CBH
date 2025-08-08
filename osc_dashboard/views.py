import pandas as pd
import os
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

def load_osc_data():
    """Carrega os dados do CSV das OSCs"""
    csv_path = os.path.join(settings.BASE_DIR, 'data', 'dados_osc_PR_completo.csv')
    
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        return df
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def get_filter_options():
    """Obtém as opções de filtro disponíveis"""
    df = load_osc_data()
    
    if df.empty:
        return {
            'municipios': [],
            'naturezas_juridicas': [],
            'total_registros': 0
        }
    
    # Remove valores vazios e obtém valores únicos
    municipios = sorted(df['edmu_nm_municipio'].dropna().unique().tolist())
    naturezas_juridicas = sorted(df['natureza_juridica'].dropna().unique().tolist())
    
    return {
        'municipios': municipios,
        'naturezas_juridicas': naturezas_juridicas,
        'total_registros': len(df)
    }

def dashboard(request):
    """View principal do dashboard"""
    filter_options = get_filter_options()
    
    context = {
        'municipios': filter_options['municipios'],
        'naturezas_juridicas': filter_options['naturezas_juridicas'],
        'total_registros': filter_options['total_registros']
    }
    
    return render(request, 'osc_dashboard/dashboard.html', context)

@csrf_exempt
def export_data(request):
    """Exporta dados filtrados para Excel"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Parâmetros de filtro
            municipio = data.get('municipio', '')
            natureza_juridica = data.get('natureza_juridica', '')
            palavras_chave = data.get('palavras_chave', '')
            naturezas_ignorar = data.get('naturezas_ignorar', [])
            
            # Carrega dados
            df = load_osc_data()
            
            if df.empty:
                return JsonResponse({'error': 'Dados não encontrados'}, status=404)
            
            # Aplica filtros
            if municipio:
                df = df[df['edmu_nm_municipio'].str.contains(municipio, case=False, na=False)]
            
            if natureza_juridica:
                df = df[df['natureza_juridica'].str.contains(natureza_juridica, case=False, na=False)]
            
            if palavras_chave:
                df = df[df['nome'].str.contains(palavras_chave, case=False, na=False)]
            
            # Remove naturezas jurídicas ignoradas
            if naturezas_ignorar:
                for natureza in naturezas_ignorar:
                    df = df[~df['natureza_juridica'].str.contains(natureza, case=False, na=False)]
            
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
    """Filtra dados e retorna resultados em JSON"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Parâmetros de filtro
            municipio = data.get('municipio', '')
            natureza_juridica = data.get('natureza_juridica', '')
            palavras_chave = data.get('palavras_chave', '')
            naturezas_ignorar = data.get('naturezas_ignorar', [])
            page = data.get('page', 1)
            per_page = data.get('per_page', 50)
            
            # Carrega dados
            df = load_osc_data()
            
            if df.empty:
                return JsonResponse({
                    'data': [],
                    'total': 0,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': 0
                })
            
            # Aplica filtros
            if municipio:
                df = df[df['edmu_nm_municipio'].str.contains(municipio, case=False, na=False)]
            
            if natureza_juridica:
                df = df[df['natureza_juridica'].str.contains(natureza_juridica, case=False, na=False)]
            
            if palavras_chave:
                df = df[df['nome'].str.contains(palavras_chave, case=False, na=False)]
            
            # Remove naturezas jurídicas ignoradas
            if naturezas_ignorar:
                for natureza in naturezas_ignorar:
                    df = df[~df['natureza_juridica'].str.contains(natureza, case=False, na=False)]
            
            # Paginação
            total = len(df)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            df_page = df.iloc[start_idx:end_idx]
            
            # Converte para lista de dicionários
            data_list = df_page.to_dict('records')
            
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
