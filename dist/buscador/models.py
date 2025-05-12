from django.db import models

# formularios para subir archivos

class ExpiracionConfig(models.Model):
    fecha_expiracion = models.DateField()

    def __str__(self):
        return f"Expira el {self.fecha_expiracion}"

class Archivo(models.Model):
    archivo = models.FileField(upload_to='archivos/')
    nombre = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.nombre or self.archivo.name
