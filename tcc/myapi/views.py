from django.shortcuts import render, redirect
import json
from django.conf import settings
from rag.utils import *

with open(settings.BASE_DIR / 'myapi/static/colors.json') as f:
    cores = json.load(f)

def home(request):
    resposta = None
    if request.method == "POST":
        bool_json = request.POST.get("resposta_json") is not None
        entrada = request.POST.get("input_pergunta")
        resposta = implementa_rag(get_llm(), get_neo4j_driver(), entrada.upper(), bool_json)
        return render(request, "myapi/home.html", {"cores":cores, "resposta":resposta})
    return render(request, "myapi/home.html", {"cores":cores})