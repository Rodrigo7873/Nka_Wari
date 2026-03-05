from django.urls import path
from . import views

app_name = 'comptes'

urlpatterns = [
    path('', views.accueil_comptes, name='accueil'),
    path('liste/', views.liste_comptes, name='liste_comptes'),
    path('creer/', views.creer_compte, name='creer_compte'),
    path('detail/<int:id>/', views.detail_compte, name='detail_compte'),
    path('modifier/<int:id>/', views.modifier_compte, name='modifier_compte'),
    path('archives/', views.liste_archives_comptes, name='liste_archives'),
    path('archiver/<int:id>/', views.archiver_compte, name='archiver_compte'),
    path('desarchiver/<int:id>/', views.desarchiver_compte, name='desarchiver_compte'),
    path('supprimer/<int:id>/', views.supprimer_compte, name='supprimer_compte'),
    path('operation/<int:id>/', views.operation_compte, name='operation_compte'),
    path('export/csv/', views.export_comptes_csv, name='export_comptes_csv'),
    path('update-prix-or/', views.update_prix_or_manual, name='update_prix_or_manual'),
    path('saisie-prix-or/', views.saisie_prix_or_manuel, name='saisie_prix_or_manuel'),
]