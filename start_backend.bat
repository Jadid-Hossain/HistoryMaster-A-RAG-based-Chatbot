@echo off
cd /d "%~dp0backend"
call ..\venv\Scripts\activate.bat
echo ============================================
echo   History Master backend starting on port 8000 ...
echo   Swagger API docs: http://localhost:8000/docs
echo ============================================
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
