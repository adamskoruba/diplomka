from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def url_spoof(request):
    return render(request, 'url_spoof.html')

def mouse(request):
    return render(request, 'mouse.html')