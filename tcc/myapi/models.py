from django.db import models
from neomodel import StructuredNode, StringProperty, RelationshipTo, DateProperty, StructuredRel, FloatProperty, IntegerProperty

# Relationship models

class Relacao_Interpessoal(StructuredRel):
    '''Classe que representa a relação de filiação entre duas pessoas.'''
    grau_precisao = IntegerProperty(required=True)

class Relacao_Interpessoal_Temporal(StructuredRel):
    '''Classe que representa a relação de filiação entre duas pessoas.'''
    grau_precisao = IntegerProperty(required=True)
    ano_inicio = IntegerProperty()
    ano_fim = IntegerProperty()

class Relacao_Cargo(StructuredRel):
    '''Classe que representa a relação de uma pessoa a um cargo.'''
    cargo = StringProperty(required=True)
    data_inicio = DateProperty(required=True)
    data_fim = DateProperty()
    grau_precisao = IntegerProperty(required=True)

class Relacao_Pessoa_Sociedade(StructuredRel):
    '''Classe que representa a relação de uma pessoa a um bem.'''
    valor_bem = FloatProperty()
    cargo = StringProperty()
    grau_precisao = IntegerProperty(required=True)

# Node models
class Organizacao(StructuredNode):
    '''Classe que representa uma entidade organizacional.'''
    cnpj = StringProperty(unique_index=True)
    nome = StringProperty(required=True, unique_index=True)
    grau_precisao = IntegerProperty(required=True)
    tipo = StringProperty()
    objetivo = StringProperty()

class Pessoa(StructuredNode):
    '''Classe que representa uma entidade PEP (Pessoa Exposta Politicamente).'''
    nome = StringProperty(unique_index=True,required=True)
    cpf = StringProperty()
    data_nascimento = DateProperty()
    grau_precisao = IntegerProperty(required=True)
    
    filho = RelationshipTo('Pessoa', 'FILHO_DE', model=Relacao_Interpessoal)
    neto = RelationshipTo('Pessoa', 'NETO_DE', model=Relacao_Interpessoal)
    irmao = RelationshipTo('Pessoa', 'IRMAO_DE', model=Relacao_Interpessoal)
    descendente = RelationshipTo('Pessoa', 'DESCENDENTE_DE', model=Relacao_Interpessoal)
    familiar = RelationshipTo('Pessoa', 'FAMILIAR_DE', model=Relacao_Interpessoal) # representa um familiar generico
    conjuge = RelationshipTo('Pessoa', 'CONJUGE_DE', model=Relacao_Interpessoal_Temporal)
    
    socio = RelationshipTo('Organizacao', 'SOCIO_DE', model=Relacao_Pessoa_Sociedade)
    cargo = RelationshipTo('Organizacao', 'OCUPA', model=Relacao_Cargo)