from django.utils import timezone
from django.conf import settings
import logging
import re
import shlex
from io import BytesIO

def verificar_licencia():
    fecha_actual = timezone.now().date()
    fecha_expiracion = timezone.datetime.strptime(settings.FECHA_EXPIRACION, "%Y-%m-%d").date()
    return fecha_actual >= fecha_expiracion

from django.shortcuts import render
from django.core.exceptions import ValidationError
from django import template
from django.utils.safestring import mark_safe

from .forms import ArchivoUploadForm

import fitz  # PyMuPDF
import pandas as pd
from docx import Document
import unicodedata

from odf.opendocument import load
from odf.text import P
from odf import teletype

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

register = template.Library()

def normalizar_texto(texto):
    texto = texto.strip().lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = texto.upper()
    texto = re.sub(r'\s+', ' ', texto)
    return texto

@register.filter(name='resaltar')
def resaltar(texto, argumentos):
    """
    Resalta en HTML los términos en el texto según los argumentos tipo: termino|#color;termino2|#color2
    """
    patrones = []
    for arg in argumentos.split(";"):
        if not arg.strip():
            continue
        termino, color = arg.split("|")
        regex = crear_regex_insensible(termino)
        patrones.append((re.compile(rf"({regex})", re.IGNORECASE), color))

    def aplicar_resaltado(patrones, texto):
        posiciones_ocupadas = []

        def ya_ocupado(start, end):
            return any(s < end and start < e for s, e in posiciones_ocupadas)

        resultado = texto
        offset = 0
        for patron, color in patrones:
            for match in patron.finditer(texto):
                start, end = match.start(), match.end()
                if ya_ocupado(start, end):
                    continue
                span = f'<span style="background-color:{color}">{match.group(0)}</span>'
                resultado = resultado[:start + offset] + span + resultado[end + offset:]
                offset += len(span) - (end - start)
                posiciones_ocupadas.append((start, end))
        return resultado

    return aplicar_resaltado(patrones, texto)

def upload_y_buscar(request):
    logger.debug("Iniciando la vista upload_y_buscar")
    resultados = None
    archivos = request.session.get('archivos', [])
    busqueda = ''
    argumentos = ''

    if request.method == 'POST':
        form = ArchivoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            nuevos_archivos = request.FILES.getlist('archivos')
            archivos.extend([archivo.name for archivo in nuevos_archivos])
            request.session['archivos'] = archivos

            busqueda = form.cleaned_data['busqueda']
            resultados = procesar_archivos(nuevos_archivos, busqueda)
            colores = ['#ffff00', '#00ff00', '#0000ff', '#ff0000', '#ff69b4', '#ffa500', '#808080', '#87ceeb']  # amarillo, verde, azul, rojo, rosa, naranja, gris, azul celeste
            terminos = shlex.split(busqueda.strip())
            argumentos = ';'.join(f"{termino}|{colores[i % len(colores)]}" for i, termino in enumerate(terminos))
        else:
            logger.debug("Formulario inválido")
    else:
        form = ArchivoUploadForm()

    return render(request, 'buscador/buscar.html', {
        'form': form,
        'resultados': resultados,
        'archivos': archivos,
        'busqueda': busqueda,
        'argumentos': argumentos
    })

def obtener_contexto(texto, terminos_originales):
    palabras = texto.split()
    normalizado = normalizar_texto(texto)
    for termino in terminos_originales:
        termino_norm = normalizar_texto(termino)
        if termino_norm in normalizado:
            for i, palabra in enumerate(palabras):
                if termino_norm in normalizar_texto(palabra):
                    inicio = max(i - 3, 0)
                    fin = min(i + 4, len(palabras))
                    return " ".join(palabras[inicio:fin])
    return ""

def procesar_archivos(archivos, busqueda):
    resultados = []
    try:
        terminos_originales = shlex.split(busqueda.strip())
        terminos_normalizados = [normalizar_texto(t) for t in terminos_originales]
    except ValueError as e:
        raise ValidationError("Error en los términos de búsqueda: usa comillas correctamente.")

    if not terminos_originales:
        raise ValidationError("Debe ingresar al menos un término de búsqueda.")

    colores = ['#ffff00', '#00ff00', '#0000ff', '#ff0000']
    argumentos = ';'.join(f"{termino}|{colores[i % len(colores)]}" for i, termino in enumerate(terminos_originales))
    logger.debug(f"Argumentos para resaltar: {argumentos}")

    for archivo in archivos:
        resultado = {
            'archivo': archivo.name,
            'tipo': archivo.content_type,
            'total': 0,
            'detalles': [],
            'contenido': ''
        }

        try:
            if archivo.name.endswith('.pdf'):
                contenido, coincidencias = extraer_texto_pdf(archivo, terminos_normalizados, terminos_originales)
            elif archivo.name.endswith('.txt'):
                contenido, coincidencias = extraer_texto_txt(archivo, terminos_normalizados, terminos_originales)
            elif archivo.name.endswith('.xlsx'):
                contenido, coincidencias = extraer_texto_excel(archivo, terminos_normalizados, terminos_originales)
            elif archivo.name.endswith('.docx'):
                contenido, coincidencias = extraer_texto_docx(archivo, terminos_normalizados, terminos_originales)
            elif archivo.name.endswith('.rtf'):
                contenido, coincidencias = extraer_texto_rtf(archivo, terminos_normalizados, terminos_originales)
            elif archivo.name.endswith('.xml'):
                contenido, coincidencias = extraer_texto_xml(archivo, terminos_normalizados, terminos_originales)
            elif archivo.name.endswith('.odt'):
                contenido, coincidencias = extraer_texto_odt(archivo, terminos_normalizados, terminos_originales)
            elif archivo.name.endswith('.csv'):
                contenido, coincidencias = extraer_texto_csv(archivo, terminos_normalizados, terminos_originales)
            elif archivo.name.endswith('.json'):
                contenido, coincidencias = extraer_texto_json(archivo, terminos_normalizados, terminos_originales)
            else:
                raise ValidationError("Formato de archivo no soportado.")

            resultado['total'] = len(coincidencias)
            resultado['detalles'] = coincidencias
            resultado['contenido'] = resaltar(contenido, argumentos)

        except Exception as e:
            resultado['error'] = str(e)
            logger.error(f"Error procesando {archivo.name}: {str(e)}")

        resultados.append(resultado)

    return resultados
#----------------------------------


# Función mejorada para descomponer y obtener la base de un carácter
def descomponer(c):
    """Devuelve la base del carácter (sin tilde)."""
    base = unicodedata.normalize('NFD', c)
    return base[0] if len(base) > 0 else c

def crear_regex_insensible(termino):
    """Crea una expresión regular que coincida con variantes acentuadas y mayúsculas/minúsculas."""
    mapeo = {
        'a': '[aáàâäãÁÀÂÄÃA]',
        'e': '[eéèêëÉÈÊËE]',
        'i': '[iíìîïÍÌÎÏI]',
        'o': '[oóòôöõÓÒÔÖÕO]',
        'u': '[uúùûüÚÙÛÜU]',
        'n': '[nñÑN]'
    }

    regex = ''
    for c in termino:
        base = unicodedata.normalize('NFD', c).encode('ascii', 'ignore').decode('utf-8').lower()
        if base in mapeo:
            regex += mapeo[base]
        elif base.isalpha():
            regex += f"[{base}{base.upper()}]"
        else:
            regex += re.escape(c)  # por si hay símbolos
    return regex


def resaltar(texto, argumentos):
    """
    Resalta en HTML los términos en el texto según los argumentos tipo: termino|#color;termino2|#color2
    """
    patrones = []
    for arg in argumentos.split(";"):
        if not arg.strip():
            continue
        termino, color = arg.split("|")
        regex = crear_regex_insensible(termino)
        patrones.append((re.compile(rf"({regex})", re.IGNORECASE), color))

    def aplicar_resaltado(patrones, texto):
        posiciones_ocupadas = []

        def ya_ocupado(start, end):
            return any(s < end and start < e for s, e in posiciones_ocupadas)

        resultado = texto
        offset = 0
        for patron, color in patrones:
            for match in patron.finditer(texto):
                start, end = match.start(), match.end()
                if ya_ocupado(start, end):
                    continue
                span = f'<span style="background-color:{color}">{match.group(0)}</span>'
                resultado = resultado[:start + offset] + span + resultado[end + offset:]
                offset += len(span) - (end - start)
                posiciones_ocupadas.append((start, end))
        return resultado

    return aplicar_resaltado(patrones, texto)


#----------------------------------
def extraer_texto_pdf(archivo, terminos_busqueda, terminos_originales):
    try:
        archivo.seek(0)
        pdf_document = fitz.open(stream=archivo.read(), filetype="pdf")
        contenido_total = ""
        coincidencias = []

        for pagina_num, pagina in enumerate(pdf_document, start=1):
            texto = pagina.get_text()
            contenido_total += texto + "\n"
            # Búsqueda robusta: unir todas las líneas normalizadas de la página
            texto_completo = " ".join([normalizar_texto(linea) for linea in texto.splitlines()])
            for termino in terminos_busqueda:
                if termino in texto_completo:
                    logger.debug(f"[PDF] Coincidencia encontrada (robusta): '{termino}' en página {pagina_num}")
                    coincidencias.append({'pagina': pagina_num, 'linea': '-', 'contenido': 'Coincidencia robusta en toda la página'})
            # Además, sigue buscando por línea
            for linea_num, linea in enumerate(texto.splitlines(), start=1):
                texto_norm = normalizar_texto(linea)
                for termino in terminos_busqueda:
                    if termino in texto_norm:
                        logger.debug(f"[PDF] Coincidencia encontrada: '{termino}' en página {pagina_num}, línea {linea_num}: {texto_norm}")
                        contexto = obtener_contexto(linea, terminos_originales)
                        coincidencias.append({'pagina': pagina_num, 'linea': linea_num, 'contenido': contexto})

        return contenido_total, coincidencias
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo PDF: {str(e)}")


def extraer_texto_txt(archivo, terminos_busqueda, terminos_originales):
    try:
        archivo.seek(0)
        try:
            contenido = archivo.read().decode('utf-8')
        except UnicodeDecodeError:
            contenido = archivo.read().decode('latin-1')

        coincidencias = []
        lineas = contenido.split('\n')
        # Búsqueda robusta: unir todas las líneas normalizadas del archivo
        texto_completo = " ".join([normalizar_texto(linea) for linea in lineas])
        for termino in terminos_busqueda:
            if re.search(rf'\b{re.escape(termino)}\b', texto_completo):
                logger.debug(f"[TXT] Coincidencia encontrada (robusta): '{termino}' en todo el archivo")
                coincidencias.append({'linea': '-', 'contenido': 'Coincidencia robusta en todo el archivo'})
        # Además, sigue buscando por línea
        for linea_num, linea in enumerate(lineas, start=1):
            texto_norm = normalizar_texto(linea)
            for termino in terminos_busqueda:
                if re.search(rf'\b{re.escape(termino)}\b', texto_norm):
                    logger.debug(f"[TXT] Coincidencia encontrada: '{termino}' en línea {linea_num}: {texto_norm}")
                    contexto = obtener_contexto(linea, terminos_originales)
                    coincidencias.append({'linea': linea_num, 'contenido': contexto})
        return contenido, coincidencias
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo TXT: {str(e)}")


def extraer_texto_excel(archivo, terminos_busqueda, terminos_originales):
    try:
        archivo.seek(0)
        xl = pd.ExcelFile(archivo)
        coincidencias = []
        contenido_total = ""

        for hoja in xl.sheet_names:
            df = xl.parse(hoja).fillna('')
            contenido_total += f"--- Hoja: {hoja} ---\n"
            for fila_num, fila in df.iterrows():
                for col_num, celda in enumerate(fila):
                    texto_celda = str(celda)
                    texto_norm = normalizar_texto(texto_celda)
                    celda_excel = f"{df.columns[col_num]}{fila_num + 1}"
                    for termino in terminos_busqueda:
                        termino_norm = normalizar_texto(termino)
                        if re.search(rf'\b{re.escape(termino_norm)}\b', texto_norm):
                            logger.debug(f"[XLSX] Coincidencia encontrada: '{termino_norm}' en hoja {hoja}, celda {celda_excel}: {texto_norm}")
                            contexto = obtener_contexto(texto_celda, terminos_originales)
                            coincidencias.append({
                                'hoja': hoja,
                                'celda': celda_excel,
                                'contenido': contexto
                            })
                    contenido_total += f"{celda_excel}: {texto_celda}\n"
        return contenido_total, coincidencias
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo Excel: {str(e)}")


def extraer_texto_docx(archivo, terminos_busqueda, terminos_originales):
    try:
        archivo.seek(0)
        doc = Document(BytesIO(archivo.read()))
        coincidencias = []
        contenido_total = ""

        for parrafo_num, parrafo in enumerate(doc.paragraphs):
            texto = parrafo.text
            contenido_total += texto + "\n"
            for linea_num, linea in enumerate(texto.splitlines(), start=1):
                texto_norm = normalizar_texto(linea)
                for termino in terminos_busqueda:
                    termino_norm = normalizar_texto(termino)
                    if re.search(rf'\b{re.escape(termino_norm)}\b', texto_norm):
                        logger.debug(f"[DOCX] Coincidencia encontrada: '{termino_norm}' en párrafo {parrafo_num + 1}, línea {linea_num}: {texto_norm}")
                        contexto = obtener_contexto(linea, terminos_originales)
                        coincidencias.append({'parrafo': parrafo_num + 1, 'linea': linea_num, 'contenido': contexto})
        return contenido_total, coincidencias
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo DOCX: {str(e)}")


def extraer_texto_rtf(archivo, terminos_busqueda, terminos_originales):
    try:
        from striprtf.striprtf import rtf_to_text

        archivo.seek(0)
        contenido = archivo.read().decode('utf-8', errors='ignore')
        texto_plano = rtf_to_text(contenido)
        coincidencias = []

        lineas = texto_plano.split('\n')
        for linea_num, linea in enumerate(lineas, start=1):
            if any(re.search(rf'\b{re.escape(termino)}\b', normalizar_texto(linea)) for termino in terminos_busqueda):
                contexto = obtener_contexto(linea, terminos_originales)
                coincidencias.append({'ubicacion': f'Línea {linea_num}', 'contenido': contexto})

        return texto_plano, coincidencias
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo RTF: {str(e)}")


def extraer_texto_xml(archivo, terminos_busqueda, terminos_originales):
    try:
        import xml.etree.ElementTree as ET

        archivo.seek(0)
        tree = ET.parse(archivo)
        root = tree.getroot()
        coincidencias = []
        contenido_total = ""

        for elem in root.iter():
            if elem.text:
                contenido_total += f"<{elem.tag}> {elem.text}\n"
                for termino in terminos_busqueda:
                    texto_norm = normalizar_texto(elem.text)
                    termino_norm = normalizar_texto(termino)
                    if re.search(rf'\b{re.escape(termino_norm)}\b', texto_norm):
                        logger.debug(f"[XML] Coincidencia encontrada: '{termino_norm}' en etiqueta <{elem.tag}>: {texto_norm}")
                        contexto = obtener_contexto(elem.text, terminos_originales)
                        coincidencias.append({'etiqueta': elem.tag, 'contenido': contexto})

        return contenido_total, coincidencias
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo XML: {str(e)}")


def extraer_texto_odt(archivo, terminos_busqueda, terminos_originales):
    try:
    
        archivo.seek(0)
        odt_doc = load(archivo)
        all_paragraphs = odt_doc.getElementsByType(P)
        contenido_total = ""
        coincidencias = []

        for i, p in enumerate(all_paragraphs):
            texto = teletype.extractText(p)
            contenido_total += texto + "\n"
            for linea_num, linea in enumerate(texto.splitlines(), start=1):
                texto_norm = normalizar_texto(linea)
                for termino in terminos_busqueda:
                    termino_norm = normalizar_texto(termino)
                    if re.search(rf'\b{re.escape(termino_norm)}\b', texto_norm):
                        logger.debug(f"[ODT] Coincidencia encontrada: '{termino_norm}' en párrafo {i + 1}, línea {linea_num}: {texto_norm}")
                        contexto = obtener_contexto(linea, terminos_originales)
                        coincidencias.append({'parrafo': i + 1, 'linea': linea_num, 'contenido': contexto})

        return contenido_total, coincidencias
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo ODT: {str(e)}")

def extraer_texto_csv(archivo, terminos_busqueda, terminos_originales):
    try:
        archivo.seek(0)
        df = pd.read_csv(archivo, dtype=str).fillna('')
        contenido_total = ""
        coincidencias = []

        for fila_num, fila in df.iterrows():
            for col_num, celda in enumerate(fila):
                texto_celda = str(celda)
                texto_norm = normalizar_texto(texto_celda)
                celda_csv = f"{df.columns[col_num]}{fila_num + 1}"
                for termino in terminos_busqueda:
                    termino_norm = normalizar_texto(termino)
                    if re.search(rf'\b{re.escape(termino_norm)}\b', texto_norm):
                        logger.debug(f"[CSV] Coincidencia encontrada: '{termino_norm}' en celda {celda_csv}, fila {fila_num + 1}: {texto_norm}")
                        contexto = obtener_contexto(texto_celda, terminos_originales)
                        coincidencias.append({
                            'celda': celda_csv,
                            'fila': fila_num + 1,
                            'contenido': contexto
                        })
                contenido_total += f"{celda_csv}: {texto_celda}\n"
        return contenido_total, coincidencias
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo CSV: {str(e)}")

def extraer_texto_json(archivo, terminos_busqueda, terminos_originales):
    import json

    def extraer_valores(obj, resultados):
        if isinstance(obj, dict):
            for k, v in obj.items():
                extraer_valores(v, resultados)
        elif isinstance(obj, list):
            for item in obj:
                extraer_valores(item, resultados)
        else:
            if isinstance(obj, str):
                resultados.append(obj)

    try:
        archivo.seek(0)
        data = json.load(archivo)
        valores_texto = []
        extraer_valores(data, valores_texto)

        contenido_total = "\n".join(valores_texto)
        coincidencias = []

        for i, texto in enumerate(valores_texto):
            texto_norm = normalizar_texto(texto)
            for termino in terminos_busqueda:
                termino_norm = normalizar_texto(termino)
                if re.search(rf'\b{re.escape(termino_norm)}\b', texto_norm):
                    logger.debug(f"[JSON] Coincidencia encontrada: '{termino_norm}' en elemento {i + 1}: {texto_norm}")
                    contexto = obtener_contexto(texto, terminos_originales)
                    coincidencias.append({'elemento': i + 1, 'contenido': contexto})

        return contenido_total, coincidencias
    except Exception as e:
        raise ValidationError(f"Error al procesar el archivo JSON: {str(e)}")


#----------------------------------


from django.shortcuts import render, redirect
from django.conf import settings
from django.utils import timezone
import bcrypt  # Asegúrate de que esta línea esté presente

# A continuación usas bcrypt.gensalt() en tu código.
salt = bcrypt.gensalt()



from buscador.crypto_utils import descifrar_archivo, reconstruir_contrasena
from datetime import timedelta

# Ofuscada: BOOOM -> B7O3O1O9M
CONTRASENA_OFUSCADA = 'B7O3O1O9M'


def desbloqueo(request):
    error = None
    if request.method == 'POST':
        contrasena_ingresada = request.POST.get('contrasena')
        if contrasena_ingresada == reconstruir_contrasena(CONTRASENA_OFUSCADA):
            # Descifrar views.py si está cifrado
            import os
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
            return redirect('home')
        else:
            error = 'Contraseña incorrecta.'
    return render(request, 'desbloqueo.html', {'error': error})


# Cifrar la contraseña para el bloqueo
contrasena_bloqueo = "mi_contraseña_bloqueo"
salt = bcrypt.gensalt()
hashed_contrasena_bloqueo = bcrypt.hashpw(contrasena_bloqueo.encode('utf-8'), salt)

# Verificar la contraseña
if bcrypt.checkpw("mi_contraseña_bloqueo".encode('utf-8'), hashed_contrasena_bloqueo):
    print("Contraseña correcta")
else:
    print("Contraseña incorrecta")


# Función original
def verificar_fecha():
    fecha_exp = "2025-05-25"
    fecha_actual = timezone.now().date()
    return fecha_actual >= timezone.datetime.strptime(fecha_exp, "%Y-%m-%d").date()

# Función ofuscada (duplicando el código)
def func1():
    a = timezone.now().date()
    b = "2025-05-25"
    x = timezone.datetime.strptime(b, "%Y-%m-%d").date()
    return a >= x

def func2():
    # Un camino alternativo, similar, pero con un nombre engañoso.
    y = timezone.now().date()
    z = "2025-05-25"
    q = timezone.datetime.strptime(z, "%Y-%m-%d").date()
    return y >= q




def procesar_datos():
    # Función que solo debería funcionar después de la fecha límite
    if timezone.now().date() >= timezone.datetime.strptime(settings.FECHA_EXPIRACION, "%Y-%m-%d").date():
        # Aquí desactivas parte de la funcionalidad
        return "Funcionalidad eliminada después de la fecha"
    else:
        return "Funcionalidad activa"


from django.conf import settings
from django.utils import timezone

# Obtener la fecha actual y la fecha de expiración
fecha_actual = timezone.now().date()
fecha_expiracion = timezone.datetime.strptime(settings.FECHA_EXPIRACION, "%Y-%m-%d").date()

# Verificar si la funcionalidad debería estar activa o no
if fecha_actual >= fecha_expiracion:
    print("La licencia ha caducado. Funcionalidad bloqueada.")
    # Aquí puedes simular el bloqueo de la funcionalidad en tu código
else:
    print("La licencia está activa. Funcionalidad disponible.")
    # Aquí puedes simular el desbloqueo de la funcionalidad en tu código


from django.conf import settings

# Verificar la contraseña ingresada
# contrasena_ingresada = input("Introduce la contraseña de desbloqueo: ")
# if contrasena_ingresada == settings.CONTRASENA_DESBLOQUEO:
#     print("Contraseña correcta. La aplicación ha sido desbloqueada.")
#     # Puedes simular que la sesión está desbloqueada aquí
# else:
#     print("Contraseña incorrecta.")


# views.py
from django.shortcuts import render
from django.conf import settings
from django.utils import timezone

def buscar(request):
    # Verificar si la licencia ha caducado
    fecha_actual = timezone.now().date()
    fecha_expiracion = timezone.datetime.strptime(settings.FECHA_EXPIRACION, "%Y-%m-%d").date()
    
    # Verificar si la funcionalidad está disponible o bloqueada
    licencia_caducada = fecha_actual >= fecha_expiracion
    
    # Pasar la información a la plantilla
    return render(request, 'home.html', {'licencia_caducada': licencia_caducada})
