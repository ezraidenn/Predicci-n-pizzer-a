@echo off
echo ========================================
echo  Iniciando Pizzeria MAX - Sistema Completo
echo ========================================
echo.

echo Iniciando Backend en nueva ventana...
start "Pizzeria MAX - Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Iniciando Frontend en nueva ventana...
start "Pizzeria MAX - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo  Sistema iniciado!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo Docs:     http://localhost:8000/docs
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
