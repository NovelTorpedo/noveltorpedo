from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'search/pages/home.html')


def search(request):
    return HttpResponse(request.GET['search'])
