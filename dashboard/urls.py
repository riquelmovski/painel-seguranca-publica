from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('estado/<str:uf>/', views.detalhe_estado, name='detalhe_estado'),
    path('exportar/', views.exportar_csv, name='exportar_csv'),
    path('api/geojson/estados/', views.malha_estados_geojson, name='geojson_estados'),
]
