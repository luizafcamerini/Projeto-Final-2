from django.shortcuts import render
import json
from django.conf import settings

with open(settings.BASE_DIR / 'myapi/static/colors.json') as f:
    cores = json.load(f)

def home(request):
    return render(request, "myapi/home.html", {"cores":cores})