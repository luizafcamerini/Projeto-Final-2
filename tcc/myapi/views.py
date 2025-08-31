from django.shortcuts import render, HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("Hello, world. You're at the myapi home.")