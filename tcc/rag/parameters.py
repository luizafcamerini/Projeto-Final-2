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
QUERY: 'MATCH (p:Pessoa)-[:OCUPA]->(n) WHERE n.nome CONTAINS 'SÃO PAULO' RETURN p'""",

"""USER INPUT: 'QUEM SAO OS IRMAOS DE LUIZA?'
QUERY: 'MATCH (p:Pessoa)-[:IRMAO_DE]->(n) WHERE p.nome CONTAINS 'LUIZA' RETURN n'""",

"""USER INPUT: 'QUAL A LIGACAO ENTRE MARCOS E LUIZA?'
QUERY: 'MATCH ligacao=(p:Pessoa)-[*1..]-(n:Pessoa) WHERE p.nome CONTAINS 'MARCOS' AND n.nome CONTAINS 'LUIZA' RETURN ligacao'""",

"""USER INPUT: 'QUE TIPO DE RELACAO EXISTE ENTRE MARCOS E LUIZA?'
QUERY: 'MATCH relacao=(p:Pessoa)-[*1..]-(n:Pessoa) WHERE p.nome CONTAINS 'MARCOS' AND n.nome CONTAINS 'LUIZA' RETURN relacao'""",

"""USER INPUT: 'QUAIS SAO OS PARENTES DE JOAO DA SILVA?'
QUERY: 'MATCH (p:Pessoa)-[r:FILHO_DE | NETO_DE | IRMAO_DE | DESCENDENTE_DE | FAMILIAR_DE | CONJUGE_DE]->(n:Pessoa) WHERE p.nome CONTAINS 'JOAO DA SILVA' RETURN n,r'""",

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