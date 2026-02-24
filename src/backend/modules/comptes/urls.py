from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_comptes, name='liste_comptes'),
    path('update-prix-or/', views.update_prix_or_manual, name='update_prix_or_manual'),
    path('saisie-prix-or/', views.saisie_prix_or_manuel, name='saisie_prix_or_manuel'),
]