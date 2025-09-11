import os, sys, wikipedia
from bs4 import BeautifulSoup
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcc.settings")

class Wiki():
    def __init__(self):
        wikipedia.set_lang("pt")
        
    
    def find_personal_info(self, property: str, page: wikipedia.page)-> list:
        '''Metodo que retorna o valor de uma propriedade da pagina Wikipedia.
        Recebe:
            property: str; Propriedade buscada.
            page: wikipedia.page; Pagina da wikipedia.
        Retorna:
            list; Lista dos nomes dos valores da propriedade encontrada.'''
        soup = BeautifulSoup(page.html(), 'html.parser')
        infobox = soup.find('table', {'class': 'infobox'})
        results = []
        if infobox:
            for tr in infobox.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    if property.lower() in th.get_text().lower():
                        match property.lower():
                            case 'cônjuge' | 'progenitores' | 'filhos(as)':
                                for element in td.find_all('a'):
                                    results.append(element.get_text(" ", strip=True).upper())
                            case 'nascimento':
                                for element in td.find_all('a'):
                                    if element.has_attr("title"):
                                        results.append(element['title'].upper())
                            case _:
                                continue
        return results
    
    
    def nome_contem(self, parcial:str, completo:str):
        palavras = parcial.lower().split()
        nome_completo = completo.lower().split()
        return all(p in nome_completo for p in palavras)