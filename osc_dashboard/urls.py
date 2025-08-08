from django.urls import path
from . import views

app_name = 'osc_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('export/', views.export_data, name='export_data'),
    path('filter/', views.filter_data, name='filter_data'),
    path('mapa-teste/', views.mapa_teste, name='mapa_teste'),
    path('municipios-data/', views.get_municipios_data, name='municipios_data'),
]
