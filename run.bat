@echo off
title CampusCare - CollegeBot Launcher
cd /d "%~dp0"

echo ========================================================
echo        CampusCare - Student Support Hub Launcher
echo ========================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not found on your system!
        echo Please install Python from https://www.python.org/downloads/
        echo (Make sure to check "Add Python to PATH" during install)
        echo.
        pause
        exit /b 1
    ) else (
        set "PYTHON_CMD=py"
    )
) else (
    set "PYTHON_CMD=python"
)

:: 2. Check or Create Virtual Environment
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment (.venv)...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Could not create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo [1/3] Virtual environment (.venv) already exists.
)

:: 3. Install required packages
echo [2/3] Checking and installing required packages (Flask, scikit-learn)...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Package installation failed. Please check your internet connection.
    pause
    exit /b 1
)

:: 4. Open Browser & Run Application
echo [3/3] Launching CampusCare...
echo.
echo ========================================================
echo   [PC Browser]     : http://127.0.0.1:5000
echo   [Mobile on Wi-Fi]: http://10.166.16.4:5000
echo.
echo   Keep this black window open while using the app!
echo   To stop the server, press Ctrl + C or close this window.
echo ========================================================
echo.

:: Launch browser in background
start "" "http://127.0.0.1:5000"

:: Start the Flask application
".venv\Scripts\python.exe" app.py

if %errorlevel% neq 0 (
    echo.
    echo Server stopped unexpectedly.
    pause
)
