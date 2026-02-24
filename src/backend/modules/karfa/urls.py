from django.urls import path
from . import views

app_name = 'karfa'  # ← Important pour le namespace

urlpatterns = [
    path('', views.karfa_list, name='karfa_list'),
    path('creer/', views.karfa_create, name='karfa_create'),
    path('liste/', views.liste_tous_karfa, name='liste_tous_karfa'),
    path('<uuid:pk>/', views.detail_karfa, name='detail_karfa'),
    path('<uuid:pk>/operation/', views.ajouter_retirer_karfa, name='ajouter_retirer_karfa'),
    path('<uuid:pk>/archiver/', views.archiver_karfa, name='archiver_karfa'),
    path('export/csv/', views.export_karfa_csv, name='export_karfa_csv'),
    path('archives/', views.liste_archives, name='liste_archives'),
    path('operations/', views.toutes_operations, name='toutes_operations'),
    path('<uuid:pk>/desarchiver/', views.desarchiver_karfa, name='desarchiver_karfa'),
]