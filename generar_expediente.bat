@echo off
title MAKO-PACS - Generador de Expedientes

color 0B
echo ========================================
echo       MAKO-PACS
echo    GENERADOR DE EXPEDIENTES
echo ========================================
echo.

cd /d C:\MAKO_PACS

echo Generando expedientes ficticios...
echo.

python crear_pacientes.py

echo.
echo ========================================
echo       PROCESO FINALIZADO
echo ========================================
echo.

explorer "C:\MAKO_PACS\datos\pacientes"

pause