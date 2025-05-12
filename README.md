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
