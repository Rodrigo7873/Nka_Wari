from django.urls import path
from .views.accueil import accueil_comptes
from .views.liste import liste_comptes
from .views.detail import detail_compte
from .views.operations import saisie_prix_or_manuel, update_prix_or_manual, operation_compte
from .views.form import creer_compte, modifier_compte
from .views.archives import liste_archives_comptes, archiver_compte, desarchiver_compte, supprimer_compte
from .views.export import export_comptes_csv
from .views.export_pdf import export_comptes_pdf

app_name = 'comptes'

urlpatterns = [
    path('', accueil_comptes, name='accueil'),
    path('liste/', liste_comptes, name='liste_comptes'),
    path('creer/', creer_compte, name='creer_compte'),
    path('detail/<int:id>/', detail_compte, name='detail_compte'),
    path('modifier/<int:id>/', modifier_compte, name='modifier_compte'),
    path('archives/', liste_archives_comptes, name='liste_archives'),
    path('archiver/<int:id>/', archiver_compte, name='archiver_compte'),
    path('desarchiver/<int:id>/', desarchiver_compte, name='desarchiver_compte'),
    path('supprimer/<int:id>/', supprimer_compte, name='supprimer_compte'),
    path('operation/<int:id>/', operation_compte, name='operation_compte'),
    path('export/csv/', export_comptes_csv, name='export_comptes_csv'),
    path('export/pdf/', export_comptes_pdf, name='export_comptes_pdf'),
    path('update-prix-or/', update_prix_or_manual, name='update_prix_or_manual'),
    path('saisie-prix-or/', saisie_prix_or_manuel, name='saisie_prix_or_manuel'),
]