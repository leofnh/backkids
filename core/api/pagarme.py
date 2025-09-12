import requests
from ..models import Carrinho, Produto
from ..funcoes.carrinho import get_cart
def pagar_me(data):
    resp_item = data.get('item')
    valor_a_pagar = 0
    erros = []
    resp = {}
    for i in resp_item:     
        try:
            item = Carrinho.objects.get(id=i['pk'])
            qtde = i['quantidade']         
            item.quantidade = qtde
            item.save()
            produto = Produto.objects.get(id=item.id_produto)
            estoque = produto.estoque
            if estoque < 1:
                msg_erro = f"Infelizmente, o produto '{produto.produto}' não possui estoque suficiente (estoque atual: {produto.estoque}). A venda foi cancelada. Por favor, remova este item do pedido e tente novamente."
                erros.append({"message": msg_erro})
                #return {"status": 'erro', 'msg': f'O produto: {produto.produto} Não há estoque.'}
            valor_a_pagar += i['preco']
        except Exception as e:
            erros.append({"message": str(e)}) 
    if len(erros) > 0:
        resp['erros'] = erros
        resp['status'] = 'erros'
        resp['msg'] = 'Infelizmente não conseguimos concluir a sua venda, se persistir o problema entre em contato com a loja.'
        return resp
    else:
        valor_formatado = str(valor_a_pagar).replace(".", "")
        valor_total_int = int(valor_formatado) + 25 
        url = "https://api.pagar.me/core/v5/orders"
        #valor_total = data.get("total")
        telefone_completo = data.get('telefone').replace("(", "").replace(")", "").replace("-", "").strip()
        ddd = telefone_completo[:2]
        telefone = telefone_completo[3:]
        #valor_formatado = valor_total.replace("R$", "").replace(".", "").replace(",", "").strip()  
        payload = {
            "customer": {
                "phones": { "mobile_phone": {
                        "country_code": "55",
                        "area_code": ddd,
                        "number": telefone,
                    } },
                "name": f"{data.get('nome')}",
                "type": "individual",
                "email": f"{data.get('email')}",
                "document": f"{data.get('cpf')}",
                "document_type": "CPF",
                "gender": "male" # adicionar o sexo!
            },
            "code": "codigo",
            "items": [
                {
                    "amount": valor_total_int,
                    "description": "Venda Loja Store",
                    "quantity": 1,
                    "code": "12345"
                }
            ],
            "payments": [
                {
                    "credit_card": {
                        "card": {
                            "billing_address": {
                                "line_1": data.get('endereco'),
                                "zip_code": data.get('cep'),
                                "city": data.get('cidade'),
                                "state": data.get('estado'),
                                "country": "BR"
                            },
                            "number": data.get("numeroCartao"),
                            "holder_name": data.get("nomeTitular"),
                            "exp_month": data.get("expiraMes"),
                            "exp_year": data.get('expiraAno'),
                            "cvv": data.get('cvv'),
                        },
                        "statement_descriptor": "LOJA STORE",
                        "installments": data.get('parcelas')
                    },
                    "payment_method": "credit_card"

                }
            ]
        }
        # headers para teste da API do pagarme
        # headers = {
        #     "accept": "application/json",
        #     "content-type": "application/json",
        #     "authorization": "Basic c2tfdGVzdF83ODljNmYwMGY3MWU0NDU0YmM0ODc4OWQyMjhlZjhjZDpwa190ZXN0X3F3TkRKMTJzS1RvMFdlWEw="
        # }
        #sk_ce96548d607646b890f557dd4b1dfa7b
        headers = {
             "accept": "application/json",
             "content-type": "application/json",
             "authorization": "Basic c2tfY2U5NjU0OGQ2MDc2NDZiODkwZjU1N2RkNGIxZGZhN2I6QXVndXN0bzIwMzAh"
         }

        response = requests.post(url, json=payload, headers=headers)      
        resp_data = response.json()      
        #print(f"Olha o data ai: {resp_data}")
        try:
            transaction_status = resp_data['charges'][0]['last_transaction']['status']
            if transaction_status:                
                if transaction_status == 'captured':            
                    for i in resp_item:                
                        fin_pedido = Carrinho.objects.get(id=i['pk'])  
                        att_produto = Produto.objects.get(id=fin_pedido.id_produto)          
                        att_produto.estoque -= 1    
                        att_produto.save()
                        fin_pedido.pedido = True
                        fin_pedido.cpf = data.get('cpf')
                        fin_pedido.estado = data.get('estado')
                        fin_pedido.cidade = data.get('cidade')
                        fin_pedido.contato = data.get('contato')
                        fin_pedido.email = data.get('email')
                        fin_pedido.cep = data.get('cep')
                        fin_pedido.save()     
                            
                    usuario_name = item.nome_usuario
                    data_cart = get_cart(usuario_name)            
                    resp['status'] = 'sucesso'
                    resp['msg'] = 'Seu pagamento foi processado com sucesso! Agora é só acompanhar o seu pedido!' 
                    resp['dados'] = data_cart       
                else:                    
                    errors = resp_data['charges'][0]['last_transaction']['gateway_response']['errors']
                    resp['msg'] = 'Houve um erro no pagamento, tente novamente mais tarde.'
                    resp['status'] = 'erro'
                    for msg in errors:
                        erros.append(
                            {"message": msg['message']}
                        )
                        
                    resp['erros']= erros                   
            else:
                print("tem nao mano")
        except Exception as e:
            tem_erro = len(resp_data['errors'])
            if tem_erro > 0:
                errors = resp_data['errors']           
                for campo, msg, in errors.items():                    
                    for msg in msg:
                        erros.append(
                            {"message": msg}
                        )
                resp['msg'] = 'Houve um erro durante o pagamento.'
                resp['status'] = 'erro'               
                resp['erros'] = erros

            #print(f'Descobre ai qual que é {resp_data}')
            #print(f"Sera? {len(resp_data['errors'])}")
        
    return resp