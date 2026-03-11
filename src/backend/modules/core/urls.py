from django.urls import path
from .views.dashboard import accueil, toutes_operations
from .views.auth import login_view, logout_view, register_view, register_wizard, registration_success
from .views.profil import profil_view, modifier_profil

app_name = 'core'

urlpatterns = [
    # Accueil (Tableau de bord)
    path('', accueil, name='accueil'),
    
    # Authentification
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('register-wizard/', register_wizard, name='register_wizard'),
    path('registration-success/', registration_success, name='registration_success'),
    path('logout/', logout_view, name='logout'),
    
    # Autres fonctionnalités
    path('operations/', toutes_operations, name='toutes_operations'),
    path('profil/', profil_view, name='profil'),
    path('profil/modifier/', modifier_profil, name='modifier_profil'),
]
