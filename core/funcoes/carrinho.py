from ..models import Carrinho, Produto
from django.db.models import OuterRef, Subquery

def delete_cart(id_cart, usuario):
        status = ''
        msg = ''
        resp = {}
        try:
            carrinho = Carrinho.objects.get(id=id_cart)
            pedido = carrinho.pedido
            enviado = carrinho.enviado
            if pedido or enviado:
                  msg = 'Infelizmente não é mais possível remover este pedido'
                  status = 'erro'
            else:
                  status = 'sucesso'
                  msg = 'Pedido removido com sucesso'
                  carrinho.delete()                   
                  dados = get_cart(usuario)
                  resp['dados'] = dados                  
        except Exception as e:
            status = 'erro'
            msg = str(e)
        resp['msg'] = msg
        resp['status'] = status
        return resp

def get_cart(usuario):                
        sub_carrinho = Produto.objects.filter(id=OuterRef('id_produto'))
        carrinho = Carrinho.objects.filter(nome_usuario=usuario, pedido=False).annotate(
                produto=Subquery(sub_carrinho.values('produto')),
                marca=Subquery(sub_carrinho.values('marca')),
                preco=Subquery(sub_carrinho.values('preco')),
                codigo=Subquery(sub_carrinho.values('codigo')),
                estoque=Subquery(sub_carrinho.values('estoque'))
        )       
        #dados = list(carrinho.values('nome_usuario', 'id_produto', 'pk',
        #                                    'update', 'produto', 'marca', 
        #                                    'preco', 'codigo', 'estoque')) 
        dados = list(carrinho.values())
        return dados