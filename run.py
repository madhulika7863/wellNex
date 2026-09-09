"""
FitMind AI Coach - Main Entrypoint & Server Launcher
Checks for trained models, trains them if missing, and boots the Flask web application.
"""

import os
import sys

def main():
    print("=" * 65)
    print("  WellNex - Personalized Fitness & Mental Wellness System")
    print("=" * 65)

    # 1. Verify ML models exist
    model_file = os.path.join("ml_engine", "models", "decision_trees.joblib")
    if not os.path.exists(model_file):
        print("\n[Step 1/2] ML models not found. Running training pipeline...")
        from ml_engine.train_models import train
        train()
        print("[Step 1/2] ML models successfully trained & serialized!")
    else:
        print("\n[Step 1/2] Pre-trained ML models loaded successfully.")

    # 2. Boot Flask Web Server
    print("\n[Step 2/2] Starting WellNex Web Server...")
    print(">>> Web Dashboard: http://localhost:5000")
    print(">>> Press CTRL+C to stop the server\n")

    from backend.app import app
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    main()
