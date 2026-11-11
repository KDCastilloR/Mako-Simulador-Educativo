
@echo off
title MAKO ROBOT - CONTROL MOVIL

color 0B

echo ==========================================
echo          MAKO MOBILE SERVER
echo          CONTROL DE SIMULACION
echo ==========================================
echo.
echo Iniciando servidor MAKO...
echo.

cd /d C:\MAKO_PACS

if not exist "C:\MAKO_PACS\IA\.venv\Scripts\python.exe" (
    echo ERROR: No se encontro Python del entorno IA.
    pause
    exit /b 1
)

if not exist "C:\MAKO_PACS\control_movil\servidor.py" (
    echo ERROR: No se encontro servidor.py.
    pause
    exit /b 1
)

echo Iniciando Flask...
echo.
echo CONTROL MAKO - PUERTO 5001
echo.
echo Direccion movil:
echo http://10.23.146.1:5001
echo.
echo Para cerrar el servidor presiona CTRL+C.
echo ==========================================

"C:\MAKO_PACS\IA\.venv\Scripts\python.exe" "C:\MAKO_PACS\control_movil\servidor.py"

echo.
echo El servidor MAKO se ha detenido.
pause
