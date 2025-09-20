import pandas as pd
import os, sys, django, neomodel, dotenv, wikipedia
from datetime import datetime
import locale
from .wiki import Wiki
from .relatives import RELATIVES
locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcc.settings")
django.setup()
dotenv.load_dotenv()
from myapi.models import Pessoa, Organizacao

class DatabaseManager():
    def __init__(self):
        self.wiki = Wiki()
    
    def insere_pep(self, nome, cpf, cnpj) -> Pessoa:
        '''Metodo que insere uma pessoa PEP no banco de dados, caso ela nao exista.
        
        Recebe:
            nome: str; Nome completo da pessoa.
            cpf: str; CPF da pessoa.
            cnpj: str; CNPJ da pessoa.
            
        Retorna:
            Pessoa; A pessoa inserida ou ja existente.'''
        try:
            pep = Pessoa.nodes.get(nome=nome)
        except neomodel.DoesNotExist:
            pep = Pessoa(nome=nome, 
                        cpf=cpf, 
                        cnpj=cnpj).save()
            print(f'Pessoa {nome} inserida com sucesso.')
        return pep


    def insere_organizacao(self, nome, cnpj) -> Organizacao:
        '''Metodo que insere uma organizacao no banco de dados, caso ela nao exista.
        
        Recebe:
            nome: str; Nome da organizacao.
            cnpj: str; CNPJ da organizacao.
            
        Retorna:
            Organizacao; A organizacao inserida ou ja existente.'''
        try:
            org = Organizacao.nodes.get(nome=nome)
        except neomodel.DoesNotExist:
            org = Organizacao(nome=nome, cnpj=cnpj).save()
            print(f'Organização {nome} inserida com sucesso.')
        return org
    

    def relaciona_pessoa_organizacao(self,pessoa: Pessoa, org:Organizacao, cargo, inicio, fim):
        '''Metodo que relaciona uma pessoa e uma organizacao atraves de um cargo.
        
        Recebe:
            pessoa: Pessoa; A pessoa em questao.
            org: Organizacao; A organizacao em questao.
            cargo: str; 
        '''
        if not pessoa.cargo.is_connected(org):
            try:
                pessoa.cargo.connect(org, {'cargo': cargo,
                                            'data_inicio': inicio, 
                                            'data_fim': fim,
                                            'grau_precisao': 5})
                print(f'Relação entre {pessoa.nome} e {org.nome} criada com sucesso.')
            except AttributeError as e:
                pass


    def atualiza_nascimento(self, pessoa: Pessoa, pagina_wiki: wikipedia.page):
        '''Metodo que procura e atualiza o nascimento de uma pessoa dada.
        
        Recebe:
            pessoa: Pessoa; A pessoa em questao.
            pagina_wiki: wikipedia.page; Pagina da Wikipedia da pessoa dada.
        '''
        data_nascimento = self.wiki.procura_dado_pessoal('Nascimento', pagina_wiki)
        if data_nascimento:
            if len(data_nascimento) >= 2:
                try:
                    nascimento = datetime.strptime(data_nascimento[0] + ' DE ' + data_nascimento[1], "%d DE %B DE %Y")
                    pessoa.data_nascimento = nascimento
                    pessoa.save()
                except Exception as e:
                    pass
        
        
    def atualiza_conjuges(self, pessoa: Pessoa, pagina_wiki: wikipedia.page):
        '''Metodo que procura, insere e conecta os conjuges de uma pessoa dada.
        
        Recebe:
            pessoa: Pessoa; Pessoa da qual sao os conjuges.
            pagina_wiki: wikipedia.page; Pagina da Wikipedia da pessoa dada.
        '''
        print(f'Procurando cônjuge(s) de {pessoa.nome}...')
        conjuges = self.wiki.procura_dado_pessoal('Côjunges', pagina_wiki)
        conjuge = self.wiki.procura_dado_pessoal('Côjunge', pagina_wiki)
        if conjuges or conjuge:
            conjuge_dict = conjuge if conjuge else conjuges
            for c in conjuge_dict.keys():
                conjuge_pessoa = self.encontra_pessoa_por_nome(c)
                if not conjuge_pessoa:
                    conjuge_pessoa = self.insere_pep(c, None, None, None)
                if not pessoa.conjuge.is_connected(conjuge_pessoa):
                    pessoa.conjuge.connect(conjuge_pessoa, {'grau_precisao': 3, 
                                                            'ano_inicio': conjuge_dict[c][0] if len(conjuge_dict[c]) >= 1 else None,
                                                             'ano_fim': conjuge_dict[c][1] if len(conjuge_dict[c]) >= 2 else None})
                    print(f'Conjuge de {pessoa.nome} inserido e conectado com sucesso!')


    def atualiza_filhos(self, pessoa: Pessoa, pagina_wiki: wikipedia.page):
        '''Metodo que procura, insere e conecta os filhos(as) de uma pessoa dada.
        
        Recebe:
            pessoa: Pessoa; Pessoa da qual sao os filhos.
            pagina_wiki: wikipedia.page; Pagina da Wikipedia da pessoa dada.
        '''
        print(f'Procurando filho(s) de {pessoa.nome}...')
        filhos = self.wiki.procura_dado_pessoal('Filhos(as)',pagina_wiki)
        if filhos:
            for filho in filhos:
                if self.encontra_pessoa_por_nome(filho):
                    filho_pessoa = self.encontra_pessoa_por_nome(filho)
                else: filho_pessoa = self.insere_pep(filho, None, None)
                if not filho_pessoa.filho.is_connected(pessoa):
                    filho_pessoa.filho.connect(pessoa, {'grau_precisao': 4})
                    print(f'Filho de {pessoa.nome} inserido e conectado com sucesso!')
                    
    
    def atualiza_progenitores(self, pessoa: Pessoa, pagina_wiki: wikipedia.page):
        '''Metodo que procura, insere e conecta os progenitores de uma pessoa dada.
        
        Recebe:
            pessoa: Pessoa; Pessoa da qual sao os progenitores.
            pagina_wiki: wikipedia.page; Pagina da Wikipedia da pessoa dada.
        '''
        print(f'Procurando progenitor(es) de {pessoa.nome}...')
        progenitores = self.wiki.procura_dado_pessoal('Progenitores',pagina_wiki)
        if progenitores:
            for progenitor in progenitores.keys():
                if self.encontra_pessoa_por_nome(progenitor):
                    proge_pessoa = self.encontra_pessoa_por_nome(progenitor)
                else: proge_pessoa = self.insere_pep(progenitor, None, None)
                try:
                    relacao_attr = RELATIVES[progenitores[progenitor]]
                except Exception as e:
                    relacao_attr = 'familiar'
                relacao = getattr(pessoa, relacao_attr) # RelationshipManager: relacao = pessoa.mae ou pessoa.pai
                if not relacao.is_connected(proge_pessoa):
                    relacao.connect(proge_pessoa, {'grau_precisao': 4})
                    print(f'Progenitor de {pessoa.nome} inserido e conectado com sucesso!')
                    
    
    def atualiza_parentes(self, pessoa: Pessoa, pagina_wiki: wikipedia.page):
        ''''Metodo que procura, insere e conecta outros parentes (irmaos e meio-irmaos) da pessoa dada.
        
        Recebe:
            pessoa: Pessoa; Pessoa da qual sao os parentes.
            pagina_wiki: wikipedia.page; Pagina da Wikipedia da pessoa dada.'''
        print(f'Procurando parente(s) de {pessoa.nome}...')
        parentes = self.wiki.procura_dado_pessoal('Parentesco', pagina_wiki)
        if parentes:
            for parente in parentes.keys():
                if self.encontra_pessoa_por_nome(parente):
                    parente_pessoa = self.encontra_pessoa_por_nome(parente)
                else: parente_pessoa = self.insere_pep(parente, None, None)
                try:
                    relacao_attr = RELATIVES[parentes[parente]]
                except Exception as e:
                    relacao_attr = 'familiar'
                relacao = getattr(pessoa, relacao_attr)
                if not relacao.is_connected(parente_pessoa):
                    relacao.connect(parente_pessoa, {'grau_precisao': 3})
                    print(f'Parente de {pessoa.nome} inserido e conectado com sucesso!')
                    
    
    def encontra_pessoa_por_nome(self, parcial: str) -> Pessoa | None:
        """
        Metodo que procura a primeira Pessoa cujo nome contém todas as palavras do nome parcial.
        
        Recebe:
            parcial: str; Nome parcial a ser verificado.
            
        Retorna:
            Pessoa | None; A pessoa encontrada ou None se nao existir.
        """
        for pessoa in Pessoa.nodes:  # percorre todas as pessoas
            if self.wiki.nome_contem(parcial, pessoa.nome):
                return pessoa
        return None
    
    
    def atualiza_paginas_wiki(self, df:pd.DataFrame) -> pd.DataFrame:
        '''Metodo que atualiza a coluna Pagina_Wiki do dataframe com os IDs das paginas da Wikipedia.
        Caso haja conflito de nomes, a coluna recebe 'CONFLITANTE'. Caso nao encontre, recebe 'NÃO ENCONTRADA'.
        
        Recebe:
            df: pandas.Dataframe; Dataframe que possui dados PEPs.
            
        Retorna:
            pandas.Dataframe; Dataframe atualizado com os IDs das paginas da Wikipedia.
        '''
        df = df.copy()
        print("Iniciando atualizacao de paginas na Wikipedia no dataframe...")
        for idx, row in df.iterrows():
            nome = row['Nome_PEP']
            if not pd.isna(row['Pagina_Wiki']):
                continue
            print(f'Procurando Wiki de {nome}...')
            pagina_wiki = self.wiki.busca_pagina_wiki(nome)
            if pagina_wiki:
                mascara_bool = df['Pagina_Wiki'] == pagina_wiki.pageid
                if any(mascara_bool):
                    df.loc[mascara_bool, 'Pagina_Wiki'] = 'CONFLITANTE'
                    print(f"Página de {nome} conflitante com {df.loc[mascara_bool, 'Nome_PEP'].values}")
                else:
                    df.loc[idx, 'Pagina_Wiki'] = pagina_wiki.pageid
                    print('Pagina atualizada: \n', row)
            else:
                df.loc[idx, 'Pagina_Wiki'] = 'NÃO ENCONTRADA'
                print(f'Página da Wikipedia para {nome} não encontrada.')
                continue
        return df
    
    
    def wiki_valido(self, valor):
        '''Metodo que verifica se o valor da coluna Pagina_Wiki e valido.
        Verifica se o valor nao e nulo, nao e 'CONFLITANTE' e nao e 'NAO ENCONTRADA'.
        
        Recebe:
            valor: str | int; Valor da coluna Pagina_Wiki.
        
        Retorna:
            bool; True se o valor for valido, False caso contrario.'''
        return not pd.isna(valor) and valor not in ['CONFLITANTE', 'NÃO ENCONTRADA', '']
        

    def insere_all_pep_org(self, df:pd.DataFrame):
        '''Metodo que insere todas as PEPs, organizacoes e seus cargos.
        
        Recebe:
            df: pandas.Dataframe; Dataframe que possui dados PEPs, organizacoes e cargos.
            wiki: Wiki; Classe que procura os dados pessoais de cada PEP.'''
        print("Iniciando insercao de PEPs e organizaoes...")
        for _, row in df.iterrows():
            cpf = row['CPF']
            cnpj = None
            cargo_nome = row['Descrição_Função']
            inicio = datetime.strptime(row['Data_Início_Exercício'], "%d/%m/%Y") if "/" in row['Data_Início_Exercício'] else None
            fim = datetime.strptime(row['Data_Fim_Exercício'], "%d/%m/%Y") if "/" in row['Data_Fim_Exercício'] else None
            nome = row['Nome_PEP']
            if self.wiki_valido(row['Pagina_Wiki']):
                pessoa = self.insere_pep(nome, cpf, cnpj)
                pagina_wiki = self.wiki.busca_pagina_wiki_id(int(row['Pagina_Wiki']))
                self.atualiza_nascimento(pessoa, pagina_wiki)
                self.atualiza_conjuges(pessoa, pagina_wiki)
                self.atualiza_filhos(pessoa, pagina_wiki)
                self.atualiza_progenitores(pessoa, pagina_wiki)
                self.atualiza_parentes(pessoa, pagina_wiki)
                org = self.insere_organizacao(row['Nome_Órgão'], None)
                self.relaciona_pessoa_organizacao(pessoa, org, cargo=cargo_nome, inicio=inicio, fim=fim)
                
            
    def insere_all_pep_relations(self, df:pd.DataFrame):
        '''Metodo que insere todas os familiares de todas as PEPs.
        
        Recebe:
            df: pandas.Dataframe; Dataframe que possui dados PEPs e suas paginas wiki.
            wiki: Wiki; Classe que procura os dados pessoais de cada PEP.'''
        for _, row in df.iterrows():
            if not self.wiki_valido(row['Pagina_Wiki']):
                continue
            else:
                print("\nIniciando inserção de familiares...\n")
                pessoa = self.encontra_pessoa_por_nome(row['Nome_PEP'])
                if not pessoa:
                    pessoa = self.insere_pep(row['Nome_PEP'], row['CPF'], None)
                pagina_wiki = wikipedia.page(pageid=int(row['Pagina_Wiki']))
                if pagina_wiki:
                    self.atualiza_conjuges(pessoa, pagina_wiki)
                    self.atualiza_filhos(pessoa, pagina_wiki)
                    self.atualiza_progenitores(pessoa, pagina_wiki)
                    self.atualiza_parentes(pessoa, pagina_wiki)
                
                
    