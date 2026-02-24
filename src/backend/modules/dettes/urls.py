from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_dettes, name='liste_dettes'),
    path('creer/', views.creer_dette, name='creer_dette'),
    path('rembourser/<int:id>/', views.rembourser_dette, name='rembourser_dette'),
    path('export/csv/', views.export_dettes_csv, name='export_dettes_csv'),
]