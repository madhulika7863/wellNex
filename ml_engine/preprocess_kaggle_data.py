"""
Preprocess Real Kaggle CDC BRFSS 2015 Health Indicators Dataset (253,680 records)
Maps genuine clinical and lifestyle metrics into our fitness & mental wellness schema.
"""

import os
import numpy as np
import pandas as pd

RAW_DATA_PATH = "data/heart_disease_health_indicators_BRFSS2015.csv"
OUTPUT_DATA_PATH = "data/fitness_wellness_data.csv"

AGE_MIDPOINTS = {
    1.0: 21,  # 18-24
    2.0: 27,  # 25-29
    3.0: 32,  # 30-34
    4.0: 37,  # 35-39
    5.0: 42,  # 40-44
    6.0: 47,  # 45-49
    7.0: 52,  # 50-54
    8.0: 57,  # 55-59
    9.0: 62,  # 60-64
    10.0: 67, # 65-69
    11.0: 72, # 70-74
    12.0: 77, # 75-79
    13.0: 82  # 80+
}

def preprocess():
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw Kaggle dataset not found at {RAW_DATA_PATH}")

    print(f"Loading raw Kaggle dataset from {RAW_DATA_PATH}...")
    df_raw = pd.read_csv(RAW_DATA_PATH)
    n_records = len(df_raw)
    print(f"Loaded {n_records:,} real records.")

    np.random.seed(42)

    # 1. Age (Map category 1-13 to realistic continuous age with +/- 1.5 yr jitter)
    base_ages = df_raw["Age"].map(AGE_MIDPOINTS).fillna(45).values
    jitter = np.random.uniform(-1.8, 1.8, size=n_records)
    ages = np.clip(np.round(base_ages + jitter), 18, 85).astype(int)

    # 2. Gender (Sex: 0 = Female, 1 = Male)
    genders = np.where(df_raw["Sex"] == 1.0, "Male", "Female")

    # 3. BMI (Real clinical BMI, clipped to realistic range 15 to 48)
    bmis = np.clip(df_raw["BMI"].values, 15.0, 48.0)

    # 4. Realistic Height (cm) & Weight (kg) based on real gender and real BMI
    # Men: mean 174cm, std 6cm; Women: mean 162cm, std 5.5cm
    male_heights = np.random.normal(174.0, 6.0, size=n_records)
    female_heights = np.random.normal(162.0, 5.5, size=n_records)
    heights = np.where(genders == "Male", male_heights, female_heights)
    heights = np.round(np.clip(heights, 145.0, 198.0), 1)

    # Weight = BMI * (height / 100)^2
    weights = np.round(bmis * ((heights / 100.0) ** 2), 1)

    # 5. Stress Level (Mapped from MentHlth: 0 to 30 days of poor mental health)
    ment_hlth = df_raw["MentHlth"].values
    # Base stress 2.5, scales up to 10 with days of mental distress
    base_stress = 2.5 + (ment_hlth / 30.0) * 6.5 + np.random.normal(0, 0.4, size=n_records)
    stress_levels = np.clip(np.round(base_stress), 1, 10).astype(int)

    # 6. Sleep Hours (derived from mental health, physical health, and general health)
    phys_hlth = df_raw["PhysHlth"].values
    gen_hlth = df_raw["GenHlth"].values # 1=Excellent, 5=Poor
    sleep_base = 7.6 - (ment_hlth / 30.0) * 1.4 - (phys_hlth / 30.0) * 0.8 + np.random.normal(0, 0.5, size=n_records)
    sleep_hours = np.round(np.clip(sleep_base, 4.5, 9.5), 1)

    # 7. Activity Level
    # PhysActivity: 0 (No) or 1 (Yes); GenHlth: 1 (Excellent) to 5 (Poor)
    phys_act = df_raw["PhysActivity"].values
    activity_levels = []
    for i in range(n_records):
        pa = phys_act[i]
        gh = gen_hlth[i]
        if pa == 0:
            if gh >= 4:
                activity_levels.append("Sedentary")
            else:
                activity_levels.append("Sedentary" if np.random.rand() < 0.75 else "Lightly Active")
        else:
            if gh == 1:
                activity_levels.append("Very Active" if np.random.rand() < 0.55 else "Moderately Active")
            elif gh == 2:
                activity_levels.append("Moderately Active" if np.random.rand() < 0.65 else "Very Active")
            elif gh == 3:
                activity_levels.append("Moderately Active" if np.random.rand() < 0.60 else "Lightly Active")
            else:
                activity_levels.append("Lightly Active" if np.random.rand() < 0.70 else "Sedentary")

    # 8. Medical Condition
    # HighBP, Diabetes (1=prediabetes, 2=diabetes), DiffWalk
    high_bp = df_raw["HighBP"].values
    diabetes = df_raw["Diabetes"].values
    diff_walk = df_raw["DiffWalk"].values

    medical_conditions = []
    for i in range(n_records):
        if diff_walk[i] == 1.0 and np.random.rand() < 0.85:
            medical_conditions.append("Knee/Joint Pain")
        elif diabetes[i] in [1.0, 2.0]:
            medical_conditions.append("Diabetes")
        elif high_bp[i] == 1.0:
            medical_conditions.append("Hypertension")
        else:
            medical_conditions.append("None")

    # 9. Fitness Goal (inferred based on real demographics, BMI, and stress)
    goals = []
    for i in range(n_records):
        bmi_val = bmis[i]
        age_val = ages[i]
        stress_val = stress_levels[i]
        med_val = medical_conditions[i]
        act_val = activity_levels[i]

        if stress_val >= 8 or med_val in ["Hypertension", "Diabetes"] and np.random.rand() < 0.35:
            goals.append("Stress Relief & General Health")
        elif bmi_val >= 27.0:
            goals.append("Weight Loss")
        elif age_val >= 55 or med_val == "Knee/Joint Pain":
            goals.append("Flexibility & Posture")
        elif act_val in ["Moderately Active", "Very Active"] and age_val < 42:
            goals.append("Muscle Gain" if np.random.rand() < 0.65 else "Endurance")
        else:
            p = [0.35, 0.20, 0.15, 0.15, 0.15]
            goals.append(np.random.choice([
                "Weight Loss", "Muscle Gain", "Endurance", "Flexibility & Posture", "Stress Relief & General Health"
            ], p=p))

    # 10. Dietary Preference
    diet_choices = ["Vegetarian", "Non-Vegetarian", "Vegan", "Keto"]
    diet_prefs = np.random.choice(diet_choices, size=n_records, p=[0.42, 0.43, 0.10, 0.05])

    # 11. Target Labels for Decision Tree Classifiers
    workout_intensities = []
    workout_splits = []
    diet_strategies = []

    for i in range(n_records):
        age = ages[i]
        bmi = bmis[i]
        goal = goals[i]
        act = activity_levels[i]
        stress = stress_levels[i]
        med = medical_conditions[i]

        # Intensity logic:
        if med in ["Hypertension", "Diabetes", "Knee/Joint Pain"] or age >= 58 or stress >= 8 or bmi >= 33:
            intensity = "Low"
        elif act in ["Very Active", "Moderately Active"] and age < 45 and med == "None" and stress < 7:
            intensity = "High"
        else:
            intensity = "Moderate"
        workout_intensities.append(intensity)

        # Split logic:
        if med == "Knee/Joint Pain":
            split = "Low-Impact Swimming & Upper Body Strength"
        elif med == "Hypertension":
            split = "Aerobic Cardio & Gentle Resistance"
        elif med == "Diabetes":
            split = "Cardio Fat Burn & Light Strength"
        elif goal == "Muscle Gain" and intensity != "Low":
            split = "Hypertrophy Push-Pull-Legs"
        elif goal == "Weight Loss":
            split = "HIIT & Functional Circuit" if intensity == "High" else "Cardio Fat Burn & Light Strength"
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

    # 12. Create Cleaned DataFrame
    df_clean = pd.DataFrame({
        "age": ages,
        "gender": genders,
        "height_cm": heights,
        "weight_kg": weights,
        "bmi": np.round(bmis, 2),
        "goal": goals,
        "activity_level": activity_levels,
        "stress_level": stress_levels,
        "sleep_hours": sleep_hours,
        "medical_condition": medical_conditions,
        "dietary_preference": diet_prefs,
        "workout_intensity": workout_intensities,
        "workout_split": workout_splits,
        "diet_strategy": diet_strategies,
        "recommended_intensity": workout_intensities,
        "recommended_split": workout_splits,
        "recommended_diet": diet_strategies
    })

    print(f"Saving preprocessed dataset to {OUTPUT_DATA_PATH}...")
    df_clean.to_csv(OUTPUT_DATA_PATH, index=False)
    print(f"Successfully processed {len(df_clean):,} records and saved to {OUTPUT_DATA_PATH}!")

    # Summary preview
    print("\nDataset Snapshot:")
    print(df_clean.head(5))
    print("\nTarget Distributions:")
    print("Intensity:\n", df_clean["recommended_intensity"].value_counts(normalize=True))
    print("\nMedical Conditions:\n", df_clean["medical_condition"].value_counts(normalize=True))
    print("\nMean Stress Level:", round(df_clean["stress_level"].mean(), 2))
    print("Mean Sleep Hours:", round(df_clean["sleep_hours"].mean(), 2))
    print("Mean BMI:", round(df_clean["bmi"].mean(), 2))

if __name__ == "__main__":
    preprocess()
