@echo off
echo =====================================================================
echo           CONSTRUCTION INTELLIGENT HUB - STARTUP SCRIPT
echo =====================================================================

:: Create folders if missing
if not exist data mkdir data
if not exist logs mkdir logs

:: Check for environment configuration
if not exist .env (
    echo Warning: .env file not found. Copying .env.example ...
    copy .env.example .env
)

:: Start Backend API in a separate terminal window
echo [SYSTEM] Launching FastAPI Backend on http://localhost:8000 ...
start "Construction Hub Backend" cmd /c "set PYTHONPATH=.&& python -m uvicorn backend.main:app --port 8000 --reload"

:: Give backend time to bind to port
timeout /t 3 /nobreak > NUL

:: Start Streamlit Frontend in the current terminal window
echo [SYSTEM] Launching Streamlit Frontend on http://localhost:8501 ...
set PYTHONPATH=.
python -m streamlit run frontend/app.py --server.port 8501

pause
