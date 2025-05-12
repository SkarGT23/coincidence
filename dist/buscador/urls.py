# buscador/urls.py (este es el archivo de URLs de la app 'buscador')

from django.urls import path
import importlib
import os
from . import views_desbloqueo

urlpatterns = [
    path('desbloqueo/', views_desbloqueo.desbloqueo, name='desbloqueo'),
]

# Si views.py existe, añade la ruta principal normalmente
views_path = os.path.join(os.path.dirname(__file__), 'views.py')
if os.path.exists(views_path):
    views = importlib.import_module('.views', __package__)
    urlpatterns.append(path('', views.upload_y_buscar, name='upload_y_buscar'))

