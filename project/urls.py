# my_project/urls.py (este es el archivo global del proyecto)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # URL para el panel de administración
    path('', include('buscador.urls')),  # Incluye las URLs de la app 'buscador'
]
