from ..models import Cliente, Notinha
import datetime
def cadastrar_cliente(data):
    nome = data.get('nome', '')
    resp = {}
    if nome:
        existe = Cliente.objects.filter(nome=nome)
        if existe:
            resp['status'] = 'erro'
            resp['msg'] = 'Este cliente ja é cadastrado em nosso banco de dados! Verifique o nome do cliente.'
            return resp
        else:
            try:
                hoje = datetime.datetime.today()
                idt = data.get('idt', '')
                dn = data.get('dn', '')
                rua = data.get('rua', '')
                bairro = data.get('bairro', '')
                numero = data.get('numero', '')
                cidade = data.get('cidade', '')
                sapato = data.get('sapato', '')
                roupa = data.get('roupa', '')
                nome = data.get('nome', '')
                cpf = data.get('cpf', '')
                telefone = data.get('telefone', '')

                Cliente.objects.create(
                    nome=nome,
                    cpf=cpf,
                    idt=idt,
                    dn=dn,
                    rua=rua,
                    bairro=bairro,
                    numero=numero,
                    cidade=cidade,
                    sapato=sapato,
                    roupa=roupa,
                    cadastro=hoje,
                    telefone=telefone
                )
                resp['status'] = 'sucesso'
                resp['msg'] = 'Cliente cadastrado na nossa base de dados com sucesso!'
                dados = Cliente.objects.all()
                dados_json = list(dados.values('nome', 'cpf', 'idt', 'dn', 
                                       'rua', 'bairro', 'cidade',
                                       'numero', 'sapato', 'roupa', 'cadastro', 'id', 'telefone'
                                       ))
                resp['dados'] = dados_json
                return resp
            except Exception as e:
                resp['status'] = 'erro'
                resp['msg'] = str(e)
                return resp
    else:
        resp['status'] = 'erro'
        resp['msg'] = 'CPF Inválido ou não digitado, por favor confirme o dado.'
        return resp    


def get_cliente():
    clientes = Cliente.objects.all()
    return clientes

def update_clients(data):
    resp = {}
    try:      
        id_client = int(data.get('id', ''))
        idt = data.get('idt', '')
        dn = data.get('dn', '')
        rua = data.get('rua', '')
        bairro = data.get('bairro', '')
        numero = data.get('numero', '')
        cidade = data.get('cidade', '')
        sapato = data.get('sapato', '')
        roupa = data.get('roupa', '')
        nome = data.get('nome', '')
        cpf = data.get('cpf' , '')
        telefone = data.get('telefone', '')
        dados = Cliente.objects.get(id=id_client)
        nome_client = dados.nome
        tem_nota = Notinha.objects.filter(cliente=nome_client)
        if tem_nota:
            for i in tem_nota:
                tem_nota.update(
                    cliente=nome_client
                )
        
        dados.cpf = cpf
        dados.nome = nome
        dados.roupa = roupa
        dados.sapato = sapato
        dados.numero = numero
        dados.bairro = bairro
        dados.cidade = cidade
        dados.dn = dn
        dados.rua = rua
        dados.idt = idt
        dados.telefone = telefone
        dados.save()
        dados_att = Cliente.objects.all()
        dados_json = list(dados_att.values('nome', 'cpf', 'idt', 'dn', 
                        'rua', 'bairro', 'cidade',
                        'numero', 'sapato', 'roupa', 'cadastro', 'id', 'telefone'
                        ))
        resp['dados'] = dados_json
        resp['status'] = 'sucesso'
        resp['msg'] = 'Dados atualizado com sucesso!'     
    except Exception as e:
        resp['status'] = 'erro'
        resp['msg'] = f'Houve um erro na tentativa de atualizar os dados: {str(e)}'
    return resp