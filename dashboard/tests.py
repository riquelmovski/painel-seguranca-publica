from django.test import TestCase, Client
from django.urls import reverse

class DashboardViewsTestCase(TestCase):
    """
    Testes automatizados para garantir o funcionamento do Dashboard
    de Segurança Pública e suas rotas.
    """

    def setUp(self):
        self.client = Client()

    def test_pagina_inicial_status_code_200(self):
        """Verifica se a página inicial responde com código HTTP 200 (Sucesso)."""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)

    def test_template_utilizado(self):
        """Verifica se o template correto (dashboard/index.html) é renderizado."""
        response = self.client.get(reverse('dashboard:index'))
        self.assertTemplateUsed(response, 'dashboard/index.html')

    def test_presenca_das_metricas_no_contexto(self):
        """Verifica se todos os KPIs e gráficos solicitados estão presentes no contexto."""
        response = self.client.get(reverse('dashboard:index'))
        
        # Checa presença dos KPIs
        self.assertIn('total_cvli', response.context)
        self.assertIn('total_mandados', response.context)
        self.assertIn('total_transito', response.context)

        # Checa presença dos gráficos
        self.assertIn('grafico_barras', response.context)
        self.assertTrue('grafico_linha' in response.context or 'grafico_linhas' in response.context)

    def test_filtro_por_uf(self):
        """Verifica se a rota responde adequadamente ao filtro de estado."""
        response = self.client.get(reverse('dashboard:index') + '?uf=PB')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_cvli', response.context)

    def test_exportacao_csv(self):
        """Verifica se a rota de exportação gera um arquivo CSV com cabeçalhos corretos."""
        response = self.client.get(reverse('dashboard:exportar_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('attachment;', response['Content-Disposition'])
