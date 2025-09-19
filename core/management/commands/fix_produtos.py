from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from core.models import Produto


class Command(BaseCommand):
    help = 'Corrige produtos com ref e codigo vazios/nulos de forma otimizada'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Tamanho do batch para processamento (padrão: 1000)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações (apenas mostra o que seria feito)'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando correção de produtos...')
        )
        self.stdout.write(f'Batch size: {batch_size}')
        self.stdout.write(f'Dry run: {"Sim" if dry_run else "Não"}')
        
        try:
            # Conta total de produtos
            total_produtos = Produto.objects.count()
            self.stdout.write(f'Total de produtos: {total_produtos}')
            
            # Conta problemas
            refs_vazias = Produto.objects.filter(
                Q(ref__isnull=True) | Q(ref__exact='') | Q(ref__regex=r'^\s*$')
            ).count()
            
            codigos_vazios = Produto.objects.filter(
                Q(codigo__isnull=True) | Q(codigo__exact='') | Q(codigo__regex=r'^\s*$')
            ).count()
            
            self.stdout.write(f'REFs vazias/nulas: {refs_vazias}')
            self.stdout.write(f'Códigos vazios/nulos: {codigos_vazios}')
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('DRY RUN - Nenhuma alteração será feita')
                )
                return
            
            updated_refs = 0
            updated_codigos = 0
            
            with transaction.atomic():
                # 1. Corrige REFs vazias em lote
                self.stdout.write('Corrigindo REFs vazias...')
                count_refs = Produto.objects.filter(
                    Q(ref__isnull=True) | Q(ref__exact='') | Q(ref__regex=r'^\s*$')
                ).update(ref='SEM-REFERENCIA')
                updated_refs += count_refs
                
                # 2. Limpa REFs existentes
                self.stdout.write('Limpando REFs existentes...')
                refs_para_limpar = Produto.objects.exclude(
                    Q(ref__isnull=True) | Q(ref__exact='') | Q(ref__regex=r'^\s*$')
                ).exclude(ref='SEM-REFERENCIA')
                
                processed = 0
                for produto in refs_para_limpar.iterator(chunk_size=batch_size):
                    ref_limpa = produto.ref.strip().upper()
                    if produto.ref != ref_limpa:
                        Produto.objects.filter(id=produto.id).update(ref=ref_limpa)
                        updated_refs += 1
                    
                    processed += 1
                    if processed % batch_size == 0:
                        self.stdout.write(f'REFs processadas: {processed}')
                
                # 3. Corrige códigos vazios
                self.stdout.write('Corrigindo códigos vazios...')
                codigos_vazios_qs = Produto.objects.filter(
                    Q(codigo__isnull=True) | Q(codigo__exact='') | Q(codigo__regex=r'^\s*$')
                )
                
                processed = 0
                for produto in codigos_vazios_qs.iterator(chunk_size=batch_size):
                    novo_codigo = f'COD-{produto.id}'
                    Produto.objects.filter(id=produto.id).update(codigo=novo_codigo)
                    updated_codigos += 1
                    
                    processed += 1
                    if processed % batch_size == 0:
                        self.stdout.write(f'Códigos vazios processados: {processed}')
                
                # 4. Limpa códigos existentes
                self.stdout.write('Limpando códigos existentes...')
                codigos_para_limpar = Produto.objects.exclude(
                    Q(codigo__isnull=True) | Q(codigo__exact='') | Q(codigo__regex=r'^\s*$')
                )
                
                processed = 0
                for produto in codigos_para_limpar.iterator(chunk_size=batch_size):
                    codigo_limpo = produto.codigo.strip().upper()
                    if produto.codigo != codigo_limpo:
                        Produto.objects.filter(id=produto.id).update(codigo=codigo_limpo)
                        updated_codigos += 1
                    
                    processed += 1
                    if processed % batch_size == 0:
                        self.stdout.write(f'Códigos processados: {processed}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Correção concluída com sucesso!\n'
                    f'Total de produtos: {total_produtos}\n'
                    f'REFs atualizadas: {updated_refs}\n'
                    f'Códigos atualizados: {updated_codigos}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante a correção: {str(e)}')
            )
            raise e