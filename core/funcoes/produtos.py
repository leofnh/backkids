from ..models import Produto, ProdutoVendido, Notinha
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

def cadastrar(data):
    try:
        codigo = data.get('codigo', '')
        produto = data.get('produto', '')       
        existe = Produto.objects.filter(codigo=codigo)     
        hoje = datetime.today()
        preco = float(data.get('preco', '').replace(",", ".").replace("R$", ""))           
        custo = float(data.get('custo', '').replace(",", ".").replace("R$", ""))     
        unidades = int(data.get('estoque', 0))
        data['preco'] = preco
        data['custo'] = custo
        data['estoque'] = unidades      
        if existe:         
            #existe.update(**data)
            att_produto = Produto.objects.get(codigo=codigo)
            for field, value in data.items():               
                setattr(att_produto, field, value)
            att_produto.save()
            status = 'sucesso'
            msg = 'Produto atualizado com sucesso!'
        else:    
            data['cadastro'] = hoje          
            data['preco'] = preco         
            Produto.objects.create(**data)           
            status = 'sucesso'
            msg = 'Novo item cadastrado com sucesso!'
    except Exception as e:
        status = 'erro'
        msg = str(e)
        
    dados = Produto.objects.filter(estoque__gte=1)
    dados_json = list(dados.values())
    resp = {
        "status": status,
        "msg": msg,
        "dados": dados_json
    }
    return resp

def get_products():
    #produtos = Produto.objects.filter(estoque__gte=1)
    produtos = Produto.objects.all()
    return produtos

def vender_produto(data):
    resp = {}   
    data_hoje = date.today()
    data_7_vencimento = data_hoje + timedelta(days=7)
    status_codigo = ''
    erro_msg = ''
    lista_codigo = []
    tem_erro = False
    forma = data['forma']
    dados = data['data']    
    vendedor = data['vendedor']
    hoje = datetime.today()
    for i in dados:        
        precoFloat = i['preco'].replace(",", ".").replace("R", "").replace("$", "")
        produto = i['produto']
        codigo = i['codigo']
        marca = i['marca']
        tamanho = i['tamanho']
        preco = float(precoFloat)
        if forma == 'dinheiro' or forma == 'debito' or forma == 'pix':            
            preco = preco * 0.90
        unidades_vendida = int(i['qtde'])
        ref = i['ref']   
        if codigo:
            try:
                dados_codigo = Produto.objects.get(codigo=codigo)
                qtde = i['qtde']
                unidades = dados_codigo.estoque
                custo = dados_codigo.custo
                if qtde > unidades:
                    resp['status'] = 'erro'
                    tem_erro = True
                    erro_msg + 'Não existe estoque do produto {codigo} para registrar venda \n'
                    resp['msg'] = 'Houve um erro no estoque do produto, confirme se há estoque.'
                    resp['tem_erro'] = tem_erro
                    resp['erro_msg'] = erro_msg
                else:           
                    estoque_atual = unidades - unidades_vendida 
                    if estoque_atual >= 0:
                        ProdutoVendido.objects.create(
                            produto=produto,
                            marca=marca,
                            preco=preco,
                            custo=custo,
                            tamanho=tamanho,
                            codigo=codigo,
                            ref=ref,
                            unidades=unidades_vendida,
                            cadastro=hoje,
                            forma=forma,
                            vendedor=vendedor
                        )
                        dados_codigo.estoque = estoque_atual
                        dados_codigo.save()                        
                        status_codigo = 'sucesso'                
                    else:
                        status_codigo = 'erro'
                        tem_erro = True                    
                    codigos = {
                               "codigo" : codigo, 
                               "qtde": unidades_vendida, 
                               "code_status": status_codigo
                               }
                    lista_codigo.append(codigos)
                    resp['status'] = 'sucesso'
                    resp['msg'] = 'Venda realizada com sucesso!'
                    resp['tem_erro'] = tem_erro  
                                 
            except Exception as e:
                resp['msg'] = str(e)
                resp['status'] = 'erro'
                tem_erro = True
                resp['tem_erro'] = tem_erro
                erro_msg + f'Código: {codigo} \n {str(e)} \n'
                resp['erro_msg'] = erro_msg               
    
    if forma == 'crediario':                            
        parcelas = int(data['parcelas'])
        cliente = data['cliente']
        vencimento_str = data['data_vencimento']
        vencimento = datetime.strptime(vencimento_str, "%Y-%m-%d").date()
        valor_parcela_str = data['valor_parcela']
        valor_parcela_formated = float(valor_parcela_str.replace("R$", "").replace(".", "").replace(",", "."))
        for i in range(parcelas):
            vencimento_parcela = vencimento + relativedelta(months=i)
            Notinha.objects.create(cliente=cliente, vencimento=vencimento_parcela, 
                                    produto=codigo,cadastro=hoje, 
                                    valor=valor_parcela_formated)
        notas = Notinha.objects.filter(vencimento__lt=data_7_vencimento, 
                                   status='aberto').order_by("vencimento")
        notas_json = list(notas.values('cliente', 'vencimento', 'valor', 'produto', 'status', 'id'))
        resp['notinhas'] = notas_json
    resp['lista_codigo'] = lista_codigo
    vendas_hoje = ProdutoVendido.objects.filter(cadastro__date=data_hoje).aggregate(
        total=Sum('preco')
    )['total']
    resp['venda_hoje'] = vendas_hoje
    return resp
        

def update_produtos(codigo, value, produto):
    resp = {}
    try:
        dados = Produto.objects.get(codigo=codigo)
        #estoque = dados.estoque
        #estoque_atual = estoque + value
        if value < 0:
            resp['msg'] = 'Erro: O estoque do produto não pode ser menor que 0, verifique seu estoque.'
            resp['status'] = 'erro'
        else:
            resp['status'] = 'sucesso'
            resp['msg'] = 'Estoque atualizado.'
            resp['updateValue'] = value
            dados.estoque = value
            dados.produto = produto
            dados.save()        

    except Exception as e:
        resp['msg'] = f'Houve um erro {str(e)}'
        resp['status'] = 'erro'
    return resp
    resp = {}
    try:
        dados = Produto.objects.get(codigo=codigo)
        estoque = dados.estoque
        estoque_atual = estoque + value
        if estoque_atual < 0:
            resp['msg'] = 'Erro: O estoque do produto não pode ser menor que 0, verifique seu estoque.'
            resp['status'] = 'erro'
        else:
            resp['status'] = 'sucesso'
            resp['msg'] = 'Estoque atualizado.'
            resp['updateValue'] = estoque_atual
            dados.estoque = estoque_atual
            dados.save()        

    except Exception as e:
        resp['msg'] = f'Houve um erro {str(e)}'
        resp['status'] = 'erro'
    return resp


def update_venda(data):
    resp = {}
    hoje = date.today()
    data_7_vencimento = hoje + timedelta(days=7)
    try:
        id_nota = data.get('id', '')
        dados = Notinha.objects.get(id=id_nota)
        dados.status = 'pago'
        dados.save()

        notas = Notinha.objects.filter(vencimento__lt=data_7_vencimento, 
                                   status='aberto').order_by("vencimento")
        notas_json = list(notas.values('cliente', 'vencimento', 'valor', 'produto', 'status', 'id'))
        resp['status'] = 'sucesso'
        resp['msg'] = 'A nota foi paga com sucesso!'
        resp['dados'] = notas_json
    except Exception as e:
        resp['status'] = 'erro'
        resp['msg'] = f'Houve um erro durante a atualização: {str(e)}'
    
    return resp