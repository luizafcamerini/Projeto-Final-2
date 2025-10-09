from django.conf import settings
from neo4j import GraphDatabase, Driver
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.llm import CohereLLM
from neo4j_graphrag.generation import GraphRAG, RagTemplate

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
  "USER INPUT: 'ONDE O MARCOS TRABALHA?' MATCH (p:Pessoa)-[:OCUPA]->(n) WHERE p.nome CONTAINS 'MARCOS' RETURN n",
  "USER INPUT: 'QUE PESSOAS TRABALHAM EM SÃO PAULO?' MATCH (p:Pessoa)-[:OCUPA]->(n) WHERE n.nome CONTAINS 'SÃO PAULO' RETURN n",
  "USER INPUT: 'QUEM SAO OS IRMAOS DE LUIZA?' MATCH (p:Pessoa)-[:IRMAO_DE]->(n) WHERE p.nome CONTAINS 'LUIZA' RETURN n",
  "USER INPUT: 'QUAL A LIGACAO ENTRE MARCOS E LUIZA?' MATCH a=(p:Pessoa)-[*1..]-(n:Pessoa) WHERE p.nome CONTAINS 'MARCOS' AND n.nome CONTAINS 'LUIZA' RETURN a",
  "USER INPUT: 'QUE TIPO DE RELACAO EXISTE ENTRE MARCOS E LUIZA?' MATCH a=(p:Pessoa)-[*1..]-(n:Pessoa) WHERE p.nome CONTAINS 'MARCOS' AND n.nome CONTAINS 'LUIZA' RETURN a",
  "USER INPUT: 'QUAIS SAO OS PARENTES DE JOAO DA SILVA?' MATCH (p:Pessoa)-[:FILHO_DE | NETO_dE | IRMAO_DE | DESCENDENTE_DE | FAMILIAR_DE | CONJUGE_DE]->(n:Pessoa) WHERE p.nome CONTAINS 'JOAO DA SILVA' RETURN n",
  "USER INPUT: 'QUAIS SAO OS IRMAOS DE JOAO DA SILVA QUE TRABALHAM NA EMPRESA ABC?' MATCH (p:Pessoa)-[:IRMAO_DE]->(n)-[:OCUPA]->(o:Organizacao) WHERE p.nome CONTAINS 'JOAO DA SILVA' AND o.nome CONTAINS 'ABC' RETURN n",
]

PROMPT_TEMPLATE = """
    Voce e um agente especialista em devolver dados sobre cargos, familiares de politicos brasileiros e organizacoes brasileiras.
    LEMBRE DISSO: Uma Organizacao pode representar tanto um orgao do governo quanto um estado ou municipio.
    Dada uma pergunta do usuario, voce respondera apenas sobre os dados recolhidos, e nao sobre seus conhecimentos gerais.
    O schema do banco de dados e contexto é este:
    {context}
    Voce pode retornar nos do banco ou caminhos inteiros.
    Caso nao recolha nenhum dado que responda a pergunta, apenas responda:
    'Não foi possível encontrar nenhum resultado no banco de dados. Tente reestruturar sua pergunta.'
    Aqui estao alguns exemplos:
    {examples}
    Siga os exemplos de uppercase em nomes e como as condicionais sao feitas rigorosamente.
    Pergunta do usuario:
    {query_text}
    SEMPRE RESPONDA EM PORTUGUES!!
    Resposta:
""".format(context=NEO4J_SCHEMA, examples=EXEMPLOS, query_text="{query_text}")

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
    '''Metodo que cria e retorna objeto .
    Pega as seguintes credenciais das settings do django:
    - COHERE_API
    - COHERE_MODEL'''
    return CohereLLM(api_key=settings.COHERE_API, 
                     model_name=settings.COHERE_MODEL, 
                     model_params={"temperature":0})

def implementa_rag(llm: CohereLLM, db_driver: Driver, pergunta:str) -> str:
    '''Metodo que junta todo o pipeline de RAG dada uma pergunta.

    Recebe:
        db_driver: Driver; Driver do banco de dados.
        pergunta: str; Pergunta pega da interface.
        llm: CohereLLM; Objeto de LLM do Cohere.

    Retorna:
        str; Resposta final do RAG.'''
    num_max_tentativas = 10
    tentativas = 0
    while(tentativas < num_max_tentativas):
        try:
            retriever = Text2CypherRetriever(driver=db_driver,
                                             neo4j_schema=NEO4J_SCHEMA,
                                             llm=llm,
                                             examples=EXEMPLOS,
                                             custom_prompt=PROMPT_TEMPLATE)
            # search_results = retriever.get_search_results(pergunta)
            # print("Cypher gerado:", search_results.metadata['cypher'])
            # print("Resultados puros do banco:\n", search_results.records)
            print("Resposta do retriever:", retriever.search(query_text=pergunta))
            rag = GraphRAG(retriever=retriever, llm=llm)
            resultado = rag.search(query_text=pergunta)
            return resultado.answer
        except Exception as e:
            tentativas += 1
            print("Tentativa: ", tentativas)
            print("Erro: ", e)
    return 'Não foi possível encontrar nenhum resultado no banco de dados. Tente reestruturar sua pergunta.'