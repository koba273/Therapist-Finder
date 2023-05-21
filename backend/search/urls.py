from django.urls import path
from . import views

#url conf
urlpatterns = [
    path('search/',views.return_therapist)
]
