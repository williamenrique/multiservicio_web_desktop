@echo off
title Instalacion de Dependencias - Taller Multiservicio PRO
color 0B
cls

echo ============================================================
echo    TALLER MULTISERVICIO PRO - Instalacion de Dependencias
echo ============================================================
echo.
echo Este script instalara todas las dependencias necesarias
echo para el proyecto una por una.
echo.
echo Presione cualquier tecla para comenzar...
pause > nul
cls

:: ============================================================
:: PASO 1: Actualizar pip
:: ============================================================
echo.
echo ============================================================
echo   PASO 1: Actualizar pip al ultimo version
echo ============================================================
echo.
echo   Comando: python -m pip install --upgrade pip
echo.
echo ============================================================
echo.
python -m pip install --upgrade pip
echo.
if %ERRORLEVEL% EQU 0 (
    echo   [OK] pip actualizado correctamente.
) else (
    echo   [WARN] Hubo un problema actualizando pip, continuamos...
)
echo.
echo Presione cualquier tecla para continuar al Paso 2...
pause > nul
cls

:: ============================================================
:: PASO 2: Instalar flet (Framework de interfaz grafica)
:: ============================================================
echo.
echo ============================================================
echo   PASO 2: Instalar flet (Framework de interfaz grafica)
echo ============================================================
echo.
echo   Descripcion: Framework UI para aplicaciones de escritorio
echo   y web con Python.
echo.
echo   Comando: pip install flet>=0.86.0
echo.
echo ============================================================
echo.
pip install "flet>=0.86.0"
echo.
if %ERRORLEVEL% EQU 0 (
    echo   [OK] flet instalado correctamente.
) else (
    echo   [ERROR] Fallo la instalacion de flet. Revise el error arriba.
    echo   Presione cualquier tecla para continuar o cierre la ventana para cancelar...
    pause > nul
)
echo.
echo Presione cualquier tecla para continuar al Paso 3...
pause > nul
cls

:: ============================================================
:: PASO 3: Instalar pymysql (Conector MySQL)
:: ============================================================
echo.
echo ============================================================
echo   PASO 3: Instalar pymysql (Conector MySQL)
echo ============================================================
echo.
echo   Descripcion: Conector nativo de Python para bases de
echo   datos MySQL/MariaDB.
echo.
echo   Comando: pip install pymysql>=1.1.0
echo.
echo ============================================================
echo.
pip install "pymysql>=1.1.0"
echo.
if %ERRORLEVEL% EQU 0 (
    echo   [OK] pymysql instalado correctamente.
) else (
    echo   [ERROR] Fallo la instalacion de pymysql. Revise el error arriba.
    echo   Presione cualquier tecla para continuar o cierre la ventana para cancelar...
    pause > nul
)
echo.
echo Presione cualquier tecla para continuar al Paso 4...
pause > nul
cls

:: ============================================================
:: PASO 4: Instalar bcrypt (Hash de contrasenas)
:: ============================================================
echo.
echo ============================================================
echo   PASO 4: Instalar bcrypt (Hash de contrasenas)
echo ============================================================
echo.
echo   Descripcion: Libreria para hashing seguro de contrasenas.
echo   Se usa para autenticacion de usuarios.
echo.
echo   Comando: pip install bcrypt>=4.0
echo.
echo ============================================================
echo.
pip install "bcrypt>=4.0"
echo.
if %ERRORLEVEL% EQU 0 (
    echo   [OK] bcrypt instalado correctamente.
) else (
    echo   [ERROR] Fallo la instalacion de bcrypt. Revise el error arriba.
    echo   Presione cualquier tecla para continuar o cierre la ventana para cancelar...
    pause > nul
)
echo.
echo Presione cualquier tecla para continuar al Paso 5...
pause > nul
cls

:: ============================================================
:: PASO 5: Instalar python-dotenv (Variables de entorno)
:: ============================================================
echo.
echo ============================================================
echo   PASO 5: Instalar python-dotenv (Variables de entorno)
echo ============================================================
echo.
echo   Descripcion: Permite cargar configuracion desde archivos
echo   .env para gestionar credenciales de base de datos.
echo.
echo   Comando: pip install python-dotenv>=1.0
echo.
echo ============================================================
echo.
pip install "python-dotenv>=1.0"
echo.
if %ERRORLEVEL% EQU 0 (
    echo   [OK] python-dotenv instalado correctamente.
) else (
    echo   [ERROR] Fallo la instalacion de python-dotenv. Revise el error arriba.
    echo   Presione cualquier tecla para continuar o cierre la ventana para cancelar...
    pause > nul
)
echo.
echo Presione cualquier tecla para continuar al Paso 6...
pause > nul
cls

:: ============================================================
:: PASO 6: Verificar instalacion de todas las dependencias
:: ============================================================
echo.
echo ============================================================
echo   PASO 6: Verificar instalacion de todas las dependencias
echo ============================================================
echo.
echo   Ejecutando verificacion de modulos instalados...
echo.
echo ============================================================
echo.

python -c "
import sys
print(f'Python version: {sys.version}')
print()
deps = {
    'flet': 'Framework UI',
    'pymysql': 'Conector MySQL',
    'bcrypt': 'Hash de contrasenas',
    'dotenv': 'Variables de entorno',
}
all_ok = True
for mod, desc in deps.items():
    try:
        exec(f'import {mod}')
        print(f'  [OK] {mod:20s} - {desc}')
    except ImportError:
        print(f'  [FAIL] {mod:20s} - {desc} - NO INSTALADO')
        all_ok = False
print()
if all_ok:
    print('  ^ TODAS LAS DEPENDENCIAS ESTAN INSTALADAS CORRECTAMENTE ^')
else:
    print('  ^ ALGUNAS DEPENDENCIAS FALTAN. Revise los pasos anteriores. ^')
"

echo.
echo ============================================================
echo.
echo Presione cualquier tecla para finalizar...
pause > nul
cls

echo.
echo ============================================================
echo    INSTALACION COMPLETADA
echo ============================================================
echo.
echo   Ya puede ejecutar la aplicacion con:
echo.
echo   python main.py
echo.
echo ============================================================
echo.
pause