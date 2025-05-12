from django.shortcuts import render, redirect
from django.conf import settings
from buscador.crypto_utils import descifrar_archivo, reconstruir_contrasena
from datetime import timedelta
import os

# Ofuscada: BOOOM -> B7O3O1O9M
CONTRASENA_OFUSCADA = 'B7O3O1O9M'

def desbloqueo(request):
    error = None
    if request.method == 'POST':
        contrasena_ingresada = request.POST.get('contrasena')
        if contrasena_ingresada == reconstruir_contrasena(CONTRASENA_OFUSCADA):
            # Descifrar views.py si está cifrado
            ruta_views_enc = os.path.join(settings.BASE_DIR, 'buscador', 'views.py.enc')
            if os.path.exists(ruta_views_enc):
                descifrar_archivo(ruta_views_enc)
            # Extender la fecha de expiración 3 meses
            from buscador.models import ExpiracionConfig
            from django.utils import timezone
            exp = ExpiracionConfig.objects.first()
            if exp:
                exp.fecha_expiracion = timezone.now().date() + timedelta(days=90)
                exp.save()
            else:
                ExpiracionConfig.objects.create(fecha_expiracion=timezone.now().date() + timedelta(days=90))
            request.session['desbloqueado'] = True
            return redirect('upload_y_buscar')
        else:
            error = 'Contraseña incorrecta.'
    return render(request, 'desbloqueo.html', {'error': error})
