from django.conf import settings
from neo4j import GraphDatabase, Driver
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.llm import CohereLLM
from neo4j.graph import Path, Node, Relationship # Importações necessárias
from typing import Any, List, Dict, Union, Tuple
from .parameters import *
import json

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