from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        # Toutes les notifications (non lues en priorité)
        notifications = Notification.objects.filter(user=request.user).order_by('is_read', '-created_at')
        return {
            'notifications': notifications,
            'nombre_notifications_non_lues': Notification.objects.filter(user=request.user, is_read=False).count()
        }
    return {
        'notifications': [],
        'nombre_notifications_non_lues': 0
    }
