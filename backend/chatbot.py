"""
Intelligent AI Chatbot for Fitness & Mental Wellness Coaching
Context-aware assistant combining user profile, biometrics, and mental wellness state.
"""

import os
import re

class FitnessWellnessChatbot:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"GenAI Client initialization notice: {e}")

    def respond(self, message, user_context=None):
        """
        Generates a contextual response tailored to the user's health conditions,
        BMI, stress level, and fitness goals.
        """
        message_clean = message.strip()
        msg_lower = message_clean.lower()
        
        ctx_text = ""
        user_name = "there"
        user_goal = "Health & Fitness"
        user_bmi = "Normal"
        user_med = "None"
        user_stress = 5
        
        if user_context:
            user_name = user_context.get("name", "there")
            user_goal = user_context.get("goal", "Health & Fitness")
            user_bmi = user_context.get("bmi", 23.0)
            user_med = user_context.get("medical_condition", "None")
            user_stress = user_context.get("stress_level", 5)
            ctx_text = f"User is {user_name}, Goal: {user_goal}, BMI: {user_bmi}, Medical condition: {user_med}, Stress: {user_stress}/10."

        # If Gemini client is active, try to get response from Gemini
        if self.client:
            try:
                system_prompt = f"""
                You are 'WellNex Guide', a dedicated personal fitness coach, sports nutritionist, and wellness counselor.
                Context of the active user: {ctx_text}
                Always be encouraging, scientifically grounded, empathetic, and safety-first.
                If the user has a medical condition ({user_med}), always provide safe modifications.
                Keep responses concise (2-4 paragraphs or bullet points), practical, and actionable.
                Never state or imply that you are an AI, language model, chatbot, or virtual assistant. Never mention OpenAI, Google, or Gemini. Always speak naturally and directly as the user's dedicated WellNex health guide.
                """
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[system_prompt, message_clean]
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"Gemini API fallback to knowledge base: {e}")

        # Intelligent Built-in Knowledge & Contextual Reasoning Engine
        # 1. Stress / Anxiety / Mental Wellness Queries
        if any(w in msg_lower for w in ["stress", "anxiety", "overwhelm", "relax", "calm", "meditat", "breathing", "panic", "sleep"]):
            if user_stress >= 7 or any(w in msg_lower for w in ["high", "very", "anxiety", "panic"]):
                return (
                    f"Take a deep breath with me, {user_name}. Your nervous system is currently in a heightened state. "
                    "Here is a rapid 2-minute physiological reset:\n\n"
                    "1. **Physiological Sigh**: Take two quick inhales through your nose, then one long, slow exhale through your mouth. Repeat 3 times.\n"
                    "2. **4-7-8 Breathing**: Use our interactive **Mental Wellness Hub** tab to follow the visual breathing pacer (Inhale 4s, Hold 7s, Exhale 8s).\n"
                    "3. **Physical Grounding**: Plant both feet flat on the floor, unclench your jaw, and let your shoulders drop 2 inches.\n\n"
                    f"Remember: high stress increases cortisol, which inhibits recovery. Take 10 minutes right now to rest—your body needs this."
                )
            else:
                return (
                    f"Mental wellness and physical recovery go hand-in-hand! To optimize your focus and lower stress:\n\n"
                    "- **Morning Sunlight**: 10 minutes of natural outdoor light sets your circadian rhythm and improves nightly sleep.\n"
                    "- **Active Mindfulness**: Even a brisk 15-minute walk without your phone helps clear mental clutter.\n"
                    "- Check out the **Mental Wellness Hub** tab above for our animated 4-7-8 breathwork guide and meditation timer!"
                )

        # 2. Medical Condition Queries (Hypertension, Knee Pain, Back Pain, Asthma, Diabetes)
        if any(w in msg_lower for w in ["knee", "joint", "squat", "pain", "hurt", "injury"]):
            return (
                f"Safety first, {user_name}! If you have knee or joint discomfort (or {user_med}):\n\n"
                "- **Avoid**: Deep squats below 90 degrees, heavy plyometrics (box jumps), and downhill running.\n"
                "- **Safe Alternatives**: Glute bridges on a mat, straight-leg raises, recumbent cycling, and swimming.\n"
                "- **Key Tip**: Strengthen your hips and hamstrings—they take substantial pressure off your patellar tendons. If pain is sharp, stop immediately!"
            )
            
        if any(w in msg_lower for w in ["back pain", "spine", "deadlift", "lumbar"]):
            return (
                "For lower back care:\n\n"
                "- **Avoid**: Spinal flexion under heavy load (e.g. rounded back deadlifts or standard sit-ups).\n"
                "- **Best Exercises**: The 'McGill Big 3'—Bird-Dog, Side Plank, and McGill Curl-up.\n"
                "- **Posture Tip**: Tight hip flexors and hamstrings pull on your lumbar spine. Gentle hamstring stretching and glute activation work wonders."
            )

        if any(w in msg_lower for w in ["diabetes", "sugar", "insulin", "glucose"]):
            return (
                f"Managing fitness with diabetes:\n\n"
                "- **Cardio + Light Resistance**: Muscle contractions pull glucose directly from your bloodstream without needing insulin spikes!\n"
                "- **Timing**: A 15-minute gentle walk immediately after meals blunts post-prandial blood sugar spikes significantly.\n"
                "- **Diet**: Focus on high soluble fiber (chia seeds, oats, leafy greens, lentils) and avoid liquid sugars and refined carbs."
            )

        if any(w in msg_lower for w in ["hypertension", "blood pressure", "bp"]):
            return (
                "For healthy blood pressure control:\n\n"
                "- **Avoid**: The Valsalva maneuver (holding your breath during heavy lifts) as it spikes intra-thoracic pressure.\n"
                "- **Recommended**: Rhythmic aerobic exercise (walking, cycling, swimming) at moderate intensity for 30 mins daily.\n"
                "- **Diet**: Follow the DASH diet principles—rich in potassium (bananas, spinach) and low in sodium (<2,000 mg/day)."
            )

        # 3. Diet, Nutrition & Protein Queries
        if any(w in msg_lower for w in ["diet", "food", "protein", "calorie", "eat", "meal", "macro", "snack", "fat loss"]):
            return (
                f"Here is your personalized nutritional advice aligned with your goal ({user_goal}):\n\n"
                f"- **Protein Goal**: Aim for roughly 1.4g - 1.8g of protein per kg of body weight to preserve lean muscle and support satiety.\n"
                "- **Whole Food Foundation**: Prioritize unprocessed foods—lentils, paneer/tofu, eggs, chicken/fish, whole grains, and greens.\n"
                "- **Hydration**: Drink 2.5 - 3.5 Liters of water daily. Often, feeling sluggish or falsely hungry is simply mild dehydration.\n"
                "Visit your **Nutrition & Diet** tab to view your exact daily calorie budget and meal-by-meal schedule!"
            )

        # 4. Workout / Exercise / Motivation Queries
        if any(w in msg_lower for w in ["workout", "exercise", "routine", "gym", "split", "sore", "tired", "motivat"]):
            return (
                f"Consistency beats intensity every time, {user_name}! For your goal ({user_goal}):\n\n"
                "- **Progressive Overload**: Focus on doing 1 more rep or lifting with cleaner form each week rather than overworking.\n"
                "- **Dealing with Soreness (DOMS)**: Light active recovery (a 20-min walk, gentle foam rolling, and hydration) clears metabolic waste much faster than lying stationary.\n"
                "- **Today's Action**: Check your **Workout Planner** tab to see today's planned session and check off your completed sets!"
            )

        # 5. General greeting & default assistant response
        return (
            f"Hello {user_name}! I'm your **WellNex Guide**. I monitor your fitness plan, nutrition targets, and mental wellness.\n\n"
            f"Here is your snapshot:\n"
            f"• Goal: **{user_goal}** | Condition: **{user_med}**\n"
            f"• Stress Level: **{user_stress}/10**\n\n"
            "How can I support you right now? You can ask me about:\n"
            "- Workout form modifications or safe exercises\n"
            "- Healthy meal swaps and protein recommendations\n"
            "- Quick stress relief, breathing exercises, or sleep tips!"
        )
