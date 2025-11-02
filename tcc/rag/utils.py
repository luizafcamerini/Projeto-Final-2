from django.conf import settings
from neo4j import GraphDatabase, Driver
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.llm import CohereLLM
from neo4j.graph import Path, Node, Relationship # Importações necessárias
from typing import Any, List, Dict, Union, Tuple
import json

NEO4J_SCHEMA = """
    Propriedade dos nos:
    Pessoa [nome:STRING, cpf:STRING, data_nascimento:DATE, cnpj:STRING]
    Organizacao [cnpj:STRING, nome:STRING]
    Propriedades de relacionamentos:
    FILHO_DE [grau_precisao:INTEGER]
    NETO_DE [grau_precisao:INTEGER]
    IRMAO_DE [grau_precisao:INTEGER]
    DESCENDENTE_DE [grau_precisao:INTEGER]
    FAMILIAR_DE [grau_precisao:INTEGER]
    CONJUGE_DE [grau_precisao:INTEGER, ano_inicio:INTEGER, ano_fim:INTEGER]
    SOCIO_DE [valor_bem:FLOAT, cargo:STRING, grau_precisao:INTEGER]
    OCUPA [cargo:STRING, data_inicio:DATE, data_fim:DATE, grau_precisao:INTEGER]
    Os relacionamentos:
    (:Pessoa)-[:FILHO_DE]->(:Pessoa)
    (:Pessoa)-[:NETO_DE]->(:Pessoa)
    (:Pessoa)-[:IRMAO_DE]->(:Pessoa)
    (:Pessoa)-[:DESCENDENTE_DE]->(:Pessoa)
    (:Pessoa)-[:FAMILIAR_DE]->(:Pessoa)
    (:Pessoa)-[:CONJUGE_DE]->(:Pessoa)
    (:Pessoa)-[:SOCIO_DE]->(:Organizacao)
    (:Pessoa)-[:OCUPA]->(:Organizacao)
"""

EXEMPLOS = [
  """USER INPUT: 'ONDE O MARCOS TRABALHA?'
  QUERY: 'MATCH (p:Pessoa)-[:OCUPA]->(n) WHERE p.nome CONTAINS 'MARCOS' RETURN n'""",
  """USER INPUT: 'QUE PESSOAS TRABALHAM EM SÃO PAULO?'
  QUERY: 'MATCH (p:Pessoa)-[:OCUPA]->(n) WHERE n.nome CONTAINS 'SÃO PAULO' RETURN n'""",
  """USER INPUT: 'QUEM SAO OS IRMAOS DE LUIZA?'
  QUERY: 'MATCH (p:Pessoa)-[:IRMAO_DE]->(n) WHERE p.nome CONTAINS 'LUIZA' RETURN n'""",
  """USER INPUT: 'QUAL A LIGACAO ENTRE MARCOS E LUIZA?'
  QUERY: 'MATCH ligacao=(p:Pessoa)-[*1..]-(n:Pessoa) WHERE p.nome CONTAINS 'MARCOS' AND n.nome CONTAINS 'LUIZA' RETURN ligacao'""",
  """USER INPUT: 'QUE TIPO DE RELACAO EXISTE ENTRE MARCOS E LUIZA?'
  QUERY: 'MATCH relacao=(p:Pessoa)-[*1..]-(n:Pessoa) WHERE p.nome CONTAINS 'MARCOS' AND n.nome CONTAINS 'LUIZA' RETURN relacao'""",
  """USER INPUT: 'QUAIS SAO OS PARENTES DE JOAO DA SILVA?'
  QUERY: 'MATCH (p:Pessoa)-[:FILHO_DE | NETO_DE | IRMAO_DE | DESCENDENTE_DE | FAMILIAR_DE | CONJUGE_DE]->(n:Pessoa) WHERE p.nome CONTAINS 'JOAO DA SILVA' RETURN n'""",
  """USER INPUT: 'QUAIS SAO OS IRMAOS DE JOAO DA SILVA QUE TRABALHAM NA EMPRESA ABC?'
  QUERY: 'MATCH (p:Pessoa)-[:IRMAO_DE]->(n)-[:OCUPA]->(o:Organizacao) WHERE p.nome CONTAINS 'JOAO DA SILVA' AND o.nome CONTAINS 'ABC' RETURN n'""",
]

PROMPT_TEMPLATE = """
    Voce e um agente especialista em recolher dados sobre cargos, familiares de politicos brasileiros e organizacoes brasileiras.
    Dada uma pergunta do usuário, você formará uma query Cypher que responda a pergunta.
    O schema do banco de dados é este:
    {context}
    LEMBRE DISSO: Uma Organizacao pode representar tanto um orgao do governo quanto um estado ou municipio.
    Voce pode retornar nós do banco ou caminhos entre nós.
    Aqui estão alguns exemplos:
    {examples}
    SEMPRE use UPPERCASE para os nomes dos nós!!
    Use 'CONTAINS' para buscas parciais em strings.
    Atente-se como são retornados caminhos entre nós: SEMPRE use [*1..], sem definir um comprimento fixo.
    Pergunta do usuario:
    {query_text} """.format(context=NEO4J_SCHEMA, examples=EXEMPLOS, query_text="{query_text}")

def get_neo4j_driver() -> Driver:
    '''Metodo que retorna um driver do banco de dados.
    Pega as seguintes credenciais das settings do django:
    - NEO4J_URI
    - NEO4J_USERNAME
    - NEO4J_PASSWORD'''
    return GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME,settings.NEO4J_PASSWORD)
    )


def get_llm() -> CohereLLM:
    '''Metodo que cria e retorna objeto CohereLLM.
    Pega as seguintes credenciais das settings do django:
    - LLM_API_KEY
    - LLM_MODEL'''
    return CohereLLM(api_key=settings.LLM_API_KEY, 
                     model_name=settings.LLM_MODEL, 
                     model_params={"temperature":0})


def extrair_informacoes_do_path(caminho_neo4j_path: Path) -> dict:
    """Metodo que extrai informações estruturadas de um objeto Path do driver Python do Neo4j.
    Args:
        caminho_neo4j_path: Path; Objeto Path do Neo4j.
    
    Retorna:
        dict; Dict com informações estruturadas sobre o Path."""
    nos_info = []
    for no in caminho_neo4j_path.nodes:
        nos_info.append({
            "labels": list(no.labels),
            "propriedades": dict(no), # Converte as propriedades para um dicionário padrão
            "element_id": no.element_id,
        })

    relacionamentos_info = []
    for rel in caminho_neo4j_path.relationships:
        relacionamentos_info.append({
            "tipo": rel.type,
            "propriedades": dict(rel),
            "element_id": rel.element_id,
            "de": rel.start_node.get("nome", rel.start_node.element_id),
            "para": rel.end_node.get("nome", rel.end_node.element_id),
        })

    return {
        "tipo_retorno": "Path",
        "comprimento_caminho": len(caminho_neo4j_path.relationships),
        "nos": nos_info,
        "relacionamentos": relacionamentos_info,
    }

def extrair_informacoes_do_node(no_neo4j: Node) -> dict:
    """Metodo que extrai informações estruturadas de um objeto Node do driver Python do Neo4j.
    Args:
        no_neo4j: Node; Objeto Node do Neo4j.
    
    Retorna:
        dict; Dict com informações estruturadas sobre o Node."""
    return {
        "tipo_retorno": "Node",
        "labels": list(no_neo4j.labels),
        "propriedades": dict(no_neo4j),
        "element_id": no_neo4j.element_id,
    }

def extrair_informacoes_do_relationship(rel_neo4j: Relationship) -> dict:
    """Metodo que extrai informações estruturadas de um objeto Relationship do driver Python do Neo4j.
    Args:
        rel_neo4j: Relationship; Objeto Relationship do Neo4j.
        
    Retorna:
        dict; Dict com informações estruturadas sobre o Relationship."""
    return {
        "tipo_retorno": "Relationship",
        "tipo": rel_neo4j.type,
        "propriedades": dict(rel_neo4j),
        "element_id": rel_neo4j.element_id,
        "de": rel_neo4j.start_node.get("nome", rel_neo4j.start_node.element_id),
        "para": rel_neo4j.end_node.get("nome", rel_neo4j.end_node.element_id),
    }

def processar_resultado_generico(valor: Any) -> dict:
    """Metodo que processa um valor genérico retornado pelo Neo4j e extrai informações estruturadas.
    Args:
        valor: Any; Valor retornado pelo Neo4j (pode ser Path, Node, Relationship ou tipos primitivos).
        
    Retorna:
        dict; Dict com informações estruturadas sobre o valor."""
    if isinstance(valor, Path):
        return extrair_informacoes_do_path(valor)
    elif isinstance(valor, Node):
        return extrair_informacoes_do_node(valor)
    elif isinstance(valor, Relationship):
        return extrair_informacoes_do_relationship(valor)
    else:
        return {
            "tipo_retorno": type(valor).__name__,
            "valor": valor
        }

def implementa_rag(llm: Any, db_driver: Driver, pergunta: str, json_bool: bool) -> str:
    '''Metodo que junta todo o pipeline de RAG dada uma pergunta.
    Args:
        llm: Any; Objeto LLM (CohereLLM).
        db_driver: Driver; Driver do Neo4j.
        pergunta: str; Pergunta do usuario.
        json_bool: bool; Se True, retorna resultados em JSON, se False, retorna resposta formatada.
    Retorna:
        str; Resposta final do pipeline RAG.'''
    num_max_tentativas = 10
    tentativas = 0
    while tentativas < num_max_tentativas:
        try:
            retriever = Text2CypherRetriever(driver=db_driver,
                                             neo4j_schema=NEO4J_SCHEMA,
                                             llm=llm,
                                             examples=EXEMPLOS,
                                             custom_prompt=PROMPT_TEMPLATE)
            
            resultados_raw = retriever.get_search_results(pergunta)
            cypher_gerado = resultados_raw.metadata.get('cypher', 'N/A')
            print("Cypher gerado:", cypher_gerado)
            records = resultados_raw.records
            if records:
                resultados_processados_list = []
                keys = records[0].keys()

                for i, record in enumerate(records):
                    record_processado = {"registro_id": i + 1, "colunas": {}}
                    for key in keys:
                        valor = record[key]
                        record_processado["colunas"][key] = processar_resultado_generico(valor)
                    resultados_processados_list.append(record_processado)
                contexto_para_llm = {
                    "cypher_gerado": cypher_gerado,
                    "resultados": resultados_processados_list
                }
                
                if json_bool:
                    return json.dumps(contexto_para_llm, indent=0, ensure_ascii=False)
                resposta = llm.invoke(f"""Dado o contexto:
                                    ''{PROMPT_TEMPLATE.format(query_text=pergunta)}''
                                    e dado os dados de resultado:
                                    {resultados_processados_list}, forme uma resposta final completa apenas sobre
                                    os dados recolhidos, não sobre seus conhecimentos gerais ou sobre a query feita.""").content
                return resposta
            else:
                return "Não foi possível encontrar resultados para a pergunta fornecida. Tente reformular a pergunta."

        except Exception as e:
            tentativas += 1
            print(f"Tentativa {tentativas}/{num_max_tentativas} falhou com erro: {e}")
            if tentativas == num_max_tentativas:
                return f"Falha ao executar RAG após {num_max_tentativas} tentativas. Erro final: {e}"
        
    return "Falha inesperada no pipeline RAG."


def close_driver(driver: Driver) -> None:
    '''Metodo que fecha o driver do Neo4j.
    Args:
        driver: Driver; Driver do Neo4j a ser fechado.'''
    driver.close()