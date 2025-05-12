# Script seguro para mostrar la contraseña de desbloqueo solo si se introduce la clave maestra
# Uso: python manage.py shell < mostrar_contrasena_segura.py

from getpass import getpass
from decouple import config

CLAVE_MAESTRA = config('CLAVE_MAESTRA', default=None)
if not CLAVE_MAESTRA:
    print('ADVERTENCIA: No se ha definido la variable CLAVE_MAESTRA en el .env')
    exit(1)

clave = getpass('Introduce la clave maestra: ')
if clave == CLAVE_MAESTRA:
    print('Contraseña de desbloqueo:', config('CONTRASENA_DESBLOQUEO'))
    print('Contraseña de bloqueo:', config('CONTRASENA_BLOQUEO'))
    print('Fecha de expiración:', config('FECHA_EXPIRACION'))
else:
    print('Clave incorrecta. Acceso denegado.')
