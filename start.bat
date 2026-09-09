@echo off
title WellNex - Personalized Fitness & Mental Wellness
echo ============================================================
echo   WellNex - Personalized Fitness & Mental Wellness System
echo ============================================================
echo.
echo [1/2] Checking and installing required dependencies...
python -m pip install -r requirements.txt
echo.
echo [2/2] Launching Application...
echo The app will open in your browser at http://localhost:5000
start http://localhost:5000
python run.py
pause
