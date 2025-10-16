from django.conf import settings
from neo4j import GraphDatabase, Driver
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.llm import VertexAILLM
from langchain_google_genai import ChatGoogleGenerativeAI
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
    Siga os exemplos de uppercase e acentos em nomes (se houver) e como as condicionais sao feitas rigorosamente e
    NAO USE NENHUM TIPO DE FUNCAO AUXILIAR NA QUERY., como relationships() ou relationship().
    Atente-se como são retornados caminhos entre nós.
    Pergunta do usuario:
    {query_text}
    SEMPRE RESPONDA EM PORTUGUES!
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
    
# def get_llm() -> CohereLLM:
#     '''Metodo que cria e retorna objeto CohereLLM.
#     Pega as seguintes credenciais das settings do django:
#     - LLM_API_KEY
#     - LLM_MODEL'''
#     return CohereLLM(api_key=settings.LLM_API_KEY, 
#                      model_name=settings.LLM_MODEL, 
#                      model_params={"temperature":0})

def get_llm() -> ChatGoogleGenerativeAI:
    '''Metodo que cria e retorna objeto CohereLLM.
    Pega as seguintes credenciais das settings do django:
    - LLM_API_KEY'''
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key = settings.LLM_API_KEY)

def implementa_rag(llm: ChatGoogleGenerativeAI, db_driver: Driver, pergunta:str) -> str:
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
            resultados_query = retriever.get_search_results(pergunta)
            print("Cypher gerado:", resultados_query.metadata['cypher'])
            # print("Resultados puros do banco:\n", resultados_query.records)
            print("Resposta do retriever:", retriever.search(query_text=pergunta))
            if resultados_query:
                print("Resultados query: \n",resultados_query)
                resultados_query = resultados_query.records
                resposta = llm.invoke(f"""Dado o contexto:
                                      ''{PROMPT_TEMPLATE.format(query_text=pergunta)}''
                                      e dado os dados de resultado:
                                      {resultados_query}, forme uma resposta final completa apenas sobre
                                      os dados recolhidos, não sobre seus conhecimentos gerais ou sobre a query feita.""").content
                return resposta
            else: raise Exception
        except Exception as e:
            tentativas += 1
            print("Tentativa: ", tentativas)
            print("Erro: ", e)
    return 'Não foi possível encontrar nenhum resultado no banco de dados. Tente reestruturar sua pergunta.'