@echo off
setlocal
cd /d "%~dp0"

where iscc >nul 2>&1
if errorlevel 1 (
  echo Inno Setup (ISCC) no esta instalado o no esta en PATH.
  echo Instala Inno Setup y vuelve a ejecutar este script.
  pause
  exit /b 1
)

if not exist "..\dist\ip-calculator.exe" (
  echo No se encontro dist\ip-calculator.exe
  echo Genera primero el ejecutable con build_exe.bat
  pause
  exit /b 1
)

iscc ip_calculator.iss
if errorlevel 1 (
  echo Fallo la compilacion del instalador.
  pause
  exit /b 1
)

echo Instalador generado en dist\ip-calculator-setup.exe
pause
