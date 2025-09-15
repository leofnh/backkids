import openpyxl
import time
from django.db import transaction
from ..models import Produto
from .produtos import get_products
def import_products(file, batch_size=50):
    """
    Importa produtos de planilha Excel processando em lotes para evitar timeout
    
    Args:
        file: Arquivo Excel
        batch_size: Tamanho do lote (padrão: 50 produtos por vez)
    
    Returns:
        dict: Resultado da importação com estatísticas
    """
    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    last_row = sheet.max_row
    
    # Contadores para estatísticas
    total_rows = last_row - 1  # Exclui cabeçalho
    processed = 0
    created = 0
    updated = 0
    errors = 0
    
    print(f"Iniciando importação de {total_rows} produtos em lotes de {batch_size}")
    
    # Processa em lotes
    batch_data = []
    
    for row_num, row in enumerate(sheet.iter_rows(min_row=2, max_row=last_row, min_col=3, max_col=11), 2):
        marca = row[0].value
        tamanho = row[1].value
        preco = row[2].value
        data = row[3].value
        qtde = row[4].value
        codigo = row[5].value
        ref = row[6].value
        custo = row[7].value
        
        # Validações básicas
        if not codigo or not preco:
            print(f"Linha {row_num}: Dados obrigatórios faltando (codigo ou preço)")
            errors += 1
            continue
            
        batch_data.append({
            'marca': marca,
            'tamanho': tamanho,
            'preco': preco,
            'data': data,
            'qtde': qtde,
            'codigo': codigo,
            'ref': ref,
            'custo': custo,
            'row_num': row_num
        })
        
        # Processa o lote quando atingir o tamanho definido
        if len(batch_data) >= batch_size:
            batch_result = process_batch(batch_data)
            created += batch_result['created']
            updated += batch_result['updated'] 
            errors += batch_result['errors']
            processed += len(batch_data)
            
            print(f"Lote processado: {processed}/{total_rows} produtos ({(processed/total_rows)*100:.1f}%)")
            
            # Sleep para não sobrecarregar o sistema
            time.sleep(0.5)  # 500ms entre lotes
            
            batch_data = []  # Reset do lote
    
    # Processa o último lote (se houver dados restantes)
    if batch_data:
        batch_result = process_batch(batch_data)
        created += batch_result['created']
        updated += batch_result['updated']
        errors += batch_result['errors']
        processed += len(batch_data)
        
    print(f"Importação concluída: {created} criados, {updated} atualizados, {errors} erros")
    
    # Retorna estatísticas e dados atualizados
    dados = get_products()
    dados_json = list(dados.values('codigo', 'estoque', 'marca', 'custo', 
                                       'preco', 'ref', 'tamanho'))
     
    return {
        'success': True,
        'statistics': {
            'total_processed': processed,
            'created': created,
            'updated': updated,
            'errors': errors
        },
        'data': dados_json
    }

def process_batch(batch_data):
    """
    Processa um lote de produtos usando transação para performance
    
    Args:
        batch_data: Lista de dicionários com dados dos produtos
        
    Returns:
        dict: Estatísticas do processamento do lote
    """
    created = 0
    updated = 0
    errors = 0
    
    try:
        with transaction.atomic():
            for item in batch_data:
                try:
                    # Verifica se produto já existe
                    produto_existente = Produto.objects.filter(codigo=item['codigo']).first()
                    
                    if produto_existente:
                        # Atualiza produto existente
                        produto_existente.preco = item['preco']
                        produto_existente.estoque = item['qtde'] if item['qtde'] else produto_existente.estoque
                        produto_existente.save()
                        updated += 1
                    else:
                        # Cria novo produto
                        Produto.objects.create(
                            preco=item['preco'],
                            tamanho=item['tamanho'],
                            marca=item['marca'],
                            ref=item['ref'],
                            custo=item['custo'],
                            estoque=item['qtde'] if item['qtde'] else 0,
                            codigo=item['codigo'],
                            cadastro=item['data']
                        )
                        created += 1
                        
                except Exception as e:
                    print(f"Erro na linha {item['row_num']}: {str(e)}")
                    errors += 1
                    
    except Exception as e:
        print(f"Erro na transação do lote: {str(e)}")
        errors += len(batch_data)
    
    return {
        'created': created,
        'updated': updated,
        'errors': errors
    }

def import_products_chunked(file, chunk_size=20):
    """
    Versão alternativa para arquivos muito grandes - processa em chunks menores
    
    Args:
        file: Arquivo Excel
        chunk_size: Tamanho do chunk (padrão: 20 produtos por vez)
        
    Returns:
        generator: Yields progresso da importação
    """
    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    last_row = sheet.max_row
    
    total_rows = last_row - 1
    processed = 0
    created = 0
    updated = 0
    errors = 0
    
    chunk_data = []
    
    for row_num, row in enumerate(sheet.iter_rows(min_row=2, max_row=last_row, min_col=3, max_col=11), 2):
        marca = row[0].value
        tamanho = row[1].value
        preco = row[2].value
        data = row[3].value
        qtde = row[4].value
        codigo = row[5].value
        ref = row[6].value
        custo = row[7].value
        
        if not codigo or not preco:
            errors += 1
            continue
            
        chunk_data.append({
            'marca': marca,
            'tamanho': tamanho,
            'preco': preco,
            'data': data,
            'qtde': qtde,
            'codigo': codigo,
            'ref': ref,
            'custo': custo,
            'row_num': row_num
        })
        
        if len(chunk_data) >= chunk_size:
            # Processa o chunk
            chunk_result = process_batch(chunk_data)
            created += chunk_result['created']
            updated += chunk_result['updated']
            errors += chunk_result['errors']
            processed += len(chunk_data)
            
            # Yield do progresso
            progress = {
                'processed': processed,
                'total': total_rows,
                'percentage': (processed / total_rows) * 100,
                'created': created,
                'updated': updated,
                'errors': errors,
                'status': 'processing'
            }
            yield progress
            
            # Sleep menor para chunks menores
            time.sleep(0.2)
            chunk_data = []
    
    # Processa chunk final
    if chunk_data:
        chunk_result = process_batch(chunk_data)
        created += chunk_result['created']
        updated += chunk_result['updated']
        errors += chunk_result['errors']
        processed += len(chunk_data)
    
    # Yield final
    yield {
        'processed': processed,
        'total': total_rows,
        'percentage': 100,
        'created': created,
        'updated': updated,
        'errors': errors,
        'status': 'completed'
    }
      

    
    