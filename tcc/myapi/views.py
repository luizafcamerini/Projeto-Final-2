from django.shortcuts import render, redirect
import json
from django.conf import settings

with open(settings.BASE_DIR / 'myapi/static/colors.json') as f:
    cores = json.load(f)

def home(request):
    resposta = None
    if request.method == "POST":
        entrada = request.POST.get("input_pergunta")
        resposta = f"Você buscou por: {entrada}"
        return render(request, "myapi/home.html", {"cores":cores, "resposta":resposta})
    return render(request, "myapi/home.html", {"cores":cores})