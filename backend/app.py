"""
Flask Web Application & REST API Server for
AI-Based Personalized Fitness & Mental Wellness Coach
Project Architecture: Madan Mohan Malaviya University of Technology (MMMUT), Gorakhpur
"""

import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from backend.database import (
    init_db, save_user, save_recommendations,
    get_latest_recommendation, get_user,
    add_progress_log, get_progress_history, save_feedback,
    save_psychological_screening, get_latest_screenings, update_user_stress_level
)
from ml_engine.recommender import Recommender
from backend.chatbot import FitnessWellnessChatbot

# Configure paths
TEMPLATE_DIR = os.path.abspath("templates")
STATIC_DIR = os.path.abspath("static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# Initialize engines
recommender = Recommender()
chatbot = FitnessWellnessChatbot()

# Ensure Database is initialized
init_db()

# Enable CORS manually for cross-origin requests
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE,OPTIONS"
    return response

@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------------------------------------
# 1. Assessment & Recommendation Generation
# -------------------------------------------------------------
@app.route("/api/user/assess", methods=["POST"])
def assess_user():
    try:
        data = request.get_json(force=True)
        # Required input sanitization
        age = int(data.get("age", 25))
        gender = str(data.get("gender", "Male"))
        height_cm = float(data.get("height_cm", 170))
        weight_kg = float(data.get("weight_kg", 70))
        goal = str(data.get("goal", "Weight Loss"))
        activity_level = str(data.get("activity_level", "Lightly Active"))
        stress_level = int(data.get("stress_level", 5))
        sleep_hours = float(data.get("sleep_hours", 7.0))
        medical_condition = str(data.get("medical_condition", "None"))
        dietary_preference = str(data.get("dietary_preference", "Vegetarian"))
        name = str(data.get("name", "Fitness Explorer"))

        user_input = {
            "name": name,
            "age": age,
            "gender": gender,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "goal": goal,
            "activity_level": activity_level,
            "stress_level": stress_level,
            "sleep_hours": sleep_hours,
            "medical_condition": medical_condition,
            "dietary_preference": dietary_preference
        }

        # Generate full recommendations using ML + Physiological rules
        recs = recommender.generate_full_recommendations(user_input)

        # Save to DB
        user_input["cluster_id"] = recs["ml_insights"]["cluster_id"]
        user_id = save_user(user_input)
        rec_id = save_recommendations(user_id, recs)

        # Add initial progress entry
        add_progress_log(user_id, {
            "weight_kg": weight_kg,
            "workouts_completed": 0,
            "mood_rating": 7,
            "stress_rating": stress_level,
            "calories_consumed": recs["biometrics"]["target_calories"],
            "water_liters": 2.0,
            "notes": "Initial assessment completed."
        })

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "user": user_input,
            "recommendations": recs
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 400

# -------------------------------------------------------------
# 2. Get User Profile & Latest Recommendations
# -------------------------------------------------------------
@app.route("/api/user/<int:user_id>/profile", methods=["GET"])
def get_user_profile(user_id):
    user = get_user(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    recs = get_latest_recommendation(user_id)
    return jsonify({
        "status": "success",
        "user": user,
        "recommendations": recs
    })

# -------------------------------------------------------------
# 3. Daily Progress Tracking
# -------------------------------------------------------------
@app.route("/api/user/<int:user_id>/progress", methods=["POST"])
def log_progress(user_id):
    try:
        data = request.get_json(force=True)
        add_progress_log(user_id, data)
        return jsonify({"status": "success", "message": "Progress logged successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/user/<int:user_id>/progress", methods=["GET"])
def get_user_progress(user_id):
    history = get_progress_history(user_id)
    return jsonify({
        "status": "success",
        "history": history
    })

# -------------------------------------------------------------
# 4. Adaptive Feedback Module
# -------------------------------------------------------------
@app.route("/api/user/<int:user_id>/feedback", methods=["POST"])
def submit_feedback(user_id):
    try:
        data = request.get_json(force=True)
        save_feedback(user_id, data)

        difficulty = data.get("difficulty_feedback", "Just Right")
        user = get_user(user_id)
        latest_rec = get_latest_recommendation(user_id)

        adapted = False
        if latest_rec and difficulty in ["Too Hard", "Too Easy"]:
            workout_plan = latest_rec["workout_plan"]
            current_intensity = workout_plan.get("recommended_intensity", "Moderate")

            if difficulty == "Too Hard":
                new_intensity = "Low" if current_intensity == "Moderate" else "Moderate"
                workout_plan["recommended_intensity"] = new_intensity
                workout_plan["safety_note"] = f"Adapted based on user feedback: lowered intensity to {new_intensity}."
                for day in workout_plan.get("schedule", []):
                    day["intensity_badge"] = new_intensity
                adapted = True
            elif difficulty == "Too Easy":
                new_intensity = "High" if current_intensity == "Moderate" else "Moderate"
                workout_plan["recommended_intensity"] = new_intensity
                workout_plan["safety_note"] = f"Adapted based on user feedback: raised intensity to {new_intensity}."
                for day in workout_plan.get("schedule", []):
                    day["intensity_badge"] = new_intensity
                adapted = True

            if adapted:
                latest_rec["workout_plan"] = workout_plan
                save_recommendations(user_id, latest_rec)

        return jsonify({
            "status": "success",
            "message": "Feedback recorded",
            "adapted": adapted,
            "updated_plan": latest_rec["workout_plan"] if adapted else None
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# -------------------------------------------------------------
# 5. AI Chatbot Interaction
# -------------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        message = data.get("message", "")
        user_id = data.get("user_id")
        
        user_ctx = None
        if user_id:
            user = get_user(user_id)
            if user:
                recs = get_latest_recommendation(user_id)
                user_ctx = {
                    "name": user.get("name"),
                    "goal": user.get("goal"),
                    "bmi": recs["biometrics"]["bmi"] if recs else 23.0,
                    "medical_condition": user.get("medical_condition"),
                    "stress_level": user.get("stress_level")
                }
                
        reply = chatbot.respond(message, user_context=user_ctx)
        return jsonify({"status": "success", "response": reply})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# -------------------------------------------------------------
# 6. ML Model Diagnostics & Metrics (For Viva / Academic Showcase)
# -------------------------------------------------------------
@app.route("/api/ml/metrics", methods=["GET"])
def get_ml_metrics():
    try:
        meta_path = os.path.join("ml_engine", "models", "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                meta = json.load(f)
            return jsonify({"status": "success", "metrics": meta})
        else:
            return jsonify({"status": "error", "message": "ML models not trained yet."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# -------------------------------------------------------------
# 7. Standardized Psychological Assessment (PSS-4 & GAD-7)
# -------------------------------------------------------------
@app.route("/api/mental/screening", methods=["POST"])
def submit_psychological_screening():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        scale_type = data.get("scale_type", "PSS-4")  # "PSS-4" or "GAD-7"
        responses = data.get("responses", {})

        score = 0
        max_score = 16 if scale_type == "PSS-4" else 21
        severity = "Moderate"
        feedback = ""
        tips = []

        if scale_type == "PSS-4":
            # PSS-4 scoring: Q1 (0-4), Q2 (reversed 4-val), Q3 (reversed 4-val), Q4 (0-4)
            q1 = int(responses.get("q1", 0))
            q2 = 4 - int(responses.get("q2", 0))
            q3 = 4 - int(responses.get("q3", 0))
            q4 = int(responses.get("q4", 0))
            score = max(0, min(16, q1 + q2 + q3 + q4))

            if score <= 5:
                severity = "Low Stress"
                feedback = "Your perceived stress level is well within the healthy, resilient range. Continue maintaining your balanced routine."
                tips = ["Daily 5-min morning meditation", "Consistent sleep schedule", "Light physical activity"]
            elif score <= 10:
                severity = "Moderate Stress"
                feedback = "You are experiencing moderate stress accumulation. Incorporating active parasympathetic relaxation will help restore emotional equilibrium."
                tips = ["4-7-8 Breathing twice daily", "Digital Sunset 45 mins before bedtime", "Take 10-minute mindful walks"]
            else:
                severity = "High Stress"
                feedback = "Your responses indicate high perceived stress and mental fatigue. Prioritize restorative recovery, deep breathing pacing, and lower workout strain."
                tips = ["4-7-8 Vagus nerve breathing pacer", "15-minute guided meditation", "Reduce workout volume to restorative active recovery"]

        elif scale_type == "GAD-7":
            # GAD-7 scoring: 7 items (0-3 each), total 0-21
            for i in range(1, 8):
                score += int(responses.get(f"q{i}", 0))
            score = max(0, min(21, score))

            if score <= 4:
                severity = "Minimal Anxiety"
                feedback = "Minimal to no symptoms of general anxiety detected. Your psychological resilience is strong."
                tips = ["Maintain current mindfulness rituals", "Regular aerobic exercise", "Daily hydration"]
            elif score <= 9:
                severity = "Mild Anxiety"
                feedback = "Mild symptoms of situational anxiety or worry present. Gentle grounding exercises and breathwork can help prevent escalation."
                tips = ["Box breathing or 4-7-8 breathing", "Evening wind-down routine", "Limit caffeine after 2 PM"]
            elif score <= 14:
                severity = "Moderate Anxiety"
                feedback = "Noticeable symptoms of anxiety and nervous tension. Daily structured calming practices are strongly recommended."
                tips = ["Guided meditation sessions (10-15 mins)", "Progressive Muscle Relaxation", "Gentle yoga and stretching"]
            else:
                severity = "Severe Anxiety"
                feedback = "Significant levels of anxiety and nervous hyperarousal detected. Dedicate focused attention to deep vagus nerve stimulation and restorative wellness habits."
                tips = ["4-7-8 Breathing 3 times daily", "Gentle low-impact mobility over high-intensity workouts", "Mindful reflection and journaling"]

        screening_record = {
            "scale_type": scale_type,
            "score": score,
            "max_score": max_score,
            "severity_level": severity,
            "responses": responses
        }

        screening_id = None
        if user_id:
            screening_id = save_psychological_screening(user_id, screening_record)

        return jsonify({
            "status": "success",
            "screening_id": screening_id,
            "scale_type": scale_type,
            "score": score,
            "max_score": max_score,
            "severity_level": severity,
            "feedback": feedback,
            "recommended_actions": tips
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/mental/screening/<int:user_id>", methods=["GET"])
def get_user_screenings(user_id):
    try:
        history = get_latest_screenings(user_id, limit=10)
        return jsonify({"status": "success", "history": history})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/mental/sync-stress", methods=["POST"])
def sync_stress_to_profile():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        stress_level = int(data.get("stress_level", 5))
        stress_level = max(1, min(10, stress_level))

        if not user_id:
            return jsonify({"status": "error", "message": "User ID is required"}), 400

        user = get_user(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Update in DB
        update_user_stress_level(user_id, stress_level)
        user["stress_level"] = stress_level

        # Re-run recommendation engine with updated stress level
        recs = recommender.generate_full_recommendations(user)
        save_recommendations(user_id, recs)

        return jsonify({
            "status": "success",
            "message": f"Stress level synchronized to {stress_level}/10. Recommendations dynamically recalibrated.",
            "stress_level": stress_level,
            "recommendations": recs
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
