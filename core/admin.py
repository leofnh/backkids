from django.contrib import admin
from .models import Produto, ProdutoVendido, Cliente, Notinha, DadosUser, Carrinho

# Register your models here.
admin.site.register(Produto)
admin.site.register(ProdutoVendido)
admin.site.register(Cliente)
admin.site.register(Notinha)
admin.site.register(DadosUser)
admin.site.register(Carrinho)