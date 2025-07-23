@echo off
echo ================================================
echo    LCARS Transit Interface - USS Enterprise
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Installing required dependencies...
echo.

REM Install from requirements.txt
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Try running: pip install --upgrade pip
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

echo Starting LCARS Transit Interface...
echo.
echo NOTE: Using REAL transit data from MTA APIs
echo.

REM Run the GUI
python gui.py

REM If GUI fails, try python3
if %errorlevel% neq 0 (
    python3 gui.py
)

echo.
pause