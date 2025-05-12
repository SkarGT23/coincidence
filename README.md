# APP COINCIDENCE

Esta es una aplicación desarrollada en Python con Django que incluye funcionalidades de búsqueda, manejo de fechas de expiración, y procesamiento de documentos. El proyecto utiliza varias librerías para el manejo de archivos, seguridad, y procesamiento de datos.

## Requisitos

- Python 3.10+
- pip
- Virtualenv (opcional, pero recomendado)

## Instalación

1. Clona este repositorio o descarga el código fuente.
2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura el archivo `.env` con tus variables de entorno necesarias.
5. Realiza migraciones de base de datos:
   ```bash
   python manage.py migrate
   ```
6. Ejecuta el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

## Estructura del Proyecto

- `buscador/`: Módulo principal de la aplicación.
- `project/`: Configuración principal de Django.
- `dist/`, `build/`: Carpetas de distribución y construcción.
- `manage.py`: Script principal para comandos de Django.

## Nueva funcionalidad: Búsqueda Automática de Coincidencias entre Archivos

La aplicación ahora permite subir varios archivos de diferentes tipos (PDF, DOCX, TXT, XLSX, RTF, XML, ODT, CSV, JSON) y buscar coincidencias automáticas entre ellos **sin necesidad de ingresar una palabra clave**.

- Utiliza la función `buscar_coincidencias_automaticas_v2` para comparar los archivos subidos y encontrar palabras o números que aparecen en más de un archivo.
- La interfaz de búsqueda automática está disponible desde la página principal, mediante el botón "Búsqueda Automática (sin palabra clave)".
- El resultado muestra la lista de coincidencias encontradas y los archivos donde aparece cada coincidencia.

## Cómo usar la búsqueda automática

1. Haz clic en el botón "Búsqueda Automática (sin palabra clave)" en la página principal.
2. Sube al menos dos archivos de los formatos soportados.
3. Haz clic en "Subir y buscar coincidencias".
4. Revisa la tabla de coincidencias encontradas.

No es necesario ingresar ningún término de búsqueda para esta funcionalidad.

## Dependencias principales

- Django
- pandas
- numpy
- lxml
- PyMuPDF
- python-docx
- odfpy
- cryptography
- bcrypt

Consulta `requirements.txt` para la lista completa.

## Licencia

Este proyecto es privado y para uso interno.

---

Si tienes dudas o necesitas soporte, contacta al desarrollador principal.
