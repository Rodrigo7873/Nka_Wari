from django.urls import path
from .views.liste import liste_dettes, toutes_dettes
from .views.form import creer_dette
from .views.operations import (
    rembourser_dette, toutes_operations_dettes, ajouter_paiement, 
    ajouter_dette, encaisser_dette
)
from .views.archives import liste_archives_dettes, archiver_dette
from .views.export import export_dettes_csv
from .views.pdf import export_dettes_pdf
from .views.detail import detail_dette

app_name = 'dettes'

urlpatterns = [
    path('', liste_dettes, name='liste_dettes'),
    path('creer/', creer_dette, name='creer_dette'),
    path('rembourser/<int:id>/', rembourser_dette, name='rembourser_dette'),
    path('ajouter/<int:id>/', ajouter_dette, name='ajouter_dette'),
    path('encaisser/<int:id>/', encaisser_dette, name='encaisser_dette'),
    path('toutes/', toutes_dettes, name='toutes_dettes'),
    path('archives/', liste_archives_dettes, name='liste_archives'),
    path('export/csv/', export_dettes_csv, name='export_dettes_csv'),
    path('export/pdf/', export_dettes_pdf, name='export_dettes_pdf'),
    path('operations/', toutes_operations_dettes, name='toutes_operations_dettes'),
    path('<int:id>/', detail_dette, name='detail_dette'),
    path('<int:id>/archiver/', archiver_dette, name='archiver_dette'),
    path('<int:id>/paiement/', ajouter_paiement, name='ajouter_paiement'),
]