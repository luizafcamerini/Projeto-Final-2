# 🧠 Sistema Django + Neo4j — Inteligência para Investigação de Relações

## 📘 Sobre o Projeto
Este projeto é um sistema desenvolvido em **Django** integrado ao **Neo4j**, projetado para armazenar e analisar dados complexos de relacionamentos entre Pessoas Expostas Politicamente, empresas e atividades financeiras.  
O objetivo é apoiar **investigações contra fraude, corrupção e nepotismo**, utilizando grafos para representar conexões e agentes de IA para interpretar perguntas e gerar consultas Cypher automaticamente.

---

## 🧩 Principais Funcionalidades

- 🔗 **Modelagem de grafos no Neo4j:** Pessoas, parentes, sócios, empresas e transações financeiras.
- 🤖 **Componentes IA:**
  - **Leitura e Resposta:** interpreta perguntas em linguagem natural, separando partes vetoriais e de matching exato.
  - **Recolhimento de Dados:** converte consultas em **Cypher queries** e executa no banco.
- 🌐 **Interface Django:** para visualização e gerenciamento das entidades.
- 🧱 **Módulo RAG (Retrieval-Augmented Generation):** combinação de contexto do grafo com respostas geradas por LLMs.
- 🧪 **Módulo de Testes Automatizados** com `unittest`.

---

## ⚙️ Tecnologias Utilizadas

| Categoria | Tecnologia |
|------------|-------------|
| Backend | Python, Jupyter Notebooks |
| Banco de Dados | Neo4j |
| Inteligência Artificial | LLM (Cohere) |
| Linguagem | Python 3.10+ |
| Testes | Python unittest |
| Integração | Neo4j Python Driver & Neomodel |

---

## 🚀 Como Executar o Projeto

### 1. Clonar o repositório
```bash
git clone https://github.com/luizafcamerini/Projeto-Final-2.git
cd tcc
```

### 2. Criar e ativar o ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # (Linux/Mac)
venv\Scripts\activate     # (Windows)
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
Crie um arquivo `.env` com as seguintes variáveis:

```bash
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
NEO4J_DATABASE
LLM_API_KEY
LLM_MODEL
NEO4J_TEST_PASSWORD # Para o banco de dados de teste
NEO4J_TEST_URI      # Para o banco de dados de teste
```
> Estamos considerando que `NEO4J_USERNAME` é o mesmo para ambos os bancos de dados.

### 5. Executar as migrações e iniciar o servidor
```bash
python manage.py migrate
python manage.py runserver
```
Acesse o sistema em:
👉 http://127.0.0.1:8000/

---

## 🧠 Como Funciona o Módulo de IA

1. Usuário faz uma pergunta em linguagem natural.
2. O Agente de Leitura divide a pergunta em partes semânticas e estruturais.
3. O Agente de Recolhimento gera uma query Cypher para buscar os dados relevantes no Neo4j.
4. Os resultados são combinados em um pipeline RAG, retornando uma resposta contextualizada.

Fluxo simplificado:

```
Pergunta → Segmentação → Query Cypher → Busca no Grafo → Resposta RAG
```

## 🧪 Testes
Para rodar os testes:
```bash
python manage.py test --settings=tcc.setting_tests
```
> É importante que você use o módulo ```setting_tests.py``` como configuração para os testes. Nele, há informações sobre um segundo banco de dados, destinado apenas para testes.

## 💬 Contato
Autora: Luíza Camerini

📧 Email: luizacamerini@hotmail.com

🌐 LinkedIn: <https://www.linkedin.com/in/luizacamerini>