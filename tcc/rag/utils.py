from django.conf import settings
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import Text2CypherRetriever

def get_neo4j_driver() -> GraphDatabase.driver:
    '''Metodo que retorna um driver do banco de dados.
    Pega credenciais a partir das settings do django.'''
    return GraphDatabase.driver(
        settings.NEO4J_DATABASE_URL,
        auth=(settings.NEOJ_USERNAME, settings.NEO4J_PASSWORD)
    )

def implementa_rag(driver: GraphDatabase.driver, pergunta:str) -> str:
    '''Metodo que junta todo o pipeline de RAG dada uma pergunta.
    
    Recebe:
        driver: GraphDatabase.driver; Driver do banco de dados.
        pergunta: str; Pergunta pega da interface.
        
    Retorna:
        str; Resposta final do RAG.'''