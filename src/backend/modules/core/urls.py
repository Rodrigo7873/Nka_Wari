from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('operations/', views.toutes_operations, name='toutes_operations'),
]
