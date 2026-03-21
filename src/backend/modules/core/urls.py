from django.urls import path
from .views.dashboard import accueil, toutes_operations, offline_view, notifications_view, service_worker, manifest_view
from .views.auth import (
    login_view, logout_view, register_view, register_wizard, registration_success,
    password_reset_choice, password_reset_identifier, password_reset_question, password_reset_confirm
)
from .views.profil import profil_view, modifier_profil, changer_mot_de_passe, changer_pin
from .views.pin import definir_pin, verifier_pin, reinitialiser_pin, pin_oublie
from .views.welcome import welcome_view

app_name = 'core'

urlpatterns = [
    # Accueil (Landing / Tableau de bord)
    path('', welcome_view, name='welcome'),
    path('accueil/', accueil, name='accueil'),
    
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
    path('changer-mot-de-passe/', changer_mot_de_passe, name='changer_mot_de_passe'),
    path('changer-pin/', changer_pin, name='changer_pin'),
    path('offline/', offline_view, name='offline'),
    path('notifications/', notifications_view, name='notifications'),
    path('sw.js', service_worker, name='service_worker'),
    path('manifest.json', manifest_view, name='manifest_json'),
    
    # Réinitialisation de mot de passe
    path('password-reset/', password_reset_choice, name='password_reset_choice'),
    path('password-reset/identifier/', password_reset_identifier, name='password_reset_identifier'),
    path('password-reset/question/', password_reset_question, name='password_reset_question'),
    path('password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm_token'),
    
    # Sécurité PIN
    path('pin/definir/', definir_pin, name='definir_pin'),
    path('pin/verifier/', verifier_pin, name='verifier_pin'),
    path('pin/reinitialiser/', reinitialiser_pin, name='reinitialiser_pin'),
    path('pin/oublie/', pin_oublie, name='pin_oublie'),
    
    # Dashboard alias
    path('dashboard/', accueil, name='dashboard'),
]
