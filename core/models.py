from django.db import models
import datetime

# Create your models here.
class Produto(models.Model):
    produto = models.CharField(max_length=555, default='produto')
    marca = models.CharField(max_length=555)
    tamanho = models.CharField(max_length=55)
    preco = models.FloatField(default=0)
    estoque = models.BigIntegerField(default=0)
    codigo = models.CharField(max_length=555)
    ref = models.CharField(max_length=555)
    custo = models.FloatField(default=0)
    loja = models.BooleanField(default=False)
    descricao = models.CharField(max_length=555, null=True)
    cor = models.CharField(max_length=555)
    sequencia = models.BigIntegerField(default=1)
    cadastro = models.DateTimeField()
    update = models.DateTimeField(auto_now=True)
    
    #cor = models.CharField(max_length=555)

    def get_data(self):
        return self.cadastro.strftime('%d/%m/%Y %H:%M')

class ProdutoVendido(models.Model):
    produto = models.CharField(max_length=555, default='produto')
    marca = models.CharField(max_length=555)
    tamanho = models.CharField(max_length=55)
    preco = models.FloatField(default=0)
    unidades = models.BigIntegerField(default=0)
    codigo = models.CharField(max_length=555)
    ref = models.CharField(max_length=555)
    custo = models.FloatField(default=0)
    forma = models.CharField(max_length=555, default='dinheiro')
    vendedor = models.BigIntegerField(default=1)
    cadastro = models.DateTimeField()
    loja = models.BooleanField(default=False)
    descricao = models.CharField(max_length=555, null=True)
    update = models.DateTimeField(auto_now=True)

    def get_data(self):
        return self.cadastro.strftime('%d/%m/%Y %H:%M')

class Cliente(models.Model):
    nome = models.CharField(max_length=555)
    cpf = models.CharField(max_length=20)
    idt = models.CharField(max_length=30)
    dn = models.DateField()
    rua = models.CharField(max_length=555)
    bairro = models.CharField(max_length=555)
    numero = models.CharField(max_length=555)
    cidade = models.CharField(max_length=555)
    sapato = models.CharField(max_length=5)
    roupa = models.CharField(max_length=5)
    telefone = models.CharField(max_length=15, null=True)
    cadastro = models.DateField()
    update = models.DateTimeField(auto_now=True)

    def get_data(self):
        return self.cadastro.strftime('%d/%m/%Y %H:%M')

class Notinha(models.Model):
    cliente = models.CharField(max_length=555)
    vencimento = models.DateField()
    produto = models.CharField(max_length=555)
    valor = models.FloatField()
    cadastro = models.DateTimeField()
    status = models.CharField(max_length=555, default='aberto')
    update = models.DateTimeField(auto_now=True)

    def get_data(self):
        return self.cadastro.strftime('%d/%m/%Y %H:%M')
    
    def get_vencimento(self):
        return self.vencimento.strftime('%d/%m/%Y %H:%M')

class DadosUser(models.Model):
    id_usuario = models.BigIntegerField()
    nome_usuario = models.CharField(max_length=555)
    cargo = models.CharField(max_length=55)
    cadastro = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

class Carrinho(models.Model):
    def hoje():
        return datetime.datetime.today()
        
    id_produto = models.BigIntegerField()
    nome_usuario = models.CharField(max_length=555)
    quantidade = models.BigIntegerField(default=1)
    pedido = models.BooleanField(default=False)
    enviado = models.BooleanField(default=False)
    contato = models.CharField(max_length=555, default='atualizar')
    endereco = models.TextField(default='atualizar')
    cliente = models.CharField(max_length=555, default="atualizar")
    email = models.CharField(max_length=555, default="atualizar")
    cidade = models.CharField(max_length=555, default="atualizar")
    estado = models.CharField(max_length=555, default="atualizar")
    cep = models.CharField(max_length=555, default='atualizar')
    cpf = models.CharField(max_length=555, default="atualizar")    
    cadastro = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

class CondicionalCliente(models.Model):
    cliente = models.CharField(max_length=555)
    aberto = models.BooleanField(default=True)
    cadastro = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

class ProdutoCondicional(models.Model):
    condicional = models.BigIntegerField()
    produto = models.CharField(max_length=555)
    qtde = models.BigIntegerField(default=1)
    data_devolvido = models.DateTimeField(null=True)
    vendido = models.BooleanField(default=False)
    cadastro = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

class FotoProduto(models.Model):
    url = models.URLField()
    id_produto = models.CharField(max_length=555)
    update = models.DateTimeField(auto_now=True)
    cadastro = models.DateTimeField(auto_now_add=True)

class FotoCapaSite(models.Model):
    url = models.URLField()
    cadastro = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

class AboutUs(models.Model):
    page = models.TextField()
    cadastro = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
