import pandas as pd
import os, sys, django, dotenv
import locale
from .database_manager import DatabaseManager

locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcc.settings")
django.setup()
dotenv.load_dotenv()

db_manager = DatabaseManager()
csv_path = os.path.join(BASE_DIR, 'pipelines', 'data', '202507_PEP.csv')
if os.path.exists(csv_path):
	df_completo = pd.read_csv(csv_path, encoding='latin1', dtype=str, on_bad_lines='warn', sep=';').fillna('')
else:
    print(f"Arquivo não encontrado: {csv_path}")
    
if os.path.exists(os.path.join(BASE_DIR, 'pipelines', 'data', '202507_PEP_wiki.csv')):
    os.remove(os.path.join(BASE_DIR, 'pipelines', 'data', '202507_PEP_wiki.csv'))
    print("===Arquivo antigo de PEP com Wiki removido.===\n")

df_atualizado = pd.DataFrame()
print("Inserindo dados...")
for i in range(0, len(df_completo), 10):
    print(f"\nProcessando linhas {i} a {i+10}...\n")
    chunk = df_completo.iloc[i:i+10].copy()
    if "Pagina_Wiki" not in chunk.columns:
        chunk["Pagina_Wiki"] = pd.NA
    df_com_wiki = db_manager.atualiza_paginas_wiki(chunk)
    db_manager.insere_all_pep_org(df_com_wiki)
    db_manager.insere_all_pep_relations(df_com_wiki)
    df_atualizado = pd.concat([df_atualizado, df_com_wiki], ignore_index=True)
    df_atualizado.to_csv(os.path.join(BASE_DIR, 'pipelines', 'data', '202507_PEP_wiki.csv'), sep=";", index=False, encoding="latin1")
