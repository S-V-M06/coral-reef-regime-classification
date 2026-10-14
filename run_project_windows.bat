@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  if errorlevel 1 goto :fail
)
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :fail
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :fail
.venv\Scripts\python.exe run_project.py
if errorlevel 1 goto :fail
echo.
echo Pipeline completed. Inspect the results folder and generated PDF/PPTX.
pause
exit /b 0
:fail
echo.
echo ERROR: The setup or pipeline failed. Read the error above; verify Python 3.10+ and internet access.
pause
exit /b 1
