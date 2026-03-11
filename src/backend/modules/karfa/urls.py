from django.urls import path
from .views.liste import karfa_list, liste_tous_karfa
from .views.form import karfa_create
from .views.detail import detail_karfa
from .views.operations import ajouter_retirer_karfa, toutes_operations
from .views.archives import liste_archives, archiver_karfa, desarchiver_karfa
from .views.export import export_karfa_csv
from .views.pdf import export_karfa_pdf

app_name = 'karfa'  # ← Important pour le namespace

urlpatterns = [
    path('', karfa_list, name='karfa_list'),
    path('creer/', karfa_create, name='karfa_create'),
    path('liste/', liste_tous_karfa, name='liste_tous_karfa'),
    path('<uuid:pk>/', detail_karfa, name='detail_karfa'),
    path('<uuid:pk>/operation/', ajouter_retirer_karfa, name='ajouter_retirer_karfa'),
    path('<uuid:pk>/archiver/', archiver_karfa, name='archiver_karfa'),
    path('export/csv/', export_karfa_csv, name='export_karfa_csv'),
    path('export/pdf/', export_karfa_pdf, name='export_karfa_pdf'),
    path('archives/', liste_archives, name='liste_archives'),
    path('operations/', toutes_operations, name='toutes_operations'),
    path('<uuid:pk>/desarchiver/', desarchiver_karfa, name='desarchiver_karfa'),
]