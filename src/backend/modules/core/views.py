from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('karfa_list')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
            return render(request, 'auth/login.html', {'error': "Identifiants invalides"})
    return render(request, 'auth/login.html')