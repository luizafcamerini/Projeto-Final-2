import pandas as pd
import os, sys, django, neomodel, dotenv, wikipedia
from datetime import datetime
import locale
from .wiki import Wiki
locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcc.settings")
django.setup()
dotenv.load_dotenv()
from myapi.models import Pessoa, Organizacao

class DatabaseManager():
    def __init__(self):
        pass
    
    def insere_pep(self, nome, cpf, cnpj) -> Pessoa:
        try:
            pep = Pessoa.nodes.get(nome=nome)
        except neomodel.DoesNotExist:
            pep = Pessoa(nome=nome, 
                        cpf=cpf, 
                        cnpj=cnpj).save()
            print(f'Pessoa {nome} inserida com sucesso.')
        return pep


    def insere_organizacao(self, nome, cnpj) -> Organizacao:
        try:
            org = Organizacao.nodes.get(nome=nome)
        except neomodel.DoesNotExist:
            org = Organizacao(nome=nome, cnpj=cnpj).save()
            print(f'Organização {nome} inserida com sucesso.')
        return org


    def relaciona_pessoa_organizacao(self,pessoa: Pessoa, org:Organizacao, cargo, inicio, fim):
        if not pessoa.cargo.is_connected(org):
            try:
                pessoa.cargo.connect(org, {'cargo': cargo,
                                            'data_inicio': inicio, 
                                            'data_fim': fim,
                                            'grau_precisao': 5})
                print(f'Relação entre {pessoa.nome} e {org.nome} criada com sucesso.')
            except AttributeError as e:
                pass


    def atualiza_nascimento(self, pessoa: Pessoa, wiki:Wiki, pagina_wiki: wikipedia.page):
        data_nascimento = wiki.find_personal_info('Nascimento', pagina_wiki)
        if len(data_nascimento) >= 2:
            try:
                nascimento = datetime.strptime(data_nascimento[0] + ' DE ' + data_nascimento[1], "%d DE %B DE %Y")
                pessoa.data_nascimento = nascimento
                pessoa.save()
            except Exception as e:
                pass
        
        
    def atualiza_conjuges(self, pessoa: Pessoa, wiki:Wiki, pagina_wiki: wikipedia.page):
        conjuges = wiki.find_personal_info('Côjunge', pagina_wiki)
        if conjuges:
            for conjuge in conjuges:
                try:
                    conjuge_pessoa = Pessoa.nodes.get(nome=conjuge)
                except neomodel.DoesNotExist:
                    conjuge_pessoa = self.insere_pep(conjuge, None, None, None)
                if not pessoa.conjuge.is_connected(conjuge_pessoa):
                    pessoa.conjuge.connect(conjuge_pessoa, {'grau_precisao': 4})
                    print(f'Conjuge de {pessoa.nome} inserido e conectado com sucesso!')


    def atualiza_filhos(self, pessoa: Pessoa, wiki:Wiki, pagina_wiki: wikipedia.page):
        filhos = wiki.find_personal_info('Filhos(as)',pagina_wiki)
        if filhos:
            for filho in filhos:
                try:
                    filho_pessoa = Pessoa.nodes.get(nome=filho)
                except neomodel.DoesNotExist:
                    filho_pessoa = self.insere_pep(filho, None, None)
                if not filho_pessoa.filho.is_connected(pessoa):
                    filho_pessoa.filho.connect(pessoa, {'grau_precisao': 4})
                    print(f'Filho de {pessoa.nome} inserido e conectado com sucesso!')
                    
    
    def atualiza_progenitores(self, pessoa: Pessoa, wiki:Wiki, pagina_wiki: wikipedia.page):
        progenitores = wiki.find_personal_info('Progenitores',pagina_wiki)
        if progenitores:
            for progenitor in progenitores:
                try:
                    proge_pessoa = Pessoa.nodes.get(nome=progenitor)
                except neomodel.DoesNotExist:
                    proge_pessoa = self.insere_pep(progenitor, None, None)
                if not pessoa.filho.is_connected(proge_pessoa):
                    pessoa.filho.connect(proge_pessoa, {'grau_precisao': 4})
                    print(f'Progenitor de {pessoa.nome} inserido e conectado com sucesso!')


    def insere_data(self, df:pd.DataFrame, wiki: Wiki):
        '''Metodo que insere todas as PEPs, suas organizacoes, seus cargos e seus dados pessoais.
        Recebe:
            df: pandas.Dataframe; Dataframe que possui dados PEPs, organizacoes e cargos.
            wiki: Wiki; Classe que procura os dados pessoais de cada PEP.'''
        for _, row in df.iterrows():
            nome = row['Nome_PEP']
            cpf = row['CPF']
            cnpj = None
            org_nome = row['Nome_Órgão']
            org_cnpj = None
            cargo_nome = row['Descrição_Função']
            inicio = datetime.strptime(row['Data_Início_Exercício'], "%d/%m/%Y") if "/" in row['Data_Início_Exercício'] else None
            fim = datetime.strptime(row['Data_Fim_Exercício'], "%d/%m/%Y") if "/" in row['Data_Fim_Exercício'] else None
            try:
                pessoa = Pessoa.nodes.get(nome=nome)
            except neomodel.DoesNotExist:
                pessoa = self.insere_pep(nome, cpf, cnpj)
            busca_wiki = wikipedia.search(query=nome,results=1)
            if len(busca_wiki) == 1 :
                if wiki.nome_contem(parcial=busca_wiki[0], completo=nome):
                    pagina_wiki = wikipedia.page(title=nome)
                    self.atualiza_nascimento(pessoa, wiki, pagina_wiki)
                    self.atualiza_conjuges(pessoa, wiki, pagina_wiki)
                    self.atualiza_filhos(pessoa, wiki, pagina_wiki)
                    self.atualiza_progenitores(pessoa, wiki, pagina_wiki)
            org = self.insere_organizacao(org_nome, org_cnpj)
            self.relaciona_pessoa_organizacao(pessoa, org, cargo=cargo_nome, inicio=inicio, fim=fim)