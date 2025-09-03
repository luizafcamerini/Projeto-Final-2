from django.db import models
from neomodel import StructuredNode, StringProperty, RelationshipTo, DateProperty, StructuredRel, FloatProperty, IntegerProperty

# Relationship models

class Relacao_Interpessoal(StructuredRel):
    '''Classe que representa a relação de filiação entre duas pessoas.'''
    grau_precisao = IntegerProperty(required=True)

class Relacao_Interpessoal_Temporal(StructuredRel):
    '''Classe que representa a relação de filiação entre duas pessoas.'''
    grau_precisao = IntegerProperty(required=True)
    inicio = DateProperty(required=True)
    fim = DateProperty()

class Relacao_Membro(StructuredRel):
    '''Classe que representa a relação de um membro com 
    uma parceria e/ou organizacao.'''
    inicio = DateProperty(required=True)
    fim = DateProperty()
    grau_precisao = IntegerProperty(required=True)

class Relacao_Transacao(StructuredRel):
    '''Classe que representa a relação de uma transação entre
    uma pessoa e uma organização ou entre duas pessoas.'''
    valor = FloatProperty(required=True)
    data = DateProperty(required=True)
    grau_precisao = IntegerProperty(required=True)

class Relacao_Papel(StructuredRel):
    '''Classe que representa o papel de uma pessoa em um cargo.'''
    papel = StringProperty(required=True)
    inicio = DateProperty(required=True)
    fim = DateProperty()
    grau_precisao = IntegerProperty(required=True)
    
class Relacao_Cargo(StructuredRel):
    '''Classe que representa a relação de um cargo com uma organização.'''
    papel = StringProperty(required=True)
    inicio = DateProperty(required=True)
    fim = DateProperty()
    grau_precisao = IntegerProperty(required=True)

# Node models

class Organizacao(StructuredNode):
    '''Classe que representa uma entidade organizacional.'''
    cnpj = StringProperty(unique_index=True, required=True)
    nome = StringProperty(required=True)
    tipo = StringProperty()
    objetivo = StringProperty()

class Parceria(StructuredNode):
    '''Classe que representa uma entidade Parceria.'''
    membro = RelationshipTo(Organizacao, 'MEMBRO_DE', model=Relacao_Membro)
    grau_precisao = IntegerProperty(required=True)

class Pessoa(StructuredNode):
    '''Classe que representa uma entidade PEP (Pessoa Exposta Politicamente).'''
    generos = {'M': 'Masculino', 'F': 'Feminino', 'O': 'Outro'}
    nome = StringProperty(required=True)
    cpf = StringProperty(unique_index=True)
    data_nascimento = DateProperty(required=True)
    genero = StringProperty(required=True, choices=generos)
    cnpj = StringProperty(unique_index=True)
    
    filho = RelationshipTo('Pessoa', 'FILHO_DE', model=Relacao_Interpessoal)
    neto = RelationshipTo('Pessoa', 'NETO_DE', model=Relacao_Interpessoal)
    irmao = RelationshipTo('Pessoa', 'IRMAO_DE', model=Relacao_Interpessoal)
    conjuge = RelationshipTo('Pessoa', 'CONJUGE_DE', model=Relacao_Interpessoal_Temporal)
    descendente = RelationshipTo('Pessoa', 'DESCENDENTE_DE', model=Relacao_Interpessoal)
    conhecido = RelationshipTo('Pessoa', 'CONHECE', model=Relacao_Interpessoal)
    
    membro = RelationshipTo(Parceria, 'MEMBRO_DE', model=Relacao_Membro)
    transacao_pessoa = RelationshipTo('Pessoa', 'REALIZOU', model=Relacao_Transacao)
    transacao_organizacao = RelationshipTo(Organizacao, 'REALIZOU', model=Relacao_Transacao)

class Cargo(StructuredNode):
    '''Classe que representa um cargo ocupado por uma pessoa em uma organização.'''
    nome = StringProperty(required=True)
    pertence = RelationshipTo(Organizacao, 'PERTENCE_A')