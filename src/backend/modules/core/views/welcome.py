from django.shortcuts import render, redirect

def welcome_view(request):
    """
    Page de bienvenue pour les utilisateurs non connectés.
    Si l'utilisateur est déjà connecté, on le redirige vers le tableau de bord.
    """
    if request.user.is_authenticated:
        return redirect('core:accueil')
    return render(request, 'modules/core/welcome.html')
