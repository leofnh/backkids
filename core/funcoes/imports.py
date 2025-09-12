import openpyxl
from ..models import Produto
from .produtos import get_products
def import_products(file):
    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    last_row = sheet.max_row
    for row in sheet.iter_rows(min_row=2, max_row=last_row, min_col=3, max_col=11):
        marca = row[0].value
        tamanho = row[1].value
        preco = row[2].value
        data = row[3].value
        qtde = row[4].value
        codigo = row[5].value
        ref = row[6].value
        custo = row[7].value
        #status = row[8].value      
        ja_existe = Produto.objects.filter(codigo=codigo)
        if ja_existe:
            pass
        else:            
            try:
                Produto.objects.create(
                        preco=preco,
                        tamanho=tamanho,
                        marca=marca,
                        ref=ref,
                        custo=custo,
                        estoque=qtde,
                        codigo=codigo,
                        cadastro=data
                    )
            except Exception as e:
                print(str(e))
    
    dados = get_products()
    dados_json = list(dados.values('codigo', 'estoque', 'marca', 'custo', 
                                       'preco', 'ref', 'tamanho'))
     
    
    return dados_json
      

    
    