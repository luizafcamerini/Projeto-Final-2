import unittest
from neomodel import db
from myapi.models import Pessoa, Organizacao
from datetime import datetime
from rag.utils import implementa_rag, get_llm, get_neo4j_driver, close_driver

class Pessoa_Organizacao_Test(unittest.TestCase):
    def setUp(self):
        
        # db.cypher_query("MATCH (n) DETACH DELETE n")
        self.pessoa = Pessoa(nome="LUIZA").save()
        self.organizacao = Organizacao(nome="PUC-Rio").save()
        self.pessoa.cargo.connect(self.organizacao, 
                                {'cargo':'Desenvolvedor',
                                'data_inicio': datetime(2020, 1, 15),
                                'grau_precisao': 5})
    
    
    def test_onde_pessoa_trabalha(self):
        llm = get_llm()
        driver = get_neo4j_driver()
        pergunta = 'Onde LUIZA trabalha?'
        json = implementa_rag(llm, driver, pergunta, json_bool=True)
        if json:
            resultado = json['resultados'][0]['colunas']['n']['propriedades']['nome']
            if resultado:
                self.assertEqual(resultado, 'PUC-Rio')
        close_driver(driver)
    
    
    def pessoas_trabalham_em_x(self):
        pergunta = 'Quem trabalha na PUC-Rio?'
        json = implementa_rag(get_llm(), get_neo4j_driver(), pergunta, json_bool=True)
        if json:
            resultado = json['resultados'][0]['colunas']['n']['propriedades']['nome']
            if resultado:
                self.assertEqual(resultado, 'LUIZA')
            else:
                self.fail("Nenhum resultado encontrado")
        close_driver(get_neo4j_driver())
    
    
    def irmaos_de_pessoa(self):
        pergunta = 'Quem são os irmãos de LUIZA?'
        json = implementa_rag(get_llm(), get_neo4j_driver(), pergunta, json_bool=True)
        if json:
            resultado = json['resultados'][0]['colunas']['n']['propriedades']['nome']
            if resultado:
                self.assertEqual(resultado, 'Arthur')
            else:
                self.fail("Nenhum resultado encontrado")
        close_driver(get_neo4j_driver())
    
    
    def ligacao_entre_duas_pessoas(self):
        pergunta = 'Qual a ligação entre LUIZA e ARTHUR?'
        json = implementa_rag(get_llm(), get_neo4j_driver(), pergunta, json_bool=True)
        if json:
            resultado = json['resultados'][0]['colunas']['relacao']['propriedades']['grau_precisao']
            if resultado:
                self.assertEqual(resultado, 5)
            else:
                self.fail("Nenhum resultado encontrado")
        close_driver(get_neo4j_driver())
    
    
    def tipo_relacao_entre_duas_pessoas(self):
        ...
    
    
    def parentes_de_pessoa(self):
        ...
    
    
    def irmaos_de_pessoa_em_empresa(self):
        ...
    
    # def test_criacao_de_pessoa(self):
    #     pessoa = Pessoa.nodes.get(nome="LUIZA")
    #     self.assertEqual(pessoa.nome, "LUIZA")

    # def test_relacionamento_pessoa_empresa(self):
    #     pessoa = Pessoa.nodes.get(nome="LUIZA")
    #     organizacoes = list(pessoa.cargo.all())
    #     self.assertEqual(organizacoes[0].nome, "PUC-Rio")

    # def test_relacionamento_pessoa_um_irmao(self):
    #     self.irmao = Pessoa(nome='Arthur').save()
    #     self.pessoa.irmao.connect(self.irmao,{'grau_precisao': 5})
    #     lista_irmaos = list(self.pessoa.irmao.all())
    #     self.assertEqual(lista_irmaos[0].nome, 'Arthur')
    #     db.cypher_query("MATCH (n:Pessoa) WHERE n.nome = 'Arthur' DETACH DELETE n")
        
    # def test_relacionamento_pessoa_varios_irmaos(self):
    #     irmao1 = Pessoa(nome='Leticia').save()
    #     irmao2 = Pessoa(nome='Pedro').save()
    #     self.pessoa.irmao.connect(irmao1,{'grau_precisao': 5})
    #     self.pessoa.irmao.connect(irmao2,{'grau_precisao': 5})
    #     lista_irmaos = list(self.pessoa.irmao.all())
    #     self.assertEqual(len(lista_irmaos), 2)
    #     self.assertIn(irmao1, lista_irmaos)
    #     self.assertIn(irmao2, lista_irmaos)
    #     nomes = {i.nome for i in lista_irmaos}
    #     self.assertSetEqual(nomes, {'Leticia', 'Pedro'})
    
    # def tearDown(self):
    #     db.cypher_query("MATCH (n) DETACH DELETE n")