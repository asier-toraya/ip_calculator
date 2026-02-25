@echo off
setlocal
cd /d "%~dp0"

python -m PyInstaller --noconfirm --clean --windowed --onefile --name ip-calculator main.py
if errorlevel 1 (
  echo.
  echo No se pudo generar el ejecutable.
  echo Instala PyInstaller con: python -m pip install pyinstaller
  pause
  exit /b 1
)

echo.
echo Ejecutable generado en: dist\ip-calculator.exe
pause
