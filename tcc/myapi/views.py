from django.shortcuts import render, redirect
import json
from django.conf import settings
from rag.utils import *

with open(settings.BASE_DIR / 'myapi/static/colors.json') as f:
    cores = json.load(f)

def home(request):
    resposta = None
    if request.method == "POST":
        entrada = request.POST.get("input_pergunta")
        resposta = implementa_rag(get_neo4j_driver(), entrada)
        return render(request, "myapi/home.html", {"cores":cores, "resposta":resposta})
    return render(request, "myapi/home.html", {"cores":cores})