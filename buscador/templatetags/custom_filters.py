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
    if not argumentos:
        return texto
    pares = []
    for arg in argumentos.split(';'):
        if not arg.strip():
            continue
        if '|' not in arg:
            continue  # ignora argumentos mal formados
        partes = arg.split('|')
        if len(partes) != 2:
            continue
        palabra, color = partes
        pares.append((palabra, color))
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
