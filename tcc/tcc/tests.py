import unittest
from neomodel import db
from myapi.models import Pessoa, Organizacao
from datetime import datetime
from rag.utils import implementa_rag, get_llm, get_neo4j_driver, close_driver
from typing import Union

import json

def normalize_response(resp) -> Union[dict, None]:
	"""
	Convert resp (str/bytes/dict) into a Python dict or return None.
	"""
	if resp is None:
		return None
	if isinstance(resp, bytes):
		try:
			resp = resp.decode()
		except Exception:
			return None
	if isinstance(resp, str):
		try:
			return json.loads(resp)
		except Exception:
			return None
	return resp

class Pessoa_Organizacao_Test(unittest.TestCase):
    def setUp(self):
        self.pessoa = Pessoa(nome="LUIZA").save()
        self.organizacao = Organizacao(nome="PUC-Rio").save()
        self.pessoa.cargo.connect(self.organizacao, 
                                {'cargo':'Desenvolvedor',
                                'data_inicio': datetime(2020, 1, 15),
                                'grau_precisao': 5})
        self.irmao_pessoa = Pessoa(nome='ARTHUR').save()
        self.pessoa.irmao.connect(self.irmao_pessoa,{'grau_precisao': 5})
    
    ##### Testes com LLM #####
    
    def test_onde_pessoa_trabalha(self):
        llm = get_llm()
        driver = get_neo4j_driver()
        pergunta = 'Onde LUIZA trabalha?'
        resp = implementa_rag(llm, driver, pergunta, json_bool=True)
        resp = normalize_response(resp)
        if resp:
            resultado = resp['resultados'][0]['colunas']['n']['propriedades']['nome']
            if resultado:
                self.assertEqual(resultado, 'PUC-Rio')
        close_driver(driver)
    
    
    def test_pessoas_trabalham_em_x(self):
        pergunta = 'Quem trabalha na PUC-Rio?'
        driver = get_neo4j_driver()
        resp = implementa_rag(get_llm(), driver, pergunta, json_bool=True)
        resp = normalize_response(resp)
        if resp:
            resultado = resp['resultados'][0]['colunas']['n']['propriedades']['nome']
            if resultado:
                self.assertEqual(resultado, 'LUIZA')
            else:
                self.fail("Nenhum resultado encontrado")
        close_driver(driver)
    
    
    def test_irmaos_de_pessoa(self):
        pergunta = 'Quem são os irmãos de LUIZA?'
        driver = get_neo4j_driver()
        resp = implementa_rag(get_llm(), driver, pergunta, json_bool=True)
        resp = normalize_response(resp)
        if resp:
            resultado = resp['resultados'][0]['colunas']['n']['propriedades']['nome']
            if resultado:
                self.assertEqual(resultado, 'ARTHUR')
            else:
                self.fail("Nenhum resultado encontrado")
        close_driver(driver)
    
    
    def test_ligacao_entre_duas_pessoas(self):
        pergunta = 'Qual a ligação entre LUIZA e ARTHUR?'
        driver = get_neo4j_driver()
        resp = implementa_rag(get_llm(), driver, pergunta, json_bool=True)
        resp = normalize_response(resp)
        if resp:
            resultado = None
            colunas = resp['resultados'][0].get('colunas', {})
            for coluna in colunas.values():
                if not isinstance(coluna, dict):
                    continue
                props = coluna.get('propriedades', {})
                if 'grau_precisao' in props:
                    resultado = props['grau_precisao']
                    break
            if resultado:
                self.assertEqual(resultado, 5)
            else:
                self.fail("Nenhum resultado encontrado")
        close_driver(driver)
    
    
    def test_tipo_relacao_entre_duas_pessoas(self):
        pergunta = 'Qual o tipo de relação entre LUIZA e ARTHUR?'
        driver = get_neo4j_driver()
        resp = implementa_rag(get_llm(), driver, pergunta, json_bool=True)
        resp = normalize_response(resp)
        if resp:
            resultado = None
            colunas = resp['resultados'][0].get('colunas', {})
            for coluna in colunas.values():
                if not isinstance(coluna, dict):
                    continue
                props = coluna.get('propriedades', {})
                if 'grau_precisao' in props:
                    resultado = props['grau_precisao']
                    break
            if resultado:
                self.assertEqual(resultado, 5)
        close_driver(driver)
    
    
    def test_parentes_de_pessoa(self):
        pergunta = 'Quem são os parentes de LUIZA?'
        driver = get_neo4j_driver()
        resp = implementa_rag(get_llm(), driver, pergunta, json_bool=True)
        resp = normalize_response(resp)
        if resp:
            resultado = resp['resultados'][0]['colunas']['n']['propriedades']['nome']
            if resultado:
                self.assertEqual(resultado, 'ARTHUR')
            else:
                self.fail("Nenhum resultado encontrado")
        close_driver(driver)
    
    
    def test_irmaos_de_pessoa_em_empresa(self):
        self.irmao_pessoa.cargo.connect(self.organizacao, 
                        {'cargo':'Estagiário',
                        'data_inicio': datetime(2021, 6, 1),
                        'grau_precisao': 5})
        pergunta = 'Quem são os irmãos de LUIZA que trabalham na PUC-Rio?'
        driver = get_neo4j_driver()
        resp = implementa_rag(get_llm(), driver, pergunta, json_bool=True)
        resp = normalize_response(resp)
        if resp:
            resultado = resp['resultados'][0]['colunas']['n']['propriedades']['nome']
            if resultado:
                self.assertEqual(resultado, 'ARTHUR')
            else:
                self.fail("Nenhum resultado encontrado")
        close_driver(driver)
    
    ##### Testes sem LLM #####
    
    def test_criacao_de_pessoa(self):
        pessoa = Pessoa.nodes.get(nome="LUIZA")
        self.assertEqual(pessoa.nome, "LUIZA")

    def test_relacionamento_pessoa_empresa(self):
        pessoa = Pessoa.nodes.get(nome="LUIZA")
        organizacoes = list(pessoa.cargo.all())
        self.assertEqual(organizacoes[0].nome, "PUC-Rio")

    def test_relacionamento_pessoa_um_irmao(self):
        self.irmao_pessoa = Pessoa(nome='ARTHUR').save()
        self.pessoa.irmao.connect(self.irmao_pessoa,{'grau_precisao': 5})
        lista_irmaos = list(self.pessoa.irmao.all())
        self.assertEqual(lista_irmaos[0].nome, 'ARTHUR')
        db.cypher_query("MATCH (n:Pessoa) WHERE n.nome = 'ARTHUR' DETACH DELETE n")
        
    def test_relacionamento_pessoa_varios_irmaos(self):
        irmao1 = Pessoa(nome='LETICIA').save()
        irmao2 = Pessoa(nome='PEDRO').save()
        self.pessoa.irmao.connect(irmao1,{'grau_precisao': 5})
        self.pessoa.irmao.connect(irmao2,{'grau_precisao': 5})
        lista_irmaos = list(self.pessoa.irmao.all())
        self.assertEqual(len(lista_irmaos), 3)
        self.assertIn(irmao1, lista_irmaos)
        self.assertIn(irmao2, lista_irmaos)
        nomes = {i.nome for i in lista_irmaos}
        self.assertSetEqual(nomes, {'LETICIA', 'PEDRO', 'ARTHUR'})
    
    def tearDown(self):
        driver = get_neo4j_driver()
        driver.execute_query("MATCH (n) DETACH DELETE n")
        close_driver(driver)