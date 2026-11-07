from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'index.html')

def url_spoof(request):
    return render(request, 'url_spoof.html')

def mouse(request):
    return render(request, 'mouse.html')


@csrf_exempt
def mouse_log(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data, flush=True)

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "POST required"})