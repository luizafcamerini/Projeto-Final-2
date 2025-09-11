import pandas as pd
import os, sys, django, dotenv
from datetime import datetime
import locale
from .wiki import Wiki
from .database_manager import DatabaseManager

locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tcc.settings")
django.setup()
dotenv.load_dotenv()

wiki= Wiki()
db_manager = DatabaseManager()
csv_path = os.path.join(BASE_DIR, 'pipelines', 'data', '202507_PEP.csv')
if os.path.exists(csv_path):
	df = pd.read_csv(csv_path, encoding='latin1', dtype=str, on_bad_lines='warn', sep=';').fillna('')
else:
	print(f"Arquivo não encontrado: {csv_path}")

db_manager.insere_data(df,wiki)