@echo off
REM One-click demo: builds the frontend (if needed), starts the backend,
REM which then serves the chat UI at http://localhost:8000
cd /d "%~dp0"
if not exist "frontend\dist" (
    echo Building frontend ...
    cd frontend && call npm install && call npm run build && cd ..
)
start "KnowBot-Backend" cmd /c "cd backend && ..\venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
timeout /t 12 > nul
start http://localhost:8000
echo KnowBot is running:  http://localhost:8000   (API docs: /docs)
pause
