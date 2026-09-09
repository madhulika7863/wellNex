"""
Dataset Generator for AI-Based Personalized Fitness & Mental Wellness Coach
Generates realistic synthetic user profiles with physiological, psychological,
and lifestyle data for training K-Means and Decision Tree models.
"""

import numpy as np
import pandas as pd
import os

def generate_dataset(num_samples=2500, output_path="data/fitness_wellness_data.csv"):
    np.random.seed(42)
    
    # 1. Age: 18 to 68
    ages = np.random.randint(18, 69, size=num_samples)
    
    # 2. Gender: Male (48%), Female (48%), Other (4%)
    genders = np.random.choice(["Male", "Female", "Other"], size=num_samples, p=[0.48, 0.48, 0.04])
    
    # 3. Heights (cm): Normally distributed around 168cm with std 10cm
    heights = np.round(np.clip(np.random.normal(168, 10, size=num_samples), 145, 198), 1)
    
    # 4. Weights (kg): Distributed realistically with respect to height
    # Base BMI distribution 18 to 36
    base_bmis = np.random.normal(25.5, 4.2, size=num_samples)
    base_bmis = np.clip(base_bmis, 16.5, 42.0)
    weights = np.round(base_bmis * ((heights / 100) ** 2), 1)
    bmis = np.round(weights / ((heights / 100) ** 2), 2)
    
    # 5. Fitness Goals
    goals = np.random.choice([
        "Weight Loss",
        "Muscle Gain",
        "Endurance",
        "Flexibility & Posture",
        "Stress Relief & General Health"
    ], size=num_samples, p=[0.35, 0.25, 0.15, 0.12, 0.13])
    
    # 6. Activity Level
    activity_levels = np.random.choice([
        "Sedentary",
        "Lightly Active",
        "Moderately Active",
        "Very Active"
    ], size=num_samples, p=[0.35, 0.30, 0.23, 0.12])
    
    # 7. Stress Level: 1 to 10
    # Slightly correlated with sedentary activity and high age
    base_stress = np.random.normal(5.5, 2.0, size=num_samples)
    stress_levels = np.clip(np.round(base_stress), 1, 10).astype(int)
    
    # 8. Sleep Hours: 4.5 to 9.5
    sleep_hours = np.round(np.clip(np.random.normal(7.0 - (stress_levels - 5) * 0.2, 1.1), 4.5, 9.5), 1)
    
    # 9. Medical Conditions
    medical_conditions = np.random.choice([
        "None",
        "Hypertension",
        "Diabetes",
        "Asthma",
        "Knee/Joint Pain",
        "Back Pain"
    ], size=num_samples, p=[0.55, 0.10, 0.10, 0.08, 0.10, 0.07])
    
    # 10. Dietary Preference
    dietary_prefs = np.random.choice([
        "Vegetarian",
        "Non-Vegetarian",
        "Vegan",
        "Keto"
    ], size=num_samples, p=[0.42, 0.43, 0.10, 0.05])
    
    # Rational Target Labeling (Ground Truth for Decision Tree training)
    workout_intensities = []
    workout_splits = []
    diet_strategies = []
    
    for i in range(num_samples):
        age = ages[i]
        bmi = bmis[i]
        goal = goals[i]
        act = activity_levels[i]
        stress = stress_levels[i]
        med = medical_conditions[i]
        
        # Intensity logic: high stress or medical conditions or high age cap intensity
        if med in ["Hypertension", "Asthma", "Knee/Joint Pain", "Back Pain"] or age >= 58 or stress >= 8 or bmi >= 33:
            intensity = "Low"
        elif act in ["Very Active", "Moderately Active"] and age < 45 and med == "None" and stress < 7:
            intensity = "High"
        else:
            intensity = "Moderate"
            
        workout_intensities.append(intensity)
        
        # Split logic:
        if med == "Knee/Joint Pain":
            split = "Low-Impact Swimming & Upper Body Strength"
        elif med == "Back Pain":
            split = "Core Stability & Gentle Mobility"
        elif med == "Hypertension":
            split = "Aerobic Cardio & Gentle Resistance"
        elif med == "Asthma":
            split = "Interval Walking & Breathing Yoga"
        elif goal == "Muscle Gain" and intensity != "Low":
            split = "Hypertrophy Push-Pull-Legs"
        elif goal == "Weight Loss":
            if intensity == "High":
                split = "HIIT & Functional Circuit"
            else:
                split = "Cardio Fat Burn & Light Strength"
        elif goal == "Endurance":
            split = "Paced Cardio & Stamina Training"
        elif goal == "Flexibility & Posture":
            split = "Pilates & Hatha Yoga"
        else:
            split = "Holistic Wellness & Calisthenics"
            
        workout_splits.append(split)
        
        # Diet Strategy logic:
        if med == "Diabetes":
            diet = "Low Glycemic Complex Carb & High Fiber"
        elif med == "Hypertension":
            diet = "DASH Low Sodium Heart-Healthy"
        elif goal == "Muscle Gain":
            diet = "High Protein Calorie Surplus"
        elif goal == "Weight Loss":
            diet = "High Protein Calorie Deficit"
        elif stress >= 8:
            diet = "Anti-Inflammatory Cortisol-Balancing"
        else:
            diet = "Nutrient-Dense Balanced Maintenance"
            
        diet_strategies.append(diet)
        
    df = pd.DataFrame({
        "age": ages,
        "gender": genders,
        "height_cm": heights,
        "weight_kg": weights,
        "bmi": bmis,
        "goal": goals,
        "activity_level": activity_levels,
        "stress_level": stress_levels,
        "sleep_hours": sleep_hours,
        "medical_condition": medical_conditions,
        "dietary_preference": dietary_prefs,
        "workout_intensity": workout_intensities,
        "workout_split": workout_splits,
        "diet_strategy": diet_strategies
    })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records saved to {output_path}")
    return df

if __name__ == "__main__":
    generate_dataset()
