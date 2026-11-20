@echo off
setlocal
title WorkCommander
set "APP=%~dp0workcommander.py"

if not exist "%APP%" goto :sin_app

where py >nul 2>nul
if errorlevel 1 goto :probar_python

py -3 "%APP%" %*
exit /b %errorlevel%

:probar_python
where python >nul 2>nul
if errorlevel 1 goto :sin_python

python "%APP%" %*
exit /b %errorlevel%

:sin_app
echo No se encontro workcommander.py junto a este archivo.
pause
exit /b 1

:sin_python
echo No se encontro Python. Instale Python 3.8 o superior
echo desde https://www.python.org/downloads/ y vuelva a intentarlo.
pause
exit /b 1
