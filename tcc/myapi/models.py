from django.db import models
from neomodel import StructuredNode, StringProperty, RelationshipTo, DateProperty, StructuredRel, FloatProperty, IntegerProperty

# Relationship models

class Relacao_Interpessoal(StructuredRel):
    '''Classe que representa a relação de filiação entre duas pessoas.'''
    grau_precisao = IntegerProperty(required=True)

class Relacao_Interpessoal_Temporal(StructuredRel):
    '''Classe que representa a relação de filiação entre duas pessoas.'''
    grau_precisao = IntegerProperty(required=True)
    data_inicio = DateProperty()
    data_fim = DateProperty()

class Relacao_Membro(StructuredRel):
    '''Classe que representa a relação de um membro com 
    uma parceria e/ou organizacao.'''
    data_inicio = DateProperty(required=True)
    data_fim = DateProperty()
    grau_precisao = IntegerProperty(required=True)

class Relacao_Transacao(StructuredRel):
    '''Classe que representa a relação de uma transação entre
    uma pessoa e uma organização ou entre duas pessoas.'''
    valor = FloatProperty(required=True)
    data = DateProperty(required=True)
    grau_precisao = IntegerProperty(required=True)
    
class Relacao_Cargo(StructuredRel):
    '''Classe que representa a relação de uma pessoa a um cargo.'''
    cargo = StringProperty(required=True)
    data_inicio = DateProperty(required=True)
    data_fim = DateProperty()
    grau_precisao = IntegerProperty(required=True)

# Node models

class Organizacao(StructuredNode):
    '''Classe que representa uma entidade organizacional.'''
    cnpj = StringProperty(unique_index=True)
    nome = StringProperty(required=True, unique_index=True)
    tipo = StringProperty()
    objetivo = StringProperty()

class Parceria(StructuredNode):
    '''Classe que representa uma entidade Parceria.'''
    grau_precisao = IntegerProperty(required=True)
    membro = RelationshipTo('Organizacao', 'MEMBRO_DE', model=Relacao_Membro)

class Pessoa(StructuredNode):
    '''Classe que representa uma entidade PEP (Pessoa Exposta Politicamente).'''
    generos = {'M': 'Masculino', 'F': 'Feminino', 'O': 'Outro'}
    
    nome = StringProperty(unique_index=True,required=True)
    cpf = StringProperty()
    data_nascimento = DateProperty()
    genero = StringProperty(choices=generos)
    cnpj = StringProperty()
    
    filho = RelationshipTo('Pessoa', 'FILHO_DE', model=Relacao_Interpessoal)
    neto = RelationshipTo('Pessoa', 'NETO_DE', model=Relacao_Interpessoal)
    irmao = RelationshipTo('Pessoa', 'IRMAO_DE', model=Relacao_Interpessoal)
    conjuge = RelationshipTo('Pessoa', 'CONJUGE_DE', model=Relacao_Interpessoal_Temporal)
    descendente = RelationshipTo('Pessoa', 'DESCENDENTE_DE', model=Relacao_Interpessoal)
    conhecido = RelationshipTo('Pessoa', 'CONHECE', model=Relacao_Interpessoal)
    
    membro = RelationshipTo('Parceria', 'MEMBRO_DE', model=Relacao_Membro)
    transacao_pessoa = RelationshipTo('Pessoa', 'REALIZOU', model=Relacao_Transacao)
    transacao_organizacao = RelationshipTo('Organizacao', 'REALIZOU', model=Relacao_Transacao)
    cargo = RelationshipTo('Organizacao', 'OCUPA', model=Relacao_Cargo)