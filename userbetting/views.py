from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
def index(request):
    context = {

    }
    return render(request, 'userbetting/index.html', context)

def testPage(request):
    context = {

    }
    return render(request, 'userbetting/test.html', context)