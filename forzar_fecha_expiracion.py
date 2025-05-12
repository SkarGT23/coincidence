# Script para cambiar la fecha de expiración de la app fácilmente
# Uso: python manage.py shell < forzar_fecha_expiracion.py

from buscador.models import ExpiracionConfig
from datetime import date

# Cambia aquí la fecha que desees
nueva_fecha = date(2025, 6, 12)  # cualquier fecha pasada

exp = ExpiracionConfig.objects.first()
if exp:
    exp.fecha_expiracion = nueva_fecha
    exp.save()
else:
    ExpiracionConfig.objects.create(fecha_expiracion=nueva_fecha)

print(f"Fecha de expiración actualizada a: {nueva_fecha}")
