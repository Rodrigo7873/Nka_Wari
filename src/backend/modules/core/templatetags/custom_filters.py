
from django import template
register = template.Library()

@register.filter
def milliers(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", " ")
    except:
        return value