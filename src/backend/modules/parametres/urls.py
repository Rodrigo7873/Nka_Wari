from django.urls import path
from . import views

urlpatterns = [
    path('', views.parametres, name='parametres'),
    path('update-parametres/', views.update_parametres, name='update_parametres'),
    path('about/', views.about, name='about'),
]