# buscador/templatetags/custom_filters.py

from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def mayusculas(texto):
    """Convierte el texto a mayúsculas."""
    return texto.upper() if isinstance(texto, str) else texto


@register.filter(name='resaltar')
def resaltar(texto, argumentos):
    try:
        # argumentos = "palabra1|#ffff00;palabra2|#00ff00;palabra3|#0000ff;palabra4|#ff0000"
        pares = [arg.split('|') for arg in argumentos.split(';')]
    except Exception:
        return texto  # Si hay error en el formato, devuelve el texto original

    if not texto or not pares:
        return texto

    for palabra, color in pares:
        if palabra.strip():
            regex = re.compile(re.escape(palabra), re.IGNORECASE)
            texto = regex.sub(
                lambda match: f'<mark style="background-color: {color}">{match.group(0)}</mark>',
                texto
            )

    return mark_safe(texto)
