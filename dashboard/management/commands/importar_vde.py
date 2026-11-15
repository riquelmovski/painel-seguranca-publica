"""
Comando customizado do Django para carga de dados em massa (ETL).
Uso no terminal: python manage.py importar_vde
"""

from django.core.management.base import BaseCommand
from pathlib import Path
import pandas as pd
from dashboard.models import OcorrenciaSeguranca

class Command(BaseCommand):
    help = 'Lê o arquivo data/BancoVDE 2025.xlsx com Pandas e insere no banco via bulk_create'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limite',
            type=int,
            default=None,
            help='Limitar a quantidade de linhas a importar (útil para testes rápidos)'
        )

    def handle(self, *args, **options):
        limite = options['limite']
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        caminho_arquivo = base_dir / 'data' / 'BancoVDE 2025.xlsx'

        if not caminho_arquivo.exists():
            caminho_arquivo = Path('data/BancoVDE 2025.xlsx')

        self.stdout.write(self.style.NOTICE(f"Iniciando leitura do arquivo: {caminho_arquivo}..."))
        
        # Leitura do Excel com Pandas
        df = pd.read_excel(caminho_arquivo)
        
        if limite:
            df = df.head(limite)
            self.stdout.write(self.style.WARNING(f"Modo teste: limitando importação a {limite} registros."))

        self.stdout.write(f"Total de registros a processar: {len(df):,}".replace(",", "."))

        # Tratamento de datas
        if pd.api.types.is_numeric_dtype(df['data_referencia']):
            df['data_referencia'] = pd.to_datetime(df['data_referencia'], unit='D', origin='1899-12-30')
        else:
            df['data_referencia'] = pd.to_datetime(df['data_referencia'], errors='coerce')

        # Limpeza de números
        for col in ['feminino', 'masculino', 'nao_informado', 'total_vitima', 'total']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # Montagem dos objetos para bulk_create (em lotes de 5.000 para poupar memória)
        batch_size = 5000
        objetos = []
        total_inseridos = 0

        self.stdout.write("Inserindo registros no banco de dados...")

        for row in df.itertuples(index=False):
            data_val = row.data_referencia.date() if pd.notnull(row.data_referencia) else None
            
            obj = OcorrenciaSeguranca(
                uf=str(row.uf)[:2] if pd.notnull(row.uf) else '',
                municipio=str(row.municipio)[:150] if pd.notnull(row.municipio) else '',
                evento=str(row.evento)[:255] if pd.notnull(row.evento) else '',
                data_referencia=data_val,
                agente=str(row.agente)[:100] if pd.notnull(row.agente) else None,
                arma=str(row.arma)[:100] if pd.notnull(row.arma) else None,
                faixa_etaria=str(row.faixa_etaria)[:50] if pd.notnull(row.faixa_etaria) else None,
                feminino=row.feminino,
                masculino=row.masculino,
                nao_informado=row.nao_informado,
                total_vitima=row.total_vitima,
                total=row.total,
                abrangencia=str(row.abrangencia)[:50] if hasattr(row, 'abrangencia') and pd.notnull(row.abrangencia) else None,
            )
            objetos.append(obj)

            if len(objetos) >= batch_size:
                OcorrenciaSeguranca.objects.bulk_create(objetos)
                total_inseridos += len(objetos)
                self.stdout.write(f"  -> {total_inseridos:,} registros inseridos...".replace(",", "."))
                objetos = []

        if objetos:
            OcorrenciaSeguranca.objects.bulk_create(objetos)
            total_inseridos += len(objetos)

        self.stdout.write(self.style.SUCCESS(f"Importação concluída com sucesso! Total: {total_inseridos:,} registros.".replace(",", ".")))
