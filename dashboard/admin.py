from django.contrib import admin
from .models import OcorrenciaSeguranca

@admin.register(OcorrenciaSeguranca)
class OcorrenciaSegurancaAdmin(admin.ModelAdmin):
    """
    Configuração avançada do Django Admin para consulta e auditoria
    dos registros de segurança pública do Brasil 2025.
    """
    list_display = (
        'evento',
        'municipio',
        'uf',
        'data_referencia',
        'total',
        'total_vitima',
        'feminino',
        'masculino',
        'arma',
    )
    list_filter = ('uf', 'evento', 'data_referencia')
    search_fields = ('municipio', 'evento', 'uf')
    ordering = ('-data_referencia', '-total')
    list_per_page = 25
    date_hierarchy = 'data_referencia'
