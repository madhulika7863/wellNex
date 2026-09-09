"""
Recommendation Engine for AI-Based Personalized Fitness & Mental Wellness Coach
Combines Machine Learning outputs (K-Means, Decision Tree) with physiological rules
to construct personalized 7-Day Workout Plans, Meal-by-Meal Diets, and Mental Wellness routines.
"""

import os
import json
import joblib
import numpy as np

MODELS_DIR = "ml_engine/models"

class Recommender:
    def __init__(self):
        self.kmeans = None
        self.scaler = None
        self.decision_trees = None
        self.metadata = None
        self._load_models()

    def _load_models(self):
        try:
            metadata_path = os.path.join(MODELS_DIR, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    self.metadata = json.load(f)
                    
            km_path = os.path.join(MODELS_DIR, "kmeans_model.joblib")
            if os.path.exists(km_path):
                self.kmeans = joblib.load(km_path)
                
            sc_path = os.path.join(MODELS_DIR, "scaler.joblib")
            if os.path.exists(sc_path):
                self.scaler = joblib.load(sc_path)
                
            dt_path = os.path.join(MODELS_DIR, "decision_trees.joblib")
            if os.path.exists(dt_path):
                self.decision_trees = joblib.load(dt_path)
        except Exception as e:
            print(f"Notice: Models not fully loaded yet: {e}")

    def calculate_biometrics(self, age, gender, height_cm, weight_kg, activity_level, goal):
        height_m = height_cm / 100.0
        bmi = round(weight_kg / (height_m ** 2), 2)
        
        if bmi < 18.5:
            bmi_category = "Underweight"
            bmi_color = "#38bdf8" # Sky blue
        elif bmi < 25.0:
            bmi_category = "Normal Weight"
            bmi_color = "#34d399" # Emerald green
        elif bmi < 30.0:
            bmi_category = "Overweight"
            bmi_color = "#fbbf24" # Amber
        else:
            bmi_category = "Obese"
            bmi_color = "#f87171" # Rose red

        # BMR using Mifflin-St Jeor Equation
        if gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
            
        activity_multipliers = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725
        }
        mult = activity_multipliers.get(activity_level, 1.375)
        tdee = round(bmr * mult)

        # Calorie Target based on goal
        if goal == "Weight Loss":
            target_calories = max(1200, int(tdee - 450))
        elif goal == "Muscle Gain":
            target_calories = int(tdee + 350)
        else:
            target_calories = int(tdee)
            
        # Target Macronutrients (Grams)
        # Protein: 1.6 - 2.0g per kg for muscle, 1.4 for loss, 1.0 for health
        if goal == "Muscle Gain":
            protein_g = int(weight_kg * 1.8)
            fats_g = int((target_calories * 0.25) / 9)
            carbs_g = int((target_calories - (protein_g * 4 + fats_g * 9)) / 4)
        elif goal == "Weight Loss":
            protein_g = int(weight_kg * 1.5)
            fats_g = int((target_calories * 0.25) / 9)
            carbs_g = int((target_calories - (protein_g * 4 + fats_g * 9)) / 4)
        else:
            protein_g = int(weight_kg * 1.2)
            fats_g = int((target_calories * 0.28) / 9)
            carbs_g = int((target_calories - (protein_g * 4 + fats_g * 9)) / 4)

        return {
            "bmi": bmi,
            "bmi_category": bmi_category,
            "bmi_color": bmi_color,
            "bmr": round(bmr),
            "tdee": tdee,
            "target_calories": target_calories,
            "macros": {
                "protein_g": max(45, protein_g),
                "carbs_g": max(80, carbs_g),
                "fats_g": max(30, fats_g)
            }
        }

    def predict_archetype_and_strategy(self, user_data):
        """
        Uses K-Means clustering to identify user cohort and
        Decision Tree to predict intensity, split, and diet strategy.
        """
        if not self.kmeans or not self.scaler or not self.decision_trees:
            self._load_models()
            
        maps = self.metadata.get("maps", {}) if self.metadata else {}
        act_map = maps.get("activity", {"Sedentary": 0, "Lightly Active": 1, "Moderately Active": 2, "Very Active": 3})
        goal_map = maps.get("goal", {"Weight Loss": 0, "Muscle Gain": 1, "Endurance": 2, "Flexibility & Posture": 3, "Stress Relief & General Health": 4})
        med_map = maps.get("medical", {"None": 0, "Hypertension": 1, "Diabetes": 2, "Asthma": 3, "Knee/Joint Pain": 4, "Back Pain": 5})
        gen_map = maps.get("gender", {"Male": 0, "Female": 1, "Other": 2})

        age = user_data["age"]
        bmi = user_data["bmi"]
        stress = user_data["stress_level"]
        sleep = user_data["sleep_hours"]
        act_num = act_map.get(user_data["activity_level"], 1)
        goal_num = goal_map.get(user_data["goal"], 0)
        med_num = med_map.get(user_data["medical_condition"], 0)
        gen_num = gen_map.get(user_data["gender"], 0)

        # 1. K-Means Cluster Prediction
        cluster_id = 0
        archetype_info = {
            "id": 0,
            "name": "General Wellness Archetype",
            "summary": "Balanced general lifestyle coaching profile."
        }
        
        if self.kmeans and self.scaler:
            feat_k = np.array([[age, bmi, stress, sleep, act_num, goal_num]])
            feat_k_scaled = self.scaler.transform(feat_k)
            cluster_id = int(self.kmeans.predict(feat_k_scaled)[0])
            if self.metadata and "cluster_profiles" in self.metadata:
                c_prof = self.metadata["cluster_profiles"].get(str(cluster_id), {})
                archetype_info = {
                    "id": cluster_id,
                    "name": c_prof.get("name", f"Archetype {cluster_id}"),
                    "summary": c_prof.get("summary", ""),
                    "avg_stress": c_prof.get("avg_stress", 5.0),
                    "avg_bmi": c_prof.get("avg_bmi", 24.0)
                }

        # 2. Decision Tree Predictions
        if self.decision_trees:
            feat_dt = np.array([[age, gen_num, bmi, goal_num, act_num, stress, sleep, med_num]])
            dt_intensity = self.decision_trees["dt_intensity"].predict(feat_dt)[0]
            dt_split = self.decision_trees["dt_split"].predict(feat_dt)[0]
            dt_diet = self.decision_trees["dt_diet"].predict(feat_dt)[0]
        else:
            # Safe Fallback
            dt_intensity = "Moderate" if user_data["medical_condition"] == "None" else "Low"
            dt_split = "Holistic Wellness & Mobility"
            dt_diet = "Nutrient-Dense Balanced Maintenance"

        # Explicit Medical Safety Override
        medical = user_data["medical_condition"]
        health_alert = None
        if medical != "None":
            if medical in ["Hypertension", "Asthma", "Knee/Joint Pain", "Back Pain"]:
                dt_intensity = "Low"
            health_alert = f"Special accommodation applied for {medical}: High-impact and excessive strain exercises omitted for safety."

        return {
            "cluster_id": cluster_id,
            "archetype": archetype_info,
            "predicted_intensity": dt_intensity,
            "predicted_split": dt_split,
            "predicted_diet_strategy": dt_diet,
            "health_alert": health_alert
        }

    def generate_workout_plan(self, split_name, intensity, medical_condition, goal):
        """
        Builds a comprehensive 7-Day workout plan tailored to predicted split and health condition.
        """
        # Rest day mapping or full routine
        workout_library = {
            "Hypertrophy Push-Pull-Legs": [
                {"day": "Day 1 (Push)", "focus": "Chest, Shoulders & Triceps", "exercises": [
                    {"name": "Dumbbell Bench Press", "sets": "4 sets", "reps": "8-12 reps", "rest": "90s", "tip": "Control the descent, maintain tight core."},
                    {"name": "Seated Dumbbell Shoulder Press", "sets": "3 sets", "reps": "10-12 reps", "rest": "75s", "tip": "Avoid arching lower back."},
                    {"name": "Incline Dumbbell Flyes", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Feel the stretch across upper chest."},
                    {"name": "Triceps Rope Pushdowns", "sets": "3 sets", "reps": "12-15 reps", "rest": "60s", "tip": "Squeeze triceps at full lockout."}
                ]},
                {"day": "Day 2 (Pull)", "focus": "Back, Rear Delts & Biceps", "exercises": [
                    {"name": "Lat Pulldowns or Pull-ups", "sets": "4 sets", "reps": "8-10 reps", "rest": "90s", "tip": "Drive elbows downwards."},
                    {"name": "Chest Supported Dumbbell Rows", "sets": "3 sets", "reps": "10-12 reps", "rest": "75s", "tip": "Protect lower spine with bench support."},
                    {"name": "Face Pulls", "sets": "3 sets", "reps": "15 reps", "rest": "60s", "tip": "Great for shoulder health and posture."},
                    {"name": "Dumbbell Hammer Curls", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Keep elbows pinned by your ribs."}
                ]},
                {"day": "Day 3 (Legs & Core)", "focus": "Quadriceps, Hamstrings & Calves", "exercises": [
                    {"name": "Goblet Squats", "sets": "4 sets", "reps": "10-12 reps", "rest": "90s", "tip": "Chest tall, knees tracking over toes."},
                    {"name": "Romanian Deadlifts (Dumbbells)", "sets": "3 sets", "reps": "10-12 reps", "rest": "90s", "tip": "Hinge at hips, slight knee bend."},
                    {"name": "Walking Lunges", "sets": "3 sets", "reps": "10 each leg", "rest": "60s", "tip": "Stable steps, 90-degree angles."},
                    {"name": "Plank Hold", "sets": "3 sets", "reps": "45-60s hold", "rest": "45s", "tip": "Glutes and core fully braced."}
                ]},
                {"day": "Day 4", "focus": "Active Recovery & Mobility", "exercises": [
                    {"name": "Cat-Cow & Thoracic Rotation", "sets": "3 sets", "reps": "10 reps", "rest": "30s", "tip": "Breathe gently with each spinal movement."},
                    {"name": "Brisk 30-min Outdoor Walk", "sets": "1 session", "reps": "30 mins", "rest": "N/A", "tip": "Maintain conversational breathing pace."}
                ]},
                {"day": "Day 5 (Upper Body Power)", "focus": "Full Upper Sculpting", "exercises": [
                    {"name": "Incline Dumbbell Press", "sets": "3 sets", "reps": "10 reps", "rest": "75s", "tip": "Solid shoulder retraction."},
                    {"name": "Seated Cable Rows", "sets": "3 sets", "reps": "10-12 reps", "rest": "75s", "tip": "Hold contraction for 1 second."},
                    {"name": "Lateral Shoulder Raises", "sets": "3 sets", "reps": "15 reps", "rest": "60s", "tip": "Lead with elbows, light weight."},
                    {"name": "Overhead Tricep Extension", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Keep elbows close together."}
                ]},
                {"day": "Day 6 (Lower Body & Abs)", "focus": "Posterior Chain & Core", "exercises": [
                    {"name": "Leg Press or Bodyweight Squats", "sets": "3 sets", "reps": "12 reps", "rest": "75s", "tip": "Smooth cadence."},
                    {"name": "Lying Leg Curls / Glute Bridges", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Squeeze glutes at top."},
                    {"name": "Hanging Knee Raises", "sets": "3 sets", "reps": "12 reps", "rest": "45s", "tip": "Avoid swinging momentum."}
                ]},
                {"day": "Day 7", "focus": "Rest & Regeneration", "exercises": [
                    {"name": "Full Body Static Stretching", "sets": "1 session", "reps": "15 mins", "rest": "N/A", "tip": "Hold each stretch for 25-30s."}
                ]}
            ],
            "Low-Impact Swimming & Upper Body Strength": [
                {"day": "Day 1", "focus": "Joint-Friendly Upper Body", "exercises": [
                    {"name": "Seated Chest Press (Machine/Band)", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Zero knee strain."},
                    {"name": "Seated Cable Row", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Keep spine neutral."},
                    {"name": "Light Dumbbell Bicep Curls", "sets": "3 sets", "reps": "12 reps", "rest": "45s", "tip": "Controlled tempo."}
                ]},
                {"day": "Day 2", "focus": "Low-Impact Aquatic Cardio / Walking", "exercises": [
                    {"name": "Lap Swimming or Water Aerobics", "sets": "1 session", "reps": "30 mins", "rest": "N/A", "tip": "Water buoyancy relieves 90% knee pressure."},
                    {"name": "Glute Bridges on Mat", "sets": "3 sets", "reps": "12 reps", "rest": "45s", "tip": "Strengthens hips without knee torque."}
                ]},
                {"day": "Day 3", "focus": "Core & Upper Back Posture", "exercises": [
                    {"name": "Deadbugs", "sets": "3 sets", "reps": "10 each side", "rest": "45s", "tip": "Keep lower back pressed flat."},
                    {"name": "Resistance Band Pull-Aparts", "sets": "3 sets", "reps": "15 reps", "rest": "30s", "tip": "Strengthens upper scapular area."},
                    {"name": "Bird-Dog Pose", "sets": "3 sets", "reps": "8 each side", "rest": "45s", "tip": "Balance and spinal stabilization."}
                ]},
                {"day": "Day 4", "focus": "Gentle Rest & Joint Mobility", "exercises": [
                    {"name": "Seated Hamstring & Quad Foam Rolling", "sets": "1 session", "reps": "15 mins", "rest": "N/A", "tip": "Relieves tension around joints."}
                ]},
                {"day": "Day 5", "focus": "Seated Functional Strength", "exercises": [
                    {"name": "Seated Dumbbell Shoulder Press", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Gentle overhead range."},
                    {"name": "Lat Pulldown (Light Resistance)", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Smooth downward pull."},
                    {"name": "Straight Leg Mat Raises", "sets": "3 sets", "reps": "10 reps", "rest": "45s", "tip": "Strengthens quadriceps without bending knee joint."}
                ]},
                {"day": "Day 6", "focus": "Recumbent Bike / Easy Elliptical", "exercises": [
                    {"name": "Recumbent Stationary Bike (Low Resistance)", "sets": "1 session", "reps": "25 mins", "rest": "N/A", "tip": "Zero impact, promotes synovial fluid circulation."}
                ]},
                {"day": "Day 7", "focus": "Mindful Rest & Relaxation", "exercises": [
                    {"name": "Gentle Chair Yoga & Deep Breathing", "sets": "1 session", "reps": "20 mins", "rest": "N/A", "tip": "Calms the nervous system."}
                ]}
            ],
            "Core Stability & Gentle Mobility": [
                {"day": "Day 1", "focus": "Spine-Safe Core Strengthening", "exercises": [
                    {"name": "Bird-Dog Exercise", "sets": "3 sets", "reps": "10 each side", "rest": "45s", "tip": "Avoid hyper-extending the lower back."},
                    {"name": "Glute Bridges", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Activate glutes to unload lumbar spine."},
                    {"name": "McGill Curl-up", "sets": "3 sets", "reps": "8 reps (5s hold)", "rest": "45s", "tip": "Safe abdominal crunch that preserves spinal alignment."}
                ]},
                {"day": "Day 2", "focus": "Paced Walking & Posture Drill", "exercises": [
                    {"name": "Brisk Flat-Ground Walking", "sets": "1 session", "reps": "30 mins", "rest": "N/A", "tip": "Swing arms naturally; maintain upright spine."},
                    {"name": "Standing Chest Stretch & Wall Slides", "sets": "3 sets", "reps": "10 reps", "rest": "30s", "tip": "Counters desk posture and back strain."}
                ]},
                {"day": "Day 3", "focus": "Supported Upper Body", "exercises": [
                    {"name": "Chest-Supported Dumbbell Rows", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Bench entirely protects the lumbar back."},
                    {"name": "Resistance Band Bicep Curls", "sets": "3 sets", "reps": "12 reps", "rest": "45s", "tip": "Smooth, joint-friendly tension."},
                    {"name": "Seated Band Face Pulls", "sets": "3 sets", "reps": "15 reps", "rest": "45s", "tip": "Enhance thoracic carriage."}
                ]},
                {"day": "Day 4", "focus": "Active Spinal Decompression", "exercises": [
                    {"name": "Cat-Cow Gentle Flow", "sets": "3 sets", "reps": "10 cycles", "rest": "30s", "tip": "Slow, pain-free range of motion only."},
                    {"name": "Child's Pose with Arm Reach", "sets": "3 sets", "reps": "30s hold", "rest": "30s", "tip": "Gentle gentle stretch across lats."}
                ]},
                {"day": "Day 5", "focus": "Lower Body Stability (No Spinal Loading)", "exercises": [
                    {"name": "Supported Step-ups on Low Step", "sets": "3 sets", "reps": "10 each leg", "rest": "60s", "tip": "Hold handrail for complete balance."},
                    {"name": "Side-Lying Clamshells", "sets": "3 sets", "reps": "15 each side", "rest": "45s", "tip": "Strengthens hip abductors to protect back."},
                    {"name": "Farmer's Walk (Light weights)", "sets": "3 sets", "reps": "40 steps", "rest": "60s", "tip": "Brace core, maintain straight posture."}
                ]},
                {"day": "Day 6", "focus": "Restorative Swimming or Walking", "exercises": [
                    {"name": "Gentle Free-Flow Walking or Swim", "sets": "1 session", "reps": "25 mins", "rest": "N/A", "tip": "Decompresses spinal discs."}
                ]},
                {"day": "Day 7", "focus": "Mindful Rest & Guided Meditation", "exercises": [
                    {"name": "Mindful Breathwork & Hamstring Stretch", "sets": "1 session", "reps": "20 mins", "rest": "N/A", "tip": "Loosen tight hamstrings that pull on lumbar."}
                ]}
            ]
        }

        # Default standard full body if split isn't explicitly one of above
        default_routine = [
            {"day": "Day 1 (Full Body Flow)", "focus": "Total Body Conditioning", "exercises": [
                {"name": "Bodyweight or Goblet Squats", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Keep core engaged, chest elevated."},
                {"name": "Push-ups (Standard or Incline)", "sets": "3 sets", "reps": "10-12 reps", "rest": "60s", "tip": "Keep elbows at 45-degree angle."},
                {"name": "Dumbbell or Band Rows", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Pull back with shoulder blades."},
                {"name": "Plank Hold", "sets": "3 sets", "reps": "30-45s", "rest": "45s", "tip": "Straight line from head to heels."}
            ]},
            {"day": "Day 2 (Cardio & Breath)", "focus": "Cardiovascular Stamina", "exercises": [
                {"name": "Brisk Incline Treadmill or Outdoor Walk", "sets": "1 session", "reps": "30 mins", "rest": "N/A", "tip": "Moderate heart rate zone 2."},
                {"name": "Jumping Jacks or Step Jacks", "sets": "3 sets", "reps": "40s work", "rest": "20s", "tip": "Choose step-jacks if low impact preferred."}
            ]},
            {"day": "Day 3 (Active Recovery)", "focus": "Mobility & Mental De-Stress", "exercises": [
                {"name": "Yoga Sun Salutations (Gentle)", "sets": "5 rounds", "reps": "Slow pace", "rest": "30s", "tip": "Synchronize breath with movement."},
                {"name": "Hip Flexor & Quad Stretch", "sets": "3 sets", "reps": "30s hold", "rest": "30s", "tip": "Release pelvic tension."}
            ]},
            {"day": "Day 4 (Strength & Tone)", "focus": "Upper & Core Strength", "exercises": [
                {"name": "Overhead Shoulder Press", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Steady controlled motion."},
                {"name": "Dumbbell Deadlifts / Glute Bridges", "sets": "3 sets", "reps": "12 reps", "rest": "60s", "tip": "Drive through heels."},
                {"name": "Bicycle Crunches", "sets": "3 sets", "reps": "15 each side", "rest": "45s", "tip": "Smooth alternating twist."}
            ]},
            {"day": "Day 5 (HIIT / Steady Burn)", "focus": "Metabolic Acceleration", "exercises": [
                {"name": "Bodyweight Alternating Lunges", "sets": "3 sets", "reps": "10 each leg", "rest": "45s", "tip": "Keep upright torso."},
                {"name": "Mountain Climbers (Paced)", "sets": "3 sets", "reps": "30s work", "rest": "30s", "tip": "Drive knees smoothly."},
                {"name": "Jump Rope or Shadow Boxing", "sets": "3 rounds", "reps": "2 mins each", "rest": "60s", "tip": "Light on toes."}
            ]},
            {"day": "Day 6 (Functional Agility)", "focus": "Coordination & Core", "exercises": [
                {"name": "Side Planks", "sets": "3 sets", "reps": "30s each side", "rest": "30s", "tip": "Keep hips lifted high."},
                {"name": "Farmer's Carry", "sets": "3 sets", "reps": "45 seconds", "rest": "60s", "tip": "Grip dumbbells firmly, shoulders back."}
            ]},
            {"day": "Day 7 (Rest & Mindfulness)", "focus": "Complete Reset", "exercises": [
                {"name": "Guided Deep Breathing & Light Walk", "sets": "1 session", "reps": "20 mins", "rest": "N/A", "tip": "Prepare body and mind for the week ahead."}
            ]}
        ]

        routine = workout_library.get(split_name, default_routine)
        
        # Apply intensity multiplier adjustment
        adjusted_routine = []
        for day in routine:
            day_copy = dict(day)
            day_copy["intensity_badge"] = intensity
            day_copy["warmup"] = "5-min Dynamic mobility (Arm circles, leg swings, torso twists)"
            day_copy["cooldown"] = "5-min Gentle static stretching & 4-7-8 breathing"
            adjusted_routine.append(day_copy)

        return {
            "split_name": split_name,
            "recommended_intensity": intensity,
            "weekly_days": len(adjusted_routine),
            "safety_note": f"Adjusted for {medical_condition}" if medical_condition != "None" else "Standard safe execution form",
            "schedule": adjusted_routine
        }

    def generate_diet_plan(self, diet_strategy, preference, target_calories, macros, medical_condition):
        """
        Creates meal-by-meal daily nutrition aligned with calories, macros, and preferences.
        """
        is_veg = preference in ["Vegetarian", "Vegan"]
        is_vegan = preference == "Vegan"
        is_keto = preference == "Keto"

        # Meal options database
        breakfast_options = {
            "Vegetarian": [
                {"name": "Oatmeal with Almond Butter & Chia Seeds", "desc": "Rolled oats, almond milk, crushed walnuts, cinnamon, scoop of plant protein.", "calories": int(target_calories * 0.25), "protein": "24g", "carbs": "45g", "fats": "14g"},
                {"name": "Paneer & Spinach Scramble with Whole Wheat Toast", "desc": "100g low-fat paneer cooked with turmeric, spinach, tomatoes, and 2 slices multi-grain bread.", "calories": int(target_calories * 0.25), "protein": "26g", "carbs": "32g", "fats": "12g"}
            ],
            "Non-Vegetarian": [
                {"name": "3-Egg Veggie Omelette with Whole Grain Toast", "desc": "2 whole eggs + 2 egg whites with mushrooms, bell peppers, spinach, and avocado.", "calories": int(target_calories * 0.25), "protein": "30g", "carbs": "28g", "fats": "15g"},
                {"name": "Greek Yogurt Parfait with Whey Protein & Berries", "desc": "1.5 cups Greek yogurt mixed with scoop whey, blueberries, and pumpkin seeds.", "calories": int(target_calories * 0.25), "protein": "36g", "carbs": "30g", "fats": "9g"}
            ],
            "Vegan": [
                {"name": "Tofu Scramble with Avocado & Sourdough", "desc": "Crumbled firm tofu sauteed with nutritional yeast, spinach, and half avocado on toasted sourdough.", "calories": int(target_calories * 0.25), "protein": "25g", "carbs": "35g", "fats": "16g"}
            ],
            "Keto": [
                {"name": "Avocado & Egg Bacon Bowl", "desc": "2 poached eggs, crispy bacon bits, half sliced avocado, olive oil drizzle over baby greens.", "calories": int(target_calories * 0.25), "protein": "26g", "carbs": "6g", "fats": "28g"}
            ]
        }

        lunch_options = {
            "Vegetarian": [
                {"name": "Quinoa & Chickpea Protein Bowl", "desc": "Cooked quinoa, roasted chickpeas, cucumber, cherry tomatoes, mint-yogurt dressing.", "calories": int(target_calories * 0.35), "protein": "28g", "carbs": "62g", "fats": "14g"},
                {"name": "Dal Tadka with Brown Rice & Steamed Greens", "desc": "Lentil soup with roasted cumin, brown rice, side of sauteed seasonal vegetables.", "calories": int(target_calories * 0.35), "protein": "25g", "carbs": "65g", "fats": "11g"}
            ],
            "Non-Vegetarian": [
                {"name": "Grilled Lemon Herb Chicken Breast with Sweet Potato", "desc": "180g marinated chicken breast, baked sweet potato wedges, and steamed broccoli.", "calories": int(target_calories * 0.35), "protein": "44g", "carbs": "45g", "fats": "10g"},
                {"name": "Salmon Fillet with Quinoa & Asparagus", "desc": "Pan-seared wild salmon (150g), quinoa, roasted asparagus drizzled with olive oil.", "calories": int(target_calories * 0.35), "protein": "38g", "carbs": "35g", "fats": "18g"}
            ],
            "Vegan": [
                {"name": "Tempeh & Edamame Brown Rice Bowl", "desc": "Pan-browned marinated tempeh, shelled edamame, steamed broccoli, brown rice, tahini drizzle.", "calories": int(target_calories * 0.35), "protein": "34g", "carbs": "55g", "fats": "15g"}
            ],
            "Keto": [
                {"name": "Grilled Chicken Caesar Salad (No Croutons)", "desc": "Grilled chicken strips, romaine lettuce, parmesan shavings, rich olive oil caesar dressing.", "calories": int(target_calories * 0.35), "protein": "42g", "carbs": "7g", "fats": "32g"}
            ]
        }

        snack_options = {
            "Vegetarian": [
                {"name": "Roasted Makhana (Foxnuts) & Roasted Almonds", "desc": "Handful of crisp foxnuts seasoned with rock salt + 10 almonds with green tea.", "calories": int(target_calories * 0.15), "protein": "9g", "carbs": "18g", "fats": "8g"},
                {"name": "Sprouted Moong Salad", "desc": "Steamed moong sprouts tossed with lemon juice, onions, tomatoes, and chaat masala.", "calories": int(target_calories * 0.15), "protein": "12g", "carbs": "22g", "fats": "2g"}
            ],
            "Non-Vegetarian": [
                {"name": "Boiled Egg Whites & Walnuts", "desc": "3 boiled egg whites paired with a handful of raw walnuts and green tea.", "calories": int(target_calories * 0.15), "protein": "16g", "carbs": "6g", "fats": "10g"}
            ],
            "Vegan": [
                {"name": "Hummus with Carrot & Cucumber Sticks", "desc": "4 tbsp rich garlic chickpea hummus served with crunchy raw vegetable sticks.", "calories": int(target_calories * 0.15), "protein": "8g", "carbs": "20g", "fats": "7g"}
            ],
            "Keto": [
                {"name": "Pecan Nuts & String Cheese", "desc": "1 oz raw pecans paired with whole milk mozzarella string cheese.", "calories": int(target_calories * 0.15), "protein": "10g", "carbs": "3g", "fats": "20g"}
            ]
        }

        dinner_options = {
            "Vegetarian": [
                {"name": "Grilled Tofu/Paneer Tikka with Sautéed Veggies", "desc": "150g spiced cottage cheese/tofu skewers, grilled bell peppers, onions, mint chutney.", "calories": int(target_calories * 0.25), "protein": "26g", "carbs": "18g", "fats": "14g"},
                {"name": "Clear Vegetable Soup with Lentil Patties", "desc": "Hearty vegetable broth loaded with mushrooms, greens, served with 2 baked lentil tikkis.", "calories": int(target_calories * 0.25), "protein": "20g", "carbs": "32g", "fats": "6g"}
            ],
            "Non-Vegetarian": [
                {"name": "Baked Herb Cod/Tilapia with Sautéed Zucchini & Greens", "desc": "200g white fish baked with olive oil, garlic, and fresh herbs, served with stir-fried greens.", "calories": int(target_calories * 0.25), "protein": "40g", "carbs": "12g", "fats": "8g"},
                {"name": "Grilled Turkey/Chicken Stir-Fry", "desc": "Diced chicken breast stir-fried with bok choy, snap peas, ginger, and soy sauce.", "calories": int(target_calories * 0.25), "protein": "38g", "carbs": "15g", "fats": "7g"}
            ],
            "Vegan": [
                {"name": "Lentil Shepherd's Pie with Cauliflower Mash", "desc": "Savory brown lentil and vegetable stew topped with creamy mashed cauliflower.", "calories": int(target_calories * 0.25), "protein": "22g", "carbs": "38g", "fats": "8g"}
            ],
            "Keto": [
                {"name": "Pan-Seared Salmon with Garlic Butter Spinach", "desc": "Rich salmon fillet served over a bed of spinach wilted in grass-fed butter.", "calories": int(target_calories * 0.25), "protein": "35g", "carbs": "4g", "fats": "26g"}
            ]
        }

        # Select meal category safely
        pref_key = preference if preference in breakfast_options else "Vegetarian"
        
        b = breakfast_options[pref_key][0]
        l = lunch_options[pref_key][0]
        s = snack_options[pref_key][0]
        d = dinner_options[pref_key][0]

        special_advice = []
        if medical_condition == "Diabetes":
            special_advice.append("Prioritize low glycemic foods; avoid refined sugars and fruit juices.")
        elif medical_condition == "Hypertension":
            special_advice.append("Keep sodium intake below 2,000 mg/day; season meals with herbs, garlic, and lemon.")
        elif medical_condition in ["Knee/Joint Pain", "Back Pain"]:
            special_advice.append("Include omega-3 rich ingredients (flaxseeds, chia, walnuts) to reduce systemic inflammation.")

        return {
            "strategy_title": diet_strategy,
            "target_calories": target_calories,
            "macronutrients": macros,
            "water_target_liters": 3.0,
            "special_diet_guidance": special_advice,
            "meals": {
                "breakfast": b,
                "lunch": l,
                "evening_snack": s,
                "dinner": d
            }
        }

    def generate_mental_wellness_plan(self, stress_level, sleep_hours):
        """
        Creates personalized mental wellness support including breathing pacing,
        meditation schedules, and stress management habits.
        """
        if stress_level >= 7:
            stress_state = "Elevated Stress (Priority Intervention)"
            stress_color = "#f87171"
            daily_breathing_sessions = 3
            meditation_duration_min = 15
            primary_focus = "Cortisol Reduction & Parasympathetic Nervous System Activation"
        elif stress_level >= 4:
            stress_state = "Moderate Stress (Active Management)"
            stress_color = "#fbbf24"
            daily_breathing_sessions = 2
            meditation_duration_min = 10
            primary_focus = "Mental Focus, Clarity & Evening Wind-Down"
        else:
            stress_state = "Optimal Wellness (Preventative)"
            stress_color = "#34d399"
            daily_breathing_sessions = 1
            meditation_duration_min = 10
            primary_focus = "Mindfulness, Gratitude & Peak Cognitive Energy"

        tips = [
            {"title": "4-7-8 Breathing Pacing", "desc": "Inhale quietly through the nose for 4 seconds, hold breath for 7 seconds, exhale audibly through mouth for 8 seconds. Repeat 4 cycles."},
            {"title": "Digital Sunset Rule", "desc": f"Turn off screens 45 minutes prior to sleep to improve your current {sleep_hours}h sleep cycle and boost natural melatonin production."},
            {"title": "Progressive Muscle Relaxation", "desc": "Before bed, systematically tense and slowly release each muscle group from your toes up to your neck."},
            {"title": "5-Minute Morning Gratitude Journal", "desc": "Note down 3 specific things you are grateful for each morning to prime the brain for resilience."}
        ]

        return {
            "stress_level": stress_level,
            "stress_state": stress_state,
            "stress_color": stress_color,
            "primary_focus": primary_focus,
            "daily_breathing_sessions": daily_breathing_sessions,
            "recommended_meditation_minutes": meditation_duration_min,
            "wellness_tips": tips
        }

    def generate_full_recommendations(self, user_data):
        biometrics = self.calculate_biometrics(
            age=user_data["age"],
            gender=user_data["gender"],
            height_cm=user_data["height_cm"],
            weight_kg=user_data["weight_kg"],
            activity_level=user_data["activity_level"],
            goal=user_data["goal"]
        )
        
        user_data["bmi"] = biometrics["bmi"]
        
        ml_prediction = self.predict_archetype_and_strategy(user_data)
        
        workout_plan = self.generate_workout_plan(
            split_name=ml_prediction["predicted_split"],
            intensity=ml_prediction["predicted_intensity"],
            medical_condition=user_data.get("medical_condition", "None"),
            goal=user_data["goal"]
        )
        
        diet_plan = self.generate_diet_plan(
            diet_strategy=ml_prediction["predicted_diet_strategy"],
            preference=user_data.get("dietary_preference", "Vegetarian"),
            target_calories=biometrics["target_calories"],
            macros=biometrics["macros"],
            medical_condition=user_data.get("medical_condition", "None")
        )
        
        mental_plan = self.generate_mental_wellness_plan(
            stress_level=user_data.get("stress_level", 5),
            sleep_hours=user_data.get("sleep_hours", 7.0)
        )
        
        return {
            "biometrics": biometrics,
            "ml_insights": ml_prediction,
            "workout_plan": workout_plan,
            "diet_plan": diet_plan,
            "mental_wellness_plan": mental_plan
        }
