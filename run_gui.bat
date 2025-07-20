@echo off
echo Starting MTA Morning Transit Tracker GUI...
echo.

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Dependencies installed successfully!
echo Starting the GUI transit tracker...
echo.

python gui.py

pause