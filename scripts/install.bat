@echo off
echo ========================================
echo  Pizzeria MAX - Instalacion Automatica
echo ========================================
echo.

echo [1/4] Instalando Backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd ..
echo Backend instalado correctamente!
echo.

echo [2/4] Instalando Frontend...
cd frontend
call npm install
cd ..
echo Frontend instalado correctamente!
echo.

echo [3/4] Creando directorios necesarios...
if not exist "backend\data" mkdir backend\data
if not exist "backend\models" mkdir backend\models
echo Directorios creados!
echo.

echo [4/4] Configuracion completada!
echo.
echo ========================================
echo  INSTALACION COMPLETADA
echo ========================================
echo.
echo Para iniciar el proyecto:
echo   1. Backend:  cd backend ^&^& venv\Scripts\activate ^&^& python -m uvicorn app.main:app --reload
echo   2. Frontend: cd frontend ^&^& npm run dev
echo.
pause
