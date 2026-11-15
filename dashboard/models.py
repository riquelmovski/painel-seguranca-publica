from django.db import models

class OcorrenciaSeguranca(models.Model):
    """
    Modelo representativo dos registros do Banco VDE de Segurança Pública 2025.
    Permite consultas indexadas e persistência relacional no banco de dados do Django.
    """
    uf = models.CharField('UF', max_length=2, db_index=True)
    municipio = models.CharField('Município', max_length=150, db_index=True)
    evento = models.CharField('Indicador / Evento', max_length=255, db_index=True)
    data_referencia = models.DateField('Data de Referência', null=True, blank=True, db_index=True)
    agente = models.CharField('Agente / Força Policial', max_length=100, null=True, blank=True)
    arma = models.CharField('Arma / Meio Empregado', max_length=100, null=True, blank=True)
    faixa_etaria = models.CharField('Faixa Etária', max_length=50, null=True, blank=True)
    feminino = models.IntegerField('Vítimas Femininas', default=0)
    masculino = models.IntegerField('Vítimas Masculinas', default=0)
    nao_informado = models.IntegerField('Gênero Não Informado', default=0)
    total_vitima = models.IntegerField('Total de Vítimas', default=0)
    total = models.IntegerField('Total de Ocorrências', default=0)
    abrangencia = models.CharField('Abrangência', max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'Ocorrência de Segurança Pública'
        verbose_name_plural = 'Ocorrências de Segurança Pública'
        indexes = [
            models.Index(fields=['uf', 'evento']),
            models.Index(fields=['data_referencia']),
        ]

    def __str__(self):
        return f"{self.evento} - {self.municipio}/{self.uf} ({self.total} ocorrências)"
