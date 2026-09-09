"""
SQLite Database Layer for AI-Based Personalized Fitness & Mental Wellness Coach
Manages User Profiles, Generated Plans, Daily Progress Logs, and Feedback.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/fitness_wellness.db"

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        height_cm REAL NOT NULL,
        weight_kg REAL NOT NULL,
        goal TEXT NOT NULL,
        activity_level TEXT NOT NULL,
        stress_level INTEGER NOT NULL,
        sleep_hours REAL NOT NULL,
        medical_condition TEXT NOT NULL,
        dietary_preference TEXT NOT NULL,
        cluster_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Plans Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        biometrics_json TEXT NOT NULL,
        ml_insights_json TEXT NOT NULL,
        workout_plan_json TEXT NOT NULL,
        diet_plan_json TEXT NOT NULL,
        mental_plan_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Progress Tracking Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        log_date TEXT NOT NULL,
        weight_kg REAL,
        workouts_completed INTEGER DEFAULT 0,
        mood_rating INTEGER,
        stress_rating INTEGER,
        calories_consumed INTEGER,
        water_liters REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Feedback & Adaptive Learning Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        difficulty_feedback TEXT,
        energy_level TEXT,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Psychological Screenings (PSS-4 & GAD-7) Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS psychological_screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        scale_type TEXT NOT NULL,
        score INTEGER NOT NULL,
        max_score INTEGER NOT NULL,
        severity_level TEXT NOT NULL,
        responses_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully at", DB_PATH)

def save_user(user_dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (
            name, age, gender, height_cm, weight_kg, goal,
            activity_level, stress_level, sleep_hours,
            medical_condition, dietary_preference, cluster_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_dict.get("name", "Guest"),
        user_dict["age"],
        user_dict["gender"],
        user_dict["height_cm"],
        user_dict["weight_kg"],
        user_dict["goal"],
        user_dict["activity_level"],
        user_dict["stress_level"],
        user_dict["sleep_hours"],
        user_dict.get("medical_condition", "None"),
        user_dict.get("dietary_preference", "Vegetarian"),
        user_dict.get("cluster_id", 0)
    ))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def save_recommendations(user_id, recs):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recommendations (
            user_id, biometrics_json, ml_insights_json,
            workout_plan_json, diet_plan_json, mental_plan_json
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        json.dumps(recs["biometrics"]),
        json.dumps(recs["ml_insights"]),
        json.dumps(recs["workout_plan"]),
        json.dumps(recs["diet_plan"]),
        json.dumps(recs["mental_wellness_plan"])
    ))
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def get_latest_recommendation(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM recommendations WHERE user_id = ? ORDER BY id DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "biometrics": json.loads(row["biometrics_json"]),
        "ml_insights": json.loads(row["ml_insights_json"]),
        "workout_plan": json.loads(row["workout_plan_json"]),
        "diet_plan": json.loads(row["diet_plan_json"]),
        "mental_wellness_plan": json.loads(row["mental_plan_json"]),
        "created_at": row["created_at"]
    }

def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

def add_progress_log(user_id, log_data):
    conn = get_connection()
    cursor = conn.cursor()
    log_date = log_data.get("log_date", datetime.now().strftime("%Y-%m-%d"))
    cursor.execute("""
        INSERT INTO progress_logs (
            user_id, log_date, weight_kg, workouts_completed,
            mood_rating, stress_rating, calories_consumed, water_liters, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        log_date,
        log_data.get("weight_kg"),
        log_data.get("workouts_completed", 1),
        log_data.get("mood_rating", 7),
        log_data.get("stress_rating", 5),
        log_data.get("calories_consumed", 2000),
        log_data.get("water_liters", 2.5),
        log_data.get("notes", "")
    ))
    conn.commit()
    conn.close()

def get_progress_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM progress_logs WHERE user_id = ? ORDER BY log_date ASC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_feedback(user_id, feedback_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (user_id, rating, difficulty_feedback, energy_level, comments)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        feedback_data.get("rating", 5),
        feedback_data.get("difficulty_feedback", "Just Right"),
        feedback_data.get("energy_level", "High"),
        feedback_data.get("comments", "")
    ))
    conn.commit()
    conn.close()

def save_psychological_screening(user_id, screening_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO psychological_screenings (
            user_id, scale_type, score, max_score, severity_level, responses_json
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        screening_data.get("scale_type", "PSS-4"),
        screening_data.get("score", 0),
        screening_data.get("max_score", 16),
        screening_data.get("severity_level", "Moderate"),
        json.dumps(screening_data.get("responses", {}))
    ))
    conn.commit()
    screening_id = cursor.lastrowid
    conn.close()
    return screening_id

def get_latest_screenings(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM psychological_screenings 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_user_stress_level(user_id, new_stress_level):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET stress_level = ? WHERE id = ?
    """, (new_stress_level, user_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
