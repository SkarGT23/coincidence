from django import forms

class ArchivoUploadForm(forms.Form):
    archivos = forms.FileField(
        required=True
    )
    busqueda = forms.CharField(max_length=100, required=True)
