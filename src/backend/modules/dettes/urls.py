from django.urls import path
from . import views

app_name = 'dettes'

urlpatterns = [
    path('', views.liste_dettes, name='liste_dettes'),
    path('creer/', views.creer_dette, name='creer_dette'),
    path('rembourser/<int:id>/', views.rembourser_dette, name='rembourser_dette'),
    path('toutes/', views.toutes_dettes, name='toutes_dettes'),
    path('archives/', views.liste_archives_dettes, name='liste_archives'),
    path('export/csv/', views.export_dettes_csv, name='export_dettes_csv'),
    path('operations/', views.toutes_operations_dettes, name='toutes_operations_dettes'),
    path('<int:id>/', views.detail_dette, name='detail_dette'),
    path('<int:id>/archiver/', views.archiver_dette, name='archiver_dette'),
    path('<int:id>/paiement/', views.ajouter_paiement, name='ajouter_paiement'),
]