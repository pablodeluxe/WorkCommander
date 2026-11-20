@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if not errorlevel 1 (
    set "PY=py -3"
) else (
    set "PY=python"
)

echo Instalando/actualizando PyInstaller...
%PY% -m pip install --quiet --upgrade pyinstaller
if errorlevel 1 (
    echo No se pudo instalar PyInstaller. Revise su conexion a Internet.
    pause
    exit /b 1
)

echo Generando ejecutable...
%PY% -m PyInstaller --noconfirm --clean --onefile --console --name WorkCommander workcommander.py
if errorlevel 1 (
    echo Fallo la generacion del ejecutable.
    pause
    exit /b 1
)

echo.
echo Listo. El ejecutable esta en: %~dp0dist\WorkCommander.exe
echo Tambien puede usar WorkCommander.bat (requiere Python instalado).
pause
