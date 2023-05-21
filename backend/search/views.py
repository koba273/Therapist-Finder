from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def return_therapist(request):
    return render(request, 'search.html')