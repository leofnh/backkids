import openpyxl
from ..models import Produto, Cliente
from .produtos import get_products

def import_products(file):
    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    last_row = sheet.max_row
    for row in sheet.iter_rows(min_row=2, max_row=last_row, min_col=3, max_col=11):
        marca = row[0].value.strip()
        tamanho = row[1].value.strip()
        preco = row[2].value
        data = row[3].value
        qtde = row[4].value
        codigo = row[5].value.strip()
        ref = row[6].value.strip()
        custo = row[7].value
        ja_existe = Produto.objects.filter(codigo=codigo)
        if ja_existe:
            ja_existe.update(preco=preco)
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

def import_cliente(file):
    wb = openpyxl.load_workbook(file)
    sheet = wb.active
    last_row = sheet.max_row
    for row in sheet.iter_rows(min_row=2, max_row=last_row, min_col=2, max_col=7):
        nome = row[0].value
        email = row[1].value
        telefone = row[2].value
        data = row[3].value
        cidade = row[4].value
        estado = row[5].value
        ja_existe = Cliente.objects.filter(email=email)
        if ja_existe:
            ja_existe.update(telefone=telefone)
        else:            
            try:
                Cliente.objects.create(
                        nome=nome,
                        email=email,
                        telefone=telefone,
                        cidade=cidade,
                        estado=estado,
                        cadastro=data
                    )
            except Exception as e:
                print(str(e))

      

    
    