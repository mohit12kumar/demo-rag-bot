@echo off
title AI Study Library

echo Starting Backend...
start cmd /k "venv\Scripts\activate && uvicorn app.main:app --reload"

timeout /t 5 > nul

echo Starting Frontend...
start cmd /k "cd frontend && ..\venv\Scripts\activate && streamlit run streamlit_app.py --server.port 3000"

echo.
echo =====================================
echo Backend  : http://localhost:8000
echo Swagger  : http://localhost:8000/docs
echo Frontend : http://localhost:3000
echo =====================================
pause