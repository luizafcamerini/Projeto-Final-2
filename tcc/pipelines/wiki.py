import os, sys, wikipedia, re, unicodedata
from bs4 import BeautifulSoup
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcc.settings")

class Wiki():
    def __init__(self):
        wikipedia.set_lang("pt")
    
    def extrai_anos(self, texto: str) -> list:
        ''''Metodo que extrai anos de 4 digitos de um texto.
        
        Recebe:
            texto: str; Texto do qual os anos serao extraidos.
            
        Retorna:
            list; Lista de anos extraidos do texto.'''
        anos = re.findall(r'\b\d{4}\b', texto)
        return [int(ano) for ano in anos]
    
    
    def procura_dado_pessoal(self, property: str, page: wikipedia.page)-> dict | list:
        '''Metodo que retorna o valor de uma propriedade da pagina Wikipedia sobre uma pessoa.
        
        Recebe:
            property: str; Propriedade a ser buscada.
            page: wikipedia.page; Pagina da wikipedia da pessoa.
            
        Retorna:
            list | dict; Lista ou dicionario com os valores e datas da propriedade buscada.
            Em caso de houver datas, um dicionario e retornado.'''
        soup = BeautifulSoup(page.html(), 'html.parser')
        infobox = soup.find('table', {'class': 'infobox'})
        resultados = None
        if infobox:
            for tr in infobox.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    if property.lower() in th.get_text().lower():
                        match property.lower():
                            case 'filhos(as)':
                                resultados = []
                                for element in td.find_all('a'):
                                    resultados.append(element.get_text(" ", strip=True).upper())
                                    
                            case 'nascimento':
                                resultados = []
                                for element in td.find_all('a'):
                                    if element.has_attr("title"):
                                        resultados.append(element['title'].upper())
                                        
                            case 'cônjuges' | 'cônjuge':
                                resultados = {} 
                                for a in td.find_all('a'): # a onde ficam os nomes 
                                    nome_conjuge = a.get_text(" ", strip=True).upper() 
                                    resultados[nome_conjuge] = []
                                    span = a.find_next('span')
                                    if span:
                                        datas = self.extrai_anos(span.get_text(" ", strip=True).upper().strip("(); "))
                                        resultados[nome_conjuge] = datas
                                        
                            case 'parentesco' | 'progenitores':
                                resultados = {}
                                for span in td.find_all('span'): # pegando apenas a mae e o pai como progenitores
                                    if span.get_text() == 'Mãe:' or span.get_text() == 'Pai:':
                                        nome_parente = span.find_next()
                                        if nome_parente.name == 'a':
                                            parentesco = span.get_text().upper().strip(":")
                                            resultados[nome_parente.get_text().upper()] = parentesco
                                for a in td.find_all('a'):
                                    nome_parente = a.get_text(" ", strip=True).upper().strip("();")
                                    if nome_parente not in resultados.keys():
                                        parentesco = a.find_next('span').get_text(" ", strip=True).upper().strip("()")
                                    resultados[nome_parente] = parentesco
                                    
                            case 'nome completo':
                                resultados = td.get_text().upper()
                            
                            case _:
                                continue
        return resultados
    
    def remove_acentos(self, texto: str) -> str:
        '''Metodo que remove acentos de um texto.
        
        Recebe:
            texto: str; Texto do qual os acentos serao removidos.
            
        Retorna:
            str; Texto sem acentos.'''
        nfkd = unicodedata.normalize('NFKD', texto)
        return ''.join([c for c in nfkd if not unicodedata.combining(c)])
    
    
    def nome_contem(self, parcial:str, completo:str) -> bool:
        '''Metodo que verifica se o nome parcial esta contido no nome completo de uma pessoa.
        Todos os acentos sao removidos para a comparacao.
        
        Recebe:
            parcial: str; Nome parcial a ser verificado.
            completo: str; Nome completo onde o nome parcial sera verificado.
            
        Retorna:
            bool; True se o nome parcial estiver contido no nome completo, False caso contrario.'''
        parcial = self.remove_acentos(parcial)
        completo = self.remove_acentos(completo)
        palavras = parcial.lower().split()
        nome_completo = completo.lower().split()
        return all(p in nome_completo for p in palavras)


    def valida_pagina(self, pagina, nome):
            '''Metodo que valida se a pagina da Wikipedia encontrada corresponde a pessoa buscada.
            
            Faz ate duas verificacoes:
            1. Compara 'nome' com o título da página
            2. Compara 'nome' com o atributo 'nome completo' (quando existe)
            
            Recebe:
                pagina: wikipedia.page; Pagina da Wikipedia a ser validada.
                nome: str; Nome completo da pessoa.
                
            Retorna:
                bool; True se a pagina for valida, False caso contrario.'''
            if not pagina:
                return False
            nome_completo = self.procura_dado_pessoal("nome completo", pagina)
            if nome_completo:
                return self.nome_contem(nome_completo, nome)
            return self.nome_contem(pagina.title, nome)


    def busca_pagina_wiki(self, nome: str):
        """
        Busca a página da Wikipedia de uma pessoa pelo nome.

        Faz ate duas verificacoes:
        1. Compara 'nome' com o título da página
        2. Compara 'nome' com o atributo 'nome completo' (quando existe)

        Args:
            nome (str): Nome completo da pessoa.

        Returns:
            wikipedia.page | None: Pagina da Wikipedia ou None se nao encontrada.
        """
        try:
            resultados = wikipedia.search(query=nome, results=1)
            if not resultados:
                return None
            titulo = resultados[0]
            try:
                pagina = wikipedia.page(title=titulo)
                if self.valida_pagina(pagina, nome):
                    return pagina
            except wikipedia.exceptions.DisambiguationError as e:
                print("Página ambígua:", titulo)
                for opcao in e.options:
                    try:
                        pagina = wikipedia.page(title=opcao)
                        if self.valida_pagina(pagina, nome):
                            return pagina
                    except wikipedia.exceptions.DisambiguationError:
                        continue
                    except Exception:
                        continue
                print("Nenhuma opção resolvida para:", titulo)
                return None

        except Exception as ex:
            print("Erro inesperado:", ex)
            return None


if __name__ == "__main__":
    wiki = Wiki()
    pagina = wiki.busca_pagina_wiki("LUIZ INACIO LULA DA SILVA")
    print('tem pagina? ', True if pagina else False)
    if pagina:
        res = wiki.procura_dado_pessoal("nome completo", pagina)
        print(res)