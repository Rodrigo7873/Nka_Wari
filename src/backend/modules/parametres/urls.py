from django.urls import path
from . import views

urlpatterns = [
    path('', views.parametres, name='parametres'),
    path('about/', views.about, name='about'),
]