#!/bin/bash
echo "============================================================"
echo "  WellNex - Personalized Fitness & Mental Wellness System"
echo "============================================================"
echo ""
echo "[1/2] Installing requirements..."
python3 -m pip install -r requirements.txt
echo ""
echo "[2/2] Launching Application at http://localhost:5000 ..."
python3 run.py
