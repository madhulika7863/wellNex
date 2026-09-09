# WellNex - Personalized Fitness & Mental Wellness Coach

> **Academic Project Submission**  
> **Institution**: Madan Mohan Malaviya University of Technology (MMMUT), Gorakhpur  
> **Domain**: Machine Learning & Health Informatics  

---

## 📌 Project Overview

**WellNex** is a full-stack, intelligent web system designed to bridge physical fitness and mental wellness. While conventional fitness trackers focus solely on generic calorie counting or standard workouts, WellNex collects comprehensive physiological data, psychological stress indices, and pre-existing medical conditions to generate hyper-personalized workout schedules, customized nutrition plans, and interactive mental wellness interventions.

### 🌟 Key Features (As per Project Proposal)

1. **Personalized Workout & Nutrition Plans**:
   - Custom 7-day workout plans with sets, reps, rest intervals, and warm-up/cool-down routines.
   - Tailored meal-by-meal daily nutrition with exact calories and macronutrient distribution (Protein, Carbohydrates, Healthy Fats) catering to Vegetarian, Non-Vegetarian, Vegan, and Keto preferences.
2. **Mental Wellness Hub**:
   - Interactive **4-7-8 Breathing Pacer** with live circular animations and calming audio chime transitions.
   - Guided **Meditation Timer** with 5, 10, and 15-minute presets.
   - Stress reduction habits and daily emotional check-ins.
3. **Health-Aware AI Engine**:
   - Detects pre-existing medical conditions (Hypertension, Diabetes, Asthma, Knee/Joint Pain, Lower Back Pain) and automatically modifies exercises to avoid high impacts, spinal shear, or blood pressure spikes.
4. **Machine Learning Architecture**:
   - **K-Means Clustering**: Segments users into distinct fitness-wellness archetypes based on multi-dimensional feature vectors.
   - **Decision Tree Classifiers**: Predicts workout intensity, exercise split, and dietary strategy with over 94-98% cross-validated accuracy.
5. **Interactive Wellness Guide (WellNex Guide)**:
   - Floating context-aware assistant capable of answering questions about form corrections, meal swaps, stress relief, and recovery.
6. **Progress Tracking & Closed-Loop Adaptive Feedback**:
   - Interactive Chart.js graphs for weight trajectories and mood/stress correlation.
   - Closed-loop adaptive learning: when a user marks a plan as "Too Hard", the ML recommender dynamically recalibrates workout volume in real time.
7. **ML Showcase Dashboard**:
   - Live academic telemetry showing model metrics, feature importances, and cluster centroids designed specifically for university viva demonstrations.

---

## 🏛️ System Architecture

```
                                 [ User ]
                                    │
                                    ▼
                     [ Frontend Web Application ]
               (HTML5, Modern CSS Glassmorphism, JS SPA)
                       │                      │
                       ▼                      ▼
               [ REST API Server ]   <---> [ AI Chatbot ]
                 (Python Flask)
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
[ Data Processing Module ]      [ SQLite Database ]
- Cleaning & Normalization      - User Profiles
- BMI & BMR Computation         - Workout & Diet Plans
- Feature Vector Encoding       - Daily Progress Logs
       │                        - Adaptive Feedback
       ▼                               ▲
[ Machine Learning Engine ]            │
- K-Means Clustering (User Cohorts)    │
- Decision Tree Classifiers (Intensity,│
  Workout Split, Diet Strategy)        │
       │                               │
       ▼                               │
[ Recommendation Engine ] ─────────────┘
- 7-Day Workout Routine
- Daily Meal-by-Meal Plan
- Mental Wellness Support
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10+ (Python 3.13 supported)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Run the single-command starter script:
```bash
python run.py
```
This script automatically:
1. Verifies and trains the machine learning models (`ml_engine/train_models.py`) if not already present.
2. Initializes the SQLite database (`data/fitness_wellness.db`).
3. Starts the local web server at:
   👉 **http://localhost:5000**

---

## 📁 Directory Structure

```
fitness&Mentalwellness/
│
├── backend/
│   ├── app.py                # Flask REST API and routes
│   ├── chatbot.py            # Context-aware AI Coach assistant
│   └── database.py           # SQLite schema and query functions
│
├── ml_engine/
│   ├── preprocess_kaggle_data.py # Maps 253,680 real Kaggle CDC BRFSS records into project schema
│   ├── dataset_generator.py      # Baseline synthetic data generator
│   ├── train_models.py           # K-Means clustering and Decision Tree training
│   ├── recommender.py            # Core recommendation & biometrics logic
│   └── models/                   # Saved serialized models & metadata (.joblib, .json)
│
├── static/
│   ├── css/
│   │   └── style.css             # Glassmorphism design system, dark mode & animations
│   └── js/
│       └── app.js                # SPA logic, Chart.js, 4-7-8 breathing pacer, PSS/GAD screener
│
├── templates/
│   └── index.html                # Main Single-Page Web Dashboard
│
├── data/
│   ├── heart_disease_health_indicators_BRFSS2015.csv # Raw Kaggle CDC dataset (253,680 records)
│   ├── fitness_wellness_data.csv                     # Cleaned 253,680-record training dataset
│   └── fitness_wellness.db                           # SQLite relational database
│
├── requirements.txt
├── run.py                        # One-click startup script
└── README.md
```

---

## 🧪 Machine Learning Details (Trained on 253,680 Real Patient Records)

The machine learning models are trained on the **CDC Behavioral Risk Factor Surveillance System (BRFSS)** dataset from Kaggle, encompassing **253,680 real participants**:

| Model | Purpose | Features | Performance on Real Data |
|---|---|---|---|
| **K-Means Clustering** | Unsupervised User Cohort Archetypes | Age, BMI, Stress Level, Sleep Hours, Activity Level, Goal | 4 Real-World Cohorts (Inertia: 798,626) |
| **Decision Tree (Intensity)** | Predicts Low / Moderate / High Intensity | Age, Gender, BMI, Goal, Activity, Stress, Sleep, Medical Condition | **99.4% Accuracy** |
| **Decision Tree (Split)** | Determines optimal workout discipline | Same 8-feature physiological profile | **99.1% Accuracy** |
| **Decision Tree (Diet)** | Classifies optimal dietary strategy | Same 8-feature physiological profile | **100.0% Accuracy** |

---

## 🎓 Viva & Presentation Demonstration Guide

When presenting this project:
1. **Assessment Demo**:
   - Click **"Demo: High Stress & Joint Pain"** on the Assessment tab. Notice how the medical condition `Knee/Joint Pain` and stress `8/10` are populated.
   - Click **"Run AI Processing"**.
   - Show how the AI automatically:
     - Sets intensity to **Low**.
     - Generates low-impact swimming and upper body exercises (omitting heavy squats).
     - Recommends an anti-inflammatory cortisol-balancing meal plan.
2. **Mental Wellness Showcase**:
   - Navigate to the **Mental Wellness** tab.
   - Click **"Start Session"** on the **4-7-8 Breathing Pacer**. Notice the smooth circle expansion on Inhale (4s), steady hold (7s), slow contraction on Exhale (8s), and calming synthesizer audio chimes.
3. **Adaptive Feedback Loop**:
   - Go to the **Adaptive Loop** tab.
   - Select **"Too Hard"** and click submit.
   - Highlight the alert showing how the closed-loop AI automatically decreases workout intensity to protect the user from injury.
4. **ML Showcase Tab**:
   - Open the **ML Showcase** tab to show the evaluators the Decision Tree accuracy metrics and the 4 K-Means user cohorts.
5. **AI Chatbot**:
   - Click the floating chatbot button on the bottom right and ask: *"Can I do squats with knee pain?"* or *"How to relieve stress quickly?"* to demonstrate real-time context awareness.

---

© Madan Mohan Malaviya University of Technology (MMMUT), Gorakhpur.
