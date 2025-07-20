@echo off
echo Starting MTA Morning Transit Tracker...
echo.

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Dependencies installed successfully!
echo Starting the transit tracker...
echo.

python main.py

pause