from django.urls import path
from . import views

app_name = 'osc_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('export/', views.export_data, name='export_data'),
    path('filter/', views.filter_data, name='filter_data'),
]
