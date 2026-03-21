from django.shortcuts import redirect
from django.urls import reverse
from .models.pin import PinUtilisateur

class PinMiddleware:
    """
    Middleware de sécurité PIN.
    L'utilisateur reste authentifié 30 jours, mais le PIN est demandé à chaque ouverture.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        excluded_paths = ['/login/', '/register/', '/logout/', '/pin/', '/admin/', '/static/', '/media/']
        
        if request.user.is_authenticated:
            # Technique pour détecter une nouvelle ouverture du navigateur :
            # On utilise un cookie 'pin_browser_session' qui expire à la fermeture du navigateur.
            # Si le cookie est absent, on considère que c'est une nouvelle ouverture.
            pin_browser_session = request.COOKIES.get('pin_browser_session')
            
            if not pin_browser_session:
                # Nouvelle ouverture -> Invalider la session PIN (pas le login)
                request.session['pin_valide'] = False
                # Reconfirmer l'expiration globale de 30 jours pour le navigateur
                from django.conf import settings
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                request.session.modified = True

            current_path = request.path
            is_excluded = any(current_path.startswith(p) for p in excluded_paths)
            
            if not is_excluded:
                if not request.session.get('pin_valide'):
                    try:
                        pin_obj = PinUtilisateur.objects.get(user=request.user)
                        if pin_obj.pin_hash:
                            return redirect('core:verifier_pin')
                        else:
                            return redirect('core:definir_pin')
                    except PinUtilisateur.DoesNotExist:
                        return redirect('core:definir_pin')
        
        response = self.get_response(request)
        return response
