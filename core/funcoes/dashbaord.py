from ..models import ProdutoVendido, Notinha, Cliente, DadosUser
from django.db.models import Sum, OuterRef, FloatField, Subquery, F, Q
from django.db.models.functions import Coalesce
from datetime import date, timedelta
from django.contrib.auth.models import User


def dados_dash():
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    ano_anterior = ''
    clientes = Cliente.objects.all()
    data_7_vencimento = hoje + timedelta(days=7)
    mes_atual = hoje.month
    mes_anterior = mes_atual - 1
    dados = ProdutoVendido.objects.all()
    vendas_hoje = dados.filter(cadastro__date=hoje).aggregate(total=Sum('preco'))['total']
    vendas_ontem = dados.filter(cadastro__date=ontem).aggregate(total=Sum('preco'))['total'] 
    formas_distintas = dados.exclude(forma="").values('forma').distinct()
    contagem_formas = {}
    for forma in formas_distintas:
        forma_nome = forma['forma']
        contagem_formas[forma_nome] = dados.filter(forma=forma_nome).count()

    total_pagamentos = sum(contagem_formas.values())
    percentuais_formas = [
    {
        'forma': forma.title(),
        'percentual': round((count / total_pagamentos) * 100, 2)
    }
    for forma, count in contagem_formas.items()    ]

    #percentuais_formas = {forma: (count / total_pagamentos) * 100 for forma, count in contagem_formas.items()}
    notas = Notinha.objects.filter(vencimento__lt=data_7_vencimento, 
                                   status='aberto').order_by("vencimento")
    notas_json = list(notas.values('cliente', 'vencimento', 'valor', 'produto', 'status', 'id'))
    venda_mes_atual = dados.filter(
        cadastro__month=mes_atual
        ).aggregate(
            total=Sum('preco')
        )['total']
    venda_mes_anterior = dados.filter(
        cadastro__month=mes_anterior
        ).aggregate(
            total=Sum('preco')
        )['total']
    cliente_mes_atual = clientes.filter(cadastro__month=mes_atual).count()
    cliente_mes_anterior = clientes.filter(cadastro__month=mes_anterior).count()    
    #users = User.objects.exclude(username="admin")
    # foi removido 'unidades'
    subquery_atual = dados.filter(
        Q(cadastro__month=mes_atual, cadastro__year=hoje.year) & Q(vendedor=OuterRef('id'))
        ).values('vendedor').annotate(
        total_preco=Sum(F('preco') * F('unidades'))
    ).values('total_preco')
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = hoje.year - 1
    else:
        ano_anterior = hoje.year
        mes_anterior = mes_atual - 1
    # foi removido 'unidades'
    subquery_anterior = dados.filter(
        Q(cadastro__month=mes_anterior, cadastro__year=ano_anterior) & Q(vendedor=OuterRef('id'))
        ).values('vendedor').annotate(
        total_preco=Sum(F('preco') * F('unidades'))
    ).values('total_preco')
    dados_user = DadosUser.objects.filter(Q(cargo='func') | Q(cargo='admin')).values_list('id_usuario', flat=True)
    users = User.objects.filter(id__in=dados_user).annotate(
        venda_atual=Coalesce(Subquery(subquery_atual, output_field=FloatField()), 0.0),
        venda_anterior=Coalesce(Subquery(subquery_anterior, output_field=FloatField()), 0.0)
    )  
    user_json = list(users.values('id', 'username', 'venda_atual', 'venda_anterior'))       
    data = {
        "total_venda": venda_mes_atual,
        "notinha": notas_json,
        "payment": percentuais_formas,
        "vendas_anterior": venda_mes_anterior,
        "perc_cliente": percentual(cliente_mes_atual, cliente_mes_anterior),
        "vendas_hoje": vendas_hoje,
        "vendas_ontem": vendas_ontem,
        "users": user_json
    }

    return data

def percentual(v1, v2):
    if v1 and v2:
        frac = v1 - v2
        div = frac / v2
        result = div * 100
    else:
        result = 0
    return result