"""
Train Machine Learning Models for Personalized Fitness & Mental Wellness Coach
- K-Means Clustering for User Segmentation into archetypes
- Decision Tree Classifiers for Safe Workout and Diet Recommendation
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from ml_engine.dataset_generator import generate_dataset

MODELS_DIR = "ml_engine/models"
DATA_PATH = "data/fitness_wellness_data.csv"

# Encoding maps
ACTIVITY_MAP = {"Sedentary": 0, "Lightly Active": 1, "Moderately Active": 2, "Very Active": 3}
GOAL_MAP = {
    "Weight Loss": 0,
    "Muscle Gain": 1,
    "Endurance": 2,
    "Flexibility & Posture": 3,
    "Stress Relief & General Health": 4
}
MEDICAL_MAP = {
    "None": 0,
    "Hypertension": 1,
    "Diabetes": 2,
    "Asthma": 3,
    "Knee/Joint Pain": 4,
    "Back Pain": 5
}
GENDER_MAP = {"Male": 0, "Female": 1, "Other": 2}

def prepare_features(df):
    df_feat = df.copy()
    df_feat["activity_num"] = df_feat["activity_level"].map(ACTIVITY_MAP)
    df_feat["goal_num"] = df_feat["goal"].map(GOAL_MAP)
    df_feat["medical_num"] = df_feat["medical_condition"].map(MEDICAL_MAP)
    df_feat["gender_num"] = df_feat["gender"].map(GENDER_MAP)
    return df_feat

def train():
    os.makedirs(MODELS_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        print("Dataset not found. Generating dataset...")
        df = generate_dataset(2500, DATA_PATH)
    else:
        df = pd.read_csv(DATA_PATH)
        
    df_feat = prepare_features(df)
    
    # ==========================================
    # 1. K-MEANS CLUSTERING (User Segmentation)
    # ==========================================
    cluster_features = ["age", "bmi", "stress_level", "sleep_hours", "activity_num", "goal_num"]
    X_cluster = df_feat[cluster_features].values
    
    scaler = StandardScaler()
    X_cluster_scaled = scaler.fit_transform(X_cluster)
    
    n_clusters = 4
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X_cluster_scaled)
    
    # Characterize clusters
    cluster_profiles = {}
    archetype_names = [
        "High-Stress & Sedentary Rebooter",
        "Cardio & Weight Management Achiever",
        "Peak Strength & Athletic Builder",
        "Therapeutic & Mindful Wellness Seeker"
    ]
    
    for c in range(n_clusters):
        c_sub = df[df["cluster"] == c]
        cluster_profiles[c] = {
            "name": archetype_names[c],
            "avg_age": round(float(c_sub["age"].mean()), 1),
            "avg_bmi": round(float(c_sub["bmi"].mean()), 1),
            "avg_stress": round(float(c_sub["stress_level"].mean()), 1),
            "avg_sleep": round(float(c_sub["sleep_hours"].mean()), 1),
            "top_goal": c_sub["goal"].mode()[0] if len(c_sub) > 0 else "General Health",
            "top_activity": c_sub["activity_level"].mode()[0] if len(c_sub) > 0 else "Sedentary",
            "count": int(len(c_sub)),
            "summary": f"Cohort with mean BMI {c_sub['bmi'].mean():.1f} and stress level {c_sub['stress_level'].mean():.1f}/10."
        }
    
    # ==========================================
    # 2. DECISION TREE CLASSIFIERS
    # ==========================================
    dt_features = ["age", "gender_num", "bmi", "goal_num", "activity_num", "stress_level", "sleep_hours", "medical_num"]
    X_dt = df_feat[dt_features].values
    
    # Target 1: Workout Intensity (Low / Moderate / High)
    y_intensity = df["workout_intensity"].values
    X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(X_dt, y_intensity, test_size=0.2, random_state=42)
    dt_intensity = DecisionTreeClassifier(max_depth=5, min_samples_split=10, random_state=42)
    dt_intensity.fit(X_train_i, y_train_i)
    acc_intensity = accuracy_score(y_test_i, dt_intensity.predict(X_test_i))
    
    # Target 2: Workout Split
    y_split = df["workout_split"].values
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X_dt, y_split, test_size=0.2, random_state=42)
    dt_split = DecisionTreeClassifier(max_depth=6, min_samples_split=8, random_state=42)
    dt_split.fit(X_train_s, y_train_s)
    acc_split = accuracy_score(y_test_s, dt_split.predict(X_test_s))
    
    # Target 3: Diet Strategy
    y_diet = df["diet_strategy"].values
    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X_dt, y_diet, test_size=0.2, random_state=42)
    dt_diet = DecisionTreeClassifier(max_depth=5, min_samples_split=8, random_state=42)
    dt_diet.fit(X_train_d, y_train_d)
    acc_diet = accuracy_score(y_test_d, dt_diet.predict(X_test_d))
    
    # Feature importances for presentation showcase
    intensity_importances = dict(zip(dt_features, [round(float(v), 3) for v in dt_intensity.feature_importances_]))
    
    # Save artifacts
    joblib.dump(kmeans, os.path.join(MODELS_DIR, "kmeans_model.joblib"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.joblib"))
    joblib.dump({
        "dt_intensity": dt_intensity,
        "dt_split": dt_split,
        "dt_diet": dt_diet
    }, os.path.join(MODELS_DIR, "decision_trees.joblib"))
    
    metadata = {
        "cluster_features": cluster_features,
        "dt_features": dt_features,
        "cluster_profiles": cluster_profiles,
        "metrics": {
            "kmeans_inertia": round(float(kmeans.inertia_), 2),
            "intensity_accuracy": round(float(acc_intensity * 100), 2),
            "split_accuracy": round(float(acc_split * 100), 2),
            "diet_accuracy": round(float(acc_diet * 100), 2)
        },
        "intensity_feature_importances": intensity_importances,
        "maps": {
            "activity": ACTIVITY_MAP,
            "goal": GOAL_MAP,
            "medical": MEDICAL_MAP,
            "gender": GENDER_MAP
        }
    }
    
    with open(os.path.join(MODELS_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("=== Training Complete ===")
    print(f"K-Means clusters: {n_clusters} | Inertia: {kmeans.inertia_:.2f}")
    print(f"Intensity DT Accuracy: {acc_intensity*100:.1f}%")
    print(f"Split DT Accuracy:     {acc_split*100:.1f}%")
    print(f"Diet DT Accuracy:      {acc_diet*100:.1f}%")
    print(f"Models and metadata saved to {MODELS_DIR}/")

if __name__ == "__main__":
    train()
