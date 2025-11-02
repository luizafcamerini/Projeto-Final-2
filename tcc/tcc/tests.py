import unittest
from neomodel import db
from myapi.models import Pessoa, Organizacao
from datetime import datetime

class Pessoa_Organizacao_Test(unittest.TestCase):
    def setUp(self):
        db.cypher_query("MATCH (n) DETACH DELETE n")
        self.pessoa = Pessoa(nome="Luíza").save()
        self.organizacao = Organizacao(nome="PUC-Rio").save()
        self.pessoa.cargo.connect(self.organizacao, 
                                {'cargo':'Desenvolvedor',
                                'data_inicio': datetime(2020, 1, 15),
                                'grau_precisao': 5})

    def test_criacao_de_pessoa(self):
        pessoa = Pessoa.nodes.get(nome="Luíza")
        self.assertEqual(pessoa.nome, "Luíza")

    def test_relacionamento_pessoa_empresa(self):
        pessoa = Pessoa.nodes.get(nome="Luíza")
        organizacoes = list(pessoa.cargo.all())
        self.assertEqual(organizacoes[0].nome, "PUC-Rio")

    def test_relacionamento_pessoa_um_irmao(self):
        self.irmao = Pessoa(nome='Arthur').save()
        self.pessoa.irmao.connect(self.irmao,{'grau_precisao': 5})
        lista_irmaos = list(self.pessoa.irmao.all())
        self.assertEqual(lista_irmaos[0].nome, 'Arthur')
        db.cypher_query("MATCH (n:Pessoa) WHERE n.nome = 'Arthur' DETACH DELETE n")
        
    def test_relacionamento_pessoa_varios_irmaos(self):
        irmao1 = Pessoa(nome='Leticia').save()
        irmao2 = Pessoa(nome='Pedro').save()
        self.pessoa.irmao.connect(irmao1,{'grau_precisao': 5})
        self.pessoa.irmao.connect(irmao2,{'grau_precisao': 5})
        lista_irmaos = list(self.pessoa.irmao.all())
        self.assertEqual(len(lista_irmaos), 2)
        self.assertIn(irmao1, lista_irmaos)
        self.assertIn(irmao2, lista_irmaos)
        nomes = {i.nome for i in lista_irmaos}
        self.assertSetEqual(nomes, {'Leticia', 'Pedro'})
    
    def tearDown(self):
        db.cypher_query("MATCH (n) DETACH DELETE n")