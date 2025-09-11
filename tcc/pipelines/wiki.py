import os, sys, wikipedia, re
from bs4 import BeautifulSoup
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcc.settings")

class Wiki():
    def __init__(self):
        wikipedia.set_lang("pt")
    
    def extrai_anos(self, texto: str) -> list:
        # procura todos os números de 4 dígitos
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
        if infobox:
            for tr in infobox.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    if property.lower() in th.get_text().lower():
                        match property.lower():
                            case 'progenitores' | 'filhos(as)':
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
                                        datas = self.extrai_anos(span.get_text(" ", strip=True).upper().strip("(); ") )
                                        resultados[nome_conjuge] = datas
                                        
                            case _:
                                continue
        return resultados
    
    
    def nome_contem(self, parcial:str, completo:str):
        palavras = parcial.lower().split()
        nome_completo = completo.lower().split()
        return all(p in nome_completo for p in palavras)
    
wiki = Wiki()
pagina_wiki = wikipedia.page(title='luiz inacio lula da silva')
res = wiki.procura_dado_pessoal('cônjuge', pagina_wiki)
print(res)

pagina_wiki = wikipedia.page(title='jair bolsonaro')
res = wiki.procura_dado_pessoal('cônjuge', pagina_wiki)
print(res)

pagina_wiki = wikipedia.page(title='Ângela Portela')
res = wiki.procura_dado_pessoal('cônjuge', pagina_wiki)
print(res)