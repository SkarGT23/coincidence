@echo off
cd /d "C:\Users\Usuario\Desktop\APP COINCIDENCE - copia (3) - copia"

REM Inicia el servidor en una nueva ventana
start "" python manage.py runserver

REM Espera unos segundos para que el servidor arranque
timeout /t 3 >nul

REM Abre el navegador en la URL de la app
start "" http://127.0.0.1:8000/

pause

