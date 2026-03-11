
from django import template
register = template.Library()

@register.filter
def milliers(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", " ")
    except:
        return value

@register.filter
def intspace(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", " ")
    except:
        return value

from django.utils import timezone

@register.filter
def get_class(obj):
    return obj.__class__.__name__

@register.filter
def temps_relatif(value):
    if not value: return ""
    now = timezone.now()
    diff = now - value
    if diff.days > 0:
        if diff.days == 1: return "hier"
        return f"il y a {diff.days} jours"
    elif diff.seconds >= 3600:
        heures = diff.seconds // 3600
        return f"il y a {heures}h"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"il y a {minutes}m"
    else:
        return "à l'instant"