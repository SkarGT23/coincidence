from buscador.models import ExpiracionConfig
from django.utils import timezone

exp = ExpiracionConfig.objects.first()
if exp:
    exp.fecha_expiracion = timezone.now().date()
    exp.save()
else:
    ExpiracionConfig.objects.create(fecha_expiracion=timezone.now().date())
print('Fecha de expiración forzada a hoy.')
