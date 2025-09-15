from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import DadosUser
from django.db.models import OuterRef, Subquery, F, FloatField, ExpressionWrapper
from .funcoes.genpdf import generate_receipt_pdf
from .funcoes.produtos import cadastrar, get_products, vender_produto, update_produtos, update_venda
from .funcoes.client import cadastrar_cliente, get_cliente, update_clients
from .funcoes.dashbaord import dados_dash
from .funcoes.imports import import_products, import_products_chunked
from .api.pagarme import pagar_me
from .funcoes.carrinho import delete_cart
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import (Carrinho, Produto, FotoProduto, FotoCapaSite, AboutUs, CondicionalCliente, 
                     ProdutoCondicional, Cliente)
from django.http import HttpResponse

import json
# Create your views here.
@csrf_exempt
def home(request):    
    resp = {
        "status": 'sucesso',
        "msg": 'Json retornado com sucesso!'
    }    
    return JsonResponse(resp)
@csrf_exempt
def get_links_capa(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        resp = {
            "status": 'erro',
            "msg": 'Houve um erro inesperado. Não houve ação.'
        }
        try:
            FotoCapaSite.objects.create(url=url)
            dados = FotoCapaSite.objects.all().values()
            resp = {
                "status": 'sucesso',
                "msg": 'Imagem cadastrada com sucesso!',
                "dados": list(dados)
            }
        except Exception as e:
            resp = {
                'status' : 'erro',
                'msg': f'Erro durante o cadastro da imagem de capa, {e}'
            }        
        return JsonResponse(resp)
    elif request.method == 'GET':
        fotos = FotoCapaSite.objects.all().values()
        resp = {
            "status": 'sucesso',
            "msg": '',
            "dados": list(fotos)
        }
        return JsonResponse(resp)
    elif request.method == 'DELETE':
        resp = {
            "status": 'erro',
            "msg": 'Nenhuma ação foi executada.'
        }
        try:
            data = json.loads(request.body)
            id_foto = data.get('id_foto')
            if not id_foto:
                resp['msg'] = 'Imagem não encontrada.'
            else:                
                existe = FotoCapaSite.objects.filter(id=id_foto)
                if existe:
                    existe.delete()
                    dados = FotoCapaSite.objects.all().values()
                    resp['dados'] = list(dados)
                    resp['msg'] = 'Imagem excluída com sucesso!'
                    resp['status'] = 'sucesso'
                else:
                    resp['msg'] = 'Imagem não localizada.'
        except Exception as e:
            resp = {
                "status": 'erro',
                "msg": f"Houve um erro: {str(e)}"
            }
        return JsonResponse(resp)
    else:
        resp = {
            "status": 'erro',
            "msg": 'Methodo invalido.'
        }
        return JsonResponse(resp)

@csrf_exempt
def produtos_loja(request):
    if request.method == 'GET':
        data = get_products()
        # fazer subquery para capturar todos os produtos de mesma referência.
        #dados = data.filter(loja=True)
        refs_com_loja_true = data.filter(loja=True, estoque__gt=0).values_list('ref', flat=True).distinct()
        dados = data.filter(ref__in=refs_com_loja_true, estoque__gt=0).order_by('sequencia')
        dados_json = list(dados.values())
        resp = {
            "dados": dados_json
        }
        return JsonResponse(resp)

@csrf_exempt
def produtos(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        resp = cadastrar(data)
        return JsonResponse(resp)
    elif request.method == 'GET':
        dados = get_products()
        dados_json = list(dados.values())
        resp = {
            "dados": dados_json,
        }
        return JsonResponse(resp)
    elif request.method == 'PUT':
        data = json.loads(request.body.decode("utf-8"))
        value = data.get('newEstoque', '')
        codigo = data.get('codigo', '')
        produto = data.get('produto', '')
        resp = update_produtos(codigo, value, produto)
        return JsonResponse(resp)

@csrf_exempt
def clientes(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        resp = cadastrar_cliente(data)     
        return JsonResponse(resp)
    elif request.method == 'GET':
        dados = get_cliente()
        dados_json = list(dados.values('nome', 'cpf', 'idt', 'dn', 
                                       'rua', 'bairro', 'cidade',
                                       'numero', 'sapato', 'roupa', 'cadastro', 'id', 'telefone'
                                       ))
     
        resp = {
            "dados": dados_json,
            
        }
        return JsonResponse(resp)
    elif request.method == 'PUT':
        data = json.loads(request.body.decode("utf-8"))     
        resp = update_clients(data)  
        return JsonResponse(resp)

@csrf_exempt
def venda(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        resp = vender_produto(data)
        return JsonResponse(resp)
    elif request.method == 'GET':
        dados = get_cliente()
        dados_json = list(dados.values('nome', 'cpf', 'idt', 'dn', 
                                       'rua', 'bairro', 'cidade',
                                       'numero', 'sapato', 'roupa', 'cadastro'
                                       ))
     
        resp = {
            "dados": dados_json,
            
        }
        return JsonResponse(resp)
    elif request.method == 'PUT':
        dados = json.loads(request.body.decode("utf-8"))
        resp = update_venda(dados)
        return JsonResponse(resp)

@csrf_exempt
def dashboard(request):
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        dados = dados_dash()        
        return JsonResponse(dados)
    elif request.method == 'PUT':
        pass

@csrf_exempt
def login_app(request):
    resp = {}
    if request.method == 'POST':
        try:
            data =  json.loads(request.body.decode("utf-8"))            
            usuario = data.get('user', '')
            senha = data.get('password', '')
            if usuario and senha:
                logando = authenticate(username=usuario, password=senha)
                if logando: 
                    login(request, logando)
                    resp['status'] = 'sucesso'
                    sub_dados = DadosUser.objects.filter(id_usuario=OuterRef('id')).values('cargo')[:1]
                    dados_user = User.objects.filter(username=usuario).annotate(
                        cargo=Subquery(sub_dados)
                    )
                    dados_json = list(dados_user.values('username', 'first_name', 
                                                        'last_name', 'id', 'cargo'))
                    resp['dados_user'] = dados_json
                    return JsonResponse(resp)
                else:
                    resp['status'] = 'erro'
                    resp['msg'] = 'Erro inesperado, tente logar novamente.'
                    return JsonResponse(resp)
            else: 
                resp['status'] = 'erro'
                resp['msg'] = 'Preencha os campos de usuário e senha corretamente.'
                return JsonResponse(resp)
        except Exception as e:
            resp['status'] = 'erro'
            resp['msg'] = f'Houve um erro inesperado, informe um adm: {str(e)}'
            return JsonResponse(resp)  
        
    elif request.method == 'GET':              
        resp = {
            "status" : 'erro',
            "msg": 'Peça um administrador se precisar cadastrar.'
        }
        return JsonResponse(resp)
        
    elif request.method == 'PUT':
        resp = {
            "status" : 'erro',
            "msg": 'Peça um administrador se precisar atualizar seu cadastro.'
        }
        return JsonResponse(resp)

@csrf_exempt
def import_product(request):
    resp = {}
    if request.method == 'POST':   
        try:
            file = request.FILES.get('file', None)
            
            if not file:
                resp['status'] = 'erro'
                resp['msg'] = 'Nenhum arquivo foi enviado.'
                return JsonResponse(resp)
            
            # Importa produtos em lotes
            resultado = import_products(file, batch_size=50)
            
            if resultado.get('success', False):
                stats = resultado['statistics']
                resp['status'] = 'sucesso'
                resp['msg'] = f'Importação concluída! {stats["created"]} criados, {stats["updated"]} atualizados.'
                
                if stats['errors'] > 0:
                    resp['msg'] += f' {stats["errors"]} produtos com erro.'
                    
                resp['dados'] = resultado['data']
                resp['statistics'] = stats
            else:
                resp['status'] = 'erro'
                resp['msg'] = 'Falha na importação dos produtos.'
                
        except Exception as e:
            print(f"Erro na importação: {str(e)}")
            resp['status'] = 'erro' 
            resp['msg'] = 'Erro interno durante a importação. Tente com um arquivo menor.'
            
    else:
        resp['status'] = 'erro'
        resp['msg'] = 'Método de requisição inválido.'
        
    return JsonResponse(resp)

@csrf_exempt
def import_product_with_progress(request):
    """
    Importação de produtos com streaming de progresso
    Para arquivos muito grandes (>1000 produtos)
    """
    if request.method == 'POST':
        try:
            file = request.FILES.get('file', None)
            
            if not file:
                return JsonResponse({
                    'status': 'erro',
                    'msg': 'Nenhum arquivo foi enviado.'
                })
            
            # Função generator que retorna progresso
            def generate_progress():
                yield "data: " + json.dumps({'status': 'iniciando', 'msg': 'Iniciando importação...'}) + "\n\n"
                
                try:
                    for progress in import_products_chunked(file, chunk_size=20):
                        yield "data: " + json.dumps({
                            'status': 'progresso',
                            'progress': progress
                        }) + "\n\n"
                        
                    yield "data: " + json.dumps({
                        'status': 'concluido',
                        'msg': 'Importação finalizada com sucesso!'
                    }) + "\n\n"
                    
                except Exception as e:
                    yield "data: " + json.dumps({
                        'status': 'erro',
                        'msg': f'Erro durante a importação: {str(e)}'
                    }) + "\n\n"
            
            response = StreamingHttpResponse(
                generate_progress(),
                content_type='text/plain'
            )
            response['Cache-Control'] = 'no-cache'
            response['Connection'] = 'keep-alive'
            
            return response
            
        except Exception as e:
            return JsonResponse({
                'status': 'erro',
                'msg': f'Erro interno: {str(e)}'
            })
    
    return JsonResponse({
        'status': 'erro',
        'msg': 'Método não permitido.'
    })

@csrf_exempt
def meus_pedidos(request, usuario):
    resp = {}
    if int(usuario) == 0:
        resp['status'] = 'erro'
        resp['msg'] = 'Erro ao carregar dados.'
        resp['dados'] = []
        return JsonResponse(resp)

    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        sub_carrinho = Produto.objects.filter(id=OuterRef('id_produto'))
        carrinho = Carrinho.objects.filter(nome_usuario=usuario).annotate(
            produto=Subquery(sub_carrinho.values('produto')),
            marca=Subquery(sub_carrinho.values('marca')),
            preco=ExpressionWrapper(
                    Subquery(sub_carrinho.values('preco')) * F('quantidade'),
                    output_field=FloatField()
                ),
            codigo=Subquery(sub_carrinho.values('codigo')),
            estoque=Subquery(sub_carrinho.values('estoque'))
        )
        resp['status'] = 'sucesso'
        resp['msg'] = 'Dados carregado com sucesso'
        resp['dados'] = list(carrinho.values())     
        return JsonResponse(resp)

    else:
        resp['status'] = 'erro'
        resp['msg'] = 'metodo invalido'
        return JsonResponse(resp)

@csrf_exempt
def carrinholoja(request, usuario):
    resp = {
        "status": 'erro',
        "msg": 'Erro inesperado, por favor tente novamente.'
    }
    if request.method == 'POST':
        try:
            data =  json.loads(request.body.decode("utf-8"))             
            for produto in data['id_produto']:                
                resp_data = {
                    "nome_usuario": data['nome_usuario'],
                    "id_produto": produto['id_produto'],
                    "quantidade": data['quantidade']
                }                
                ja_tem = Carrinho.objects.filter(id_produto=produto['id_produto'], nome_usuario=usuario, 
                                                 pedido=False)
                if ja_tem:                    
                    ja_tem.update(quantidade=F("quantidade") + data['quantidade'])
                else:
                    Carrinho.objects.create(**resp_data)
            #return JsonResponse(resp)  
            #Carrinho.objects.create(**data)            
            sub_carrinho = Produto.objects.filter(id=OuterRef('id_produto'))
            carrinho = Carrinho.objects.filter(nome_usuario=usuario, pedido=False).annotate(
                produto=Subquery(sub_carrinho.values('produto')),
                marca=Subquery(sub_carrinho.values('marca')),
                preco=ExpressionWrapper(
                    Subquery(sub_carrinho.values('preco')) * F('quantidade') + 25,
                    output_field=FloatField()
                ),
                codigo=Subquery(sub_carrinho.values('codigo')),
                estoque=Subquery(sub_carrinho.values('estoque'))
            )
            resp['status'] = 'sucesso'
            resp['msg'] = 'Produto adicionado ao carrinho com sucesso!'
            #resp['dados'] = list(carrinho.values('nome_usuario', 'id_produto', 'pk',
            #                                  'update', 'produto', 'marca', 'preco', 'codigo', 'quantidade',
            #                                  'estoque'))     
            resp['dados'] = list(carrinho.values())        
        except Exception as e:
            resp['msg'] = f'Erro: {str(e)}'
        
    elif request.method == 'GET':
        #data =  json.loads(request.body.decode("utf-8"))        
        sub_carrinho = Produto.objects.filter(id=OuterRef('id_produto'))
        if int(usuario) == 1:
            carrinho = Carrinho.objects.filter(nome_usuario=usuario, pedido=False).annotate(
            produto=Subquery(sub_carrinho.values('produto')),
            marca=Subquery(sub_carrinho.values('marca')),
            preco=ExpressionWrapper(
                    Subquery(sub_carrinho.values('preco')) * F('quantidade'),
                    output_field=FloatField()
                ),
            codigo=Subquery(sub_carrinho.values('codigo')),
            estoque=Subquery(sub_carrinho.values('estoque'))
        )
        else:
            carrinho = Carrinho.objects.filter(nome_usuario=usuario, pedido=False).annotate(
            produto=Subquery(sub_carrinho.values('produto')),
            marca=Subquery(sub_carrinho.values('marca')),
            preco=ExpressionWrapper(
                    Subquery(sub_carrinho.values('preco')) * F('quantidade'),
                    output_field=FloatField()
                ),
            codigo=Subquery(sub_carrinho.values('codigo')),
            estoque=Subquery(sub_carrinho.values('estoque'))
        )        
        resp['status'], resp['msg'] = 'sucesso', 'Dados carregado com sucesso!'
        #resp['dados'] = list(carrinho.values('nome_usuario', 'id_produto', 'pk',
        #                                      'update', 'produto', 'marca', 'preco', 'codigo', 'quantidade', 
        #                                      'estoque'))   
        resp['dados'] = list(carrinho.values())       
    else:        
        resp['msg'] = 'Metodo invalido'
    
    return JsonResponse(resp)

@csrf_exempt
def send_image_product(request):
    resp = {
        "status": 'erro',
        "msg": 'Houve um erro inesperado, tente novamente.'
    }
    if request.method == 'POST':
        #data =  json.loads(request.body.decode("utf-8")) 
        url = request.POST.get('url')
        id_produto = request.POST.get('id_produto')
        data = {
            "url": url,
            "id_produto": id_produto
        }
        try:
            FotoProduto.objects.create(**data)
            resp['msg'] = 'Imagem atualizada com sucesso.'
            resp['status'] = 'sucesso'
            dados = FotoProduto.objects.all()
            dados_list = list(dados.values())
            resp['dados'] = dados_list
        except Exception as e:
            resp['msg'] = f'Erro: {str(e)}'
    elif request.method == 'GET':
        dados = FotoProduto.objects.all()
        dados_list = list(dados.values())
        resp['status'] = 'sucesso'
        resp['msg'] = 'Dados carregado com sucesso!'
        resp['dados'] = dados_list
    else:
        resp['msg'] = 'Metodo invalido'        

    return JsonResponse(resp)

@csrf_exempt
def api_cadastro(request):
    if request.method == 'POST':
        resp = {}
        data = json.loads(request.body.decode("utf-8")) 
        username = data.get('caduser')
        password = data.get('cadpassword')
        telefone = data.get('telefone')
        cargo = data.get('cargo')      
        ja_existe = User.objects.filter(username=username)
        if ja_existe:
            resp['status'] = 'erro'
            resp['msg'] = 'Este usuário já é cadastrado em nosso banco de dados!'
        else:
            try:
                criar_user = User.objects.create_user(username, username, password)
                criar_user.first_name = telefone
                criar_user.save()
                dados_user = User.objects.get(username=username)
                id_user = dados_user.id
                DadosUser.objects.create(
                    id_usuario=id_user,
                    nome_usuario=username,
                    cargo=cargo
                )
                dados_do_dash = dados_dash()         
                resp['dados'] = dados_do_dash
                resp['status'] = 'sucesso'
                resp['msg'] = 'Usuário criado com sucesso!'
            except Exception as e:
                resp['status'] = 'erro'
                resp['msg'] = f"Houve um erro durante seu cadastro, {str(e)}"

        return JsonResponse(resp)    
    else:
        return JsonResponse(
            {"status": 'erro',
            "msg": "Tentativa invalida."}
        )


@csrf_exempt
def api_del_cart(request):
    resp = {}
    if request.method == 'POST':
        # data =  json.loads(request.body.decode("utf-8"))       
        # id_cart  = data.get('id_cart') 
        # usuario = data.get('usuario')        
        id_cart = int(request.POST.get('id_cart'))
        usuario = request.POST.get('usuario')
        del_cart = delete_cart(id_cart, usuario)
        return JsonResponse(del_cart)
    else:
        resp['status'] = 'erro'
        resp['msg'] = 'metodo invalido'
    
    return JsonResponse(resp)

@csrf_exempt
def aboutus(request):
    if request.method == 'POST':
        page = request.POST.get('aboutus', '')
        resp = {
            "status": 'sucesso',
            "msg": 'Página atualizada com sucesso!'
        }
        try:
            AboutUs.objects.update_or_create(id=1, defaults={"page": page})
            dados = AboutUs.objects.filter(id=1).values()
            resp['dados'] = list(dados) 
        except Exception as e:
            resp['msg'] = f'Erro {e}'
            resp['status'] = 'erro'
        return JsonResponse(resp)
    if request.method == 'GET':
        resp = {
            "status" : 'sucesso',
        }
        try: 
            dados = AboutUs.objects.filter(id=1).values()
            resp['dados'] = list(dados)
        except Exception as e:
            resp['msg'] = f'Erro: {str(e)}'
        
        return JsonResponse(resp)

@csrf_exempt
def produto_condicional(request):
    resp = {
        "status" : 'erro',
        "msg": 'Houve um erro inesperado.'
    }
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        try:
            aberto = CondicionalCliente.objects.filter(cliente=cpf, aberto=True)
            if aberto:
                resp['msg'] = 'Este cliente já tem uma condicional em aberto, adicione produtos à ela.'
            else:
                CondicionalCliente.objects.create(cliente=cpf)
                resp['msg'] = 'Condicional aberta com sucesso!'
                resp['status'] = 'sucesso'
        except Exception as e:
            resp['msg'] = f"Houve um erro durante o cadastro. {str(e)}"
        
        sub_dados = Cliente.objects.filter(cpf=OuterRef('cliente'))
        dados = CondicionalCliente.objects.filter(aberto=True).annotate(
            nome=Subquery(sub_dados.values('nome'))
        )
        resp['dados'] = list(dados.values())

    elif request.method == 'GET':
        sub_dados = Cliente.objects.filter(cpf=OuterRef('cliente'))
        sub_produtos = Produto.objects.filter(codigo=OuterRef('produto'))
        sub_produtos_cond = CondicionalCliente.objects.filter(id=OuterRef('condicional'))

        dados = CondicionalCliente.objects.filter(aberto=True).annotate(
            nome=Subquery(sub_dados.values('nome')),            
        )
        produtos = ProdutoCondicional.objects.filter(condicional__in=dados.values_list('id', flat=True)).annotate(
            nome=Subquery(sub_produtos.values('produto')),
            preco=Subquery(sub_produtos.values('preco')),
            ref=Subquery(sub_produtos.values('ref')),
            cpf=Subquery(sub_produtos_cond.values('cliente')),
            
        )
        resp['dados'] = list(dados.values())
        resp['dados_produtos'] = list(produtos.values())
        resp['status'] = 'sucesso'
    
    return JsonResponse(resp)

@csrf_exempt
def add_produto_cond(request):
    resp = {
        "status" : 'erro',
        "msg": 'Houve um erro inesperado, tente novamente.'
    }
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        condicional = request.POST.get('condicional')
        try:
            existe_codigo = ProdutoCondicional.objects.filter(produto=codigo, condicional=condicional).exists()
            if existe_codigo:
                resp['msg'] = 'Este produto já foi adicionado à condicional.'
            else:
                existe_produto = Produto.objects.filter(codigo=codigo).exists()
                if not existe_produto:
                    resp['msg'] = 'Não existe este produto cadastrado.'
                    return JsonResponse(resp)
                ProdutoCondicional.objects.create(produto=codigo, condicional=condicional)
                resp['msg'] = 'Produto adicionado com sucesso.'
                resp['status'] = 'sucesso'
                sub_produtos = Produto.objects.filter(codigo=OuterRef('produto'))
                dados = CondicionalCliente.objects.filter(aberto=True)
                produtos = ProdutoCondicional.objects.filter(
                    condicional__in=dados.values_list('id', flat=True)
                    ).annotate(
                    nome=Subquery(sub_produtos.values('produto')),
                    preco=Subquery(sub_produtos.values('preco')),
                    ref=Subquery(sub_produtos.values('ref')),
                ).values()
                resp['dados_produtos'] = list(produtos)
        except Exception as e: 
            resp['msg'] = f'Erro inesperado: {str(e)}'
    
    return JsonResponse(resp)

@csrf_exempt
def del_img_link(request):
    resp = {
        "status" : 'erro',
        "msg": "Houve um erro inesperado."
    }
    if request.method == 'POST':
        id_img = request.POST.get('id')
        try:
            FotoProduto.objects.filter(id=id_img).delete()
            dados = FotoProduto.objects.all()
            dados_list = list(dados.values())
            resp['status'] = 'sucesso'
            resp['msg'] = 'Imagem deletada com sucesso!'
            resp['dados'] = dados_list
        except Exception as e:
            resp['msg'] = f"Houve um erro: {str(e)}"
        except FotoProduto.DoesNotExist:
            resp['msg'] = f'Este objeto não foi localizado.'

    return JsonResponse(resp)


@csrf_exempt
def api_pagar_me(request):
    resp = {}
    if request.method == 'POST':
        try:
            data =  json.loads(request.body.decode("utf-8")) 
            resp = pagar_me(data)            
            return JsonResponse(resp)
        except Exception as e:
            resp['status'] = 'erro'
            resp['msg'] = str(e)
    else:
        resp['status'] = 'erro'
        resp['msg'] = 'Metodo invalido'
    
   

    return JsonResponse(resp)

def print_receipt_view(request, sale_id):   
    pdf = generate_receipt_pdf(sale_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="recibo_{sale_id}.pdf"'
    response.write(pdf)
    return response


@csrf_exempt
def admin_produtos_sequencia(request):
    """
    View para gerenciar sequência de produtos no painel administrativo
    Produtos ativos: sem paginação (todos carregados para organização)
    Produtos inativos: com paginação para performance
    """
    if request.method == 'GET':
        try:
            from django.core.paginator import Paginator
            from django.db.models import Q
            
            # Parâmetros de paginação (apenas para produtos inativos)
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            search = request.GET.get('search', '').strip()
            
            # Query base
            produtos_query = Produto.objects.filter(estoque__gte=1)
            
            # Aplica filtros de busca se fornecidos
            if search:
                # Busca por código exato, referências similares e nome
                produtos_query = produtos_query.filter(
                    Q(codigo__iexact=search) |  # Código exato
                    Q(ref__icontains=search) |   # Referência contém o termo
                    Q(produto__icontains=search) | # Nome do produto contém o termo
                    Q(marca__icontains=search)   # Marca contém o termo
                ).distinct()
            
            # Agrupa produtos por referência para evitar duplicatas
            produtos = produtos_query.values(
                'id', 'produto', 'marca', 'ref', 'sequencia', 'loja', 
                'estoque', 'preco', 'codigo', 'descricao'
            ).order_by('sequencia', 'ref')
            
            produtos_agrupados = {}
            for produto in produtos:
                ref = produto['ref']
                if ref not in produtos_agrupados:
                    produtos_agrupados[ref] = produto
                else:
                    # Mantém o produto com maior estoque ou mais recente
                    if produto['estoque'] > produtos_agrupados[ref]['estoque']:
                        produtos_agrupados[ref] = produto
            
            # Separa produtos ativos e inativos
            produtos_lista = list(produtos_agrupados.values())
            produtos_ativos = [p for p in produtos_lista if p['loja']]
            produtos_inativos = [p for p in produtos_lista if not p['loja']]
            
            # PRODUTOS ATIVOS: Todos sem paginação (para organização de sequência)
            produtos_ativos_ordenados = sorted(produtos_ativos, key=lambda x: x['sequencia'])
            
            # PRODUTOS INATIVOS: Com paginação para performance
            paginator = Paginator(produtos_inativos, page_size)
            
            # Verifica se a página solicitada é válida
            if page > paginator.num_pages and paginator.num_pages > 0:
                page = paginator.num_pages
            if page < 1:
                page = 1
                
            produtos_inativos_paginados = paginator.get_page(page) if paginator.num_pages > 0 else []
            
            resp = {
                "status": 'sucesso',
                "produtos_ativos": produtos_ativos_ordenados,  # TODOS os ativos
                "produtos_inativos": list(produtos_inativos_paginados),  # Inativos paginados
                "pagination": {
                    "current_page": page,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "items_per_page": page_size,
                    "has_next": produtos_inativos_paginados.has_next() if produtos_inativos_paginados else False,
                    "has_previous": produtos_inativos_paginados.has_previous() if produtos_inativos_paginados else False,
                    "next_page": produtos_inativos_paginados.next_page_number() if produtos_inativos_paginados and produtos_inativos_paginados.has_next() else None,
                    "previous_page": produtos_inativos_paginados.previous_page_number() if produtos_inativos_paginados and produtos_inativos_paginados.has_previous() else None
                },
                "totals": {
                    "ativos": len(produtos_ativos),
                    "inativos": len(produtos_inativos),
                    "total": len(produtos_lista)
                },
                "search_term": search
            }
            return JsonResponse(resp)
            
        except Exception as e:
            resp = {
                'status': 'erro',
                'msg': f'Erro ao buscar produtos: {str(e)}'
            }
            return JsonResponse(resp)
    
    else:
        resp = {
            'status': 'erro',
            'msg': 'Método não permitido'
        }
        return JsonResponse(resp)

@csrf_exempt
def admin_atualizar_sequencia(request):
    """
    View para atualizar sequência de produtos
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            produtos = data.get('produtos', [])
            
            for produto_data in produtos:
                produto_id = produto_data.get('id')
                nova_sequencia = produto_data.get('sequencia')
                
                # Atualiza todos os produtos com a mesma referência
                produto = Produto.objects.get(id=produto_id)
                Produto.objects.filter(ref=produto.ref).update(sequencia=nova_sequencia)
            
            resp = {
                "status": 'sucesso',
                "msg": 'Sequência atualizada com sucesso!'
            }
            return JsonResponse(resp)
            
        except Exception as e:
            resp = {
                'status': 'erro',
                'msg': f'Erro ao atualizar sequência: {str(e)}'
            }
            return JsonResponse(resp)
    
    else:
        resp = {
            'status': 'erro',
            'msg': 'Método não permitido'
        }
        return JsonResponse(resp)

@csrf_exempt
def admin_toggle_loja(request):
    """
    View para ativar/desativar produto na loja
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            produto_id = data.get('id')
            status_loja = data.get('loja')
            
            # Atualiza todos os produtos com a mesma referência
            produto = Produto.objects.get(id=produto_id)
            Produto.objects.filter(ref=produto.ref).update(loja=status_loja)
            
            status_text = 'ativado' if status_loja else 'desativado'
            resp = {
                "status": 'sucesso',
                "msg": f'Produto {status_text} na loja com sucesso!'
            }
            return JsonResponse(resp)
            
        except Exception as e:
            resp = {
                'status': 'erro',
                'msg': f'Erro ao atualizar status: {str(e)}'
            }
            return JsonResponse(resp)
    
    else:
        resp = {
            'status': 'erro',
            'msg': 'Método não permitido'
        }
        return JsonResponse(resp)
