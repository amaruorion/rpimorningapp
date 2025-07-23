#!/bin/bash
echo "Starting MTA Morning Transit Tracker GUI..."
echo
echo "Installing dependencies..."
pip3 install --break-system-packages -r requirements.txt
echo
echo "Dependencies installed successfully!"
echo "Starting the GUI transit tracker..."
echo
python3 gui.py
read -p "Press ENTER to exit..."
