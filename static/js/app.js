/**
 * WELLNEX - FRONTEND APPLICATION SCRIPT
 * Full-stack client handling UI tabs, REST API integration, Chart.js analytics,
 * 4-7-8 breathing state machine, audio chime synthesis, and Wellness Chatbot.
 */

// Application State
let activeUser = null;
let activePlan = null;
let currentActiveDayIndex = 0;
let weightChart = null;
let moodStressChart = null;
let audioCtx = null;

// Breathing Pacer State
let breathInterval = null;
let breathState = "idle"; // 'inhale', 'hold', 'exhale'
let breathTimeRemaining = 0;
let breathCycles = 0;

// Meditation Timer State
let meditationInterval = null;
let meditationTotalSeconds = 600;
let meditationSecondsLeft = 600;
let isMeditationRunning = false;

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupAssessmentForm();
  setupBreathingPacer();
  setupMeditationTimer();
  setupPsychologicalAssessment();
  setupProgressTracking();
  setupFeedbackLoop();
  setupChatbot();
  loadInitialData();
});

// ==========================================================================
// 1. NAVIGATION & TAB SWITCHING
// ==========================================================================
function setupNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn");
  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      switchTab(targetTab);
    });
  });

  const openAssessmentBtn = document.getElementById("openAssessmentBtn");
  if (openAssessmentBtn) {
    openAssessmentBtn.addEventListener("click", () => switchTab("assessment-tab"));
  }
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(btn => {
    if (btn.getAttribute("data-tab") === tabId) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  const targetPane = document.getElementById(tabId);
  if (targetPane) {
    targetPane.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Refresh charts if opening progress tab
    if (tabId === "progress-tab" && activeUser) {
      fetchProgressHistory(activeUser.id);
    }
  }
}

// ==========================================================================
// 2. ASSESSMENT FORM & DEMO PROFILES
// ==========================================================================
function setupAssessmentForm() {
  const stressSlider = document.getElementById("inputStress");
  const stressBadge = document.getElementById("stressValueBadge");
  const stressEmoji = document.getElementById("stressReactionIcon");

  if (stressSlider) {
    stressSlider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value);
      let desc = "Low / Calm";
      let emoji = "😊";
      let badgeClass = "badge-emerald";

      if (val >= 8) {
        desc = "Severe Burnout";
        emoji = "😫";
        badgeClass = "badge-warning";
      } else if (val >= 6) {
        desc = "Elevated Stress";
        emoji = "😟";
        badgeClass = "badge-warning";
      } else if (val >= 4) {
        desc = "Moderate";
        emoji = "😐";
        badgeClass = "badge-primary";
      }

      stressBadge.className = `badge ${badgeClass}`;
      stressBadge.textContent = `${val} / 10 (${desc})`;
      stressEmoji.textContent = emoji;
    });
  }

  // Demo Profile 1: High Stress & Joint Pain
  document.getElementById("loadDemoSedentary")?.addEventListener("click", () => {
    document.getElementById("inputName").value = "Priya Sharma";
    document.getElementById("inputAge").value = "34";
    document.getElementById("inputGender").value = "Female";
    document.getElementById("inputHeight").value = "162";
    document.getElementById("inputWeight").value = "76";
    document.getElementById("inputGoal").value = "Weight Loss";
    document.getElementById("inputActivity").value = "Sedentary";
    document.getElementById("inputSleep").value = "5.5";
    document.getElementById("inputDiet").value = "Vegetarian";
    document.getElementById("inputMedical").value = "Knee/Joint Pain";
    stressSlider.value = 8;
    stressSlider.dispatchEvent(new Event("input"));
    showToast("Loaded Profile: Priya (Sedentary, High Stress)");
  });

  // Demo Profile 2: Athletic Muscle Builder
  document.getElementById("loadDemoAthlete")?.addEventListener("click", () => {
    document.getElementById("inputName").value = "Vikram Singh";
    document.getElementById("inputAge").value = "23";
    document.getElementById("inputGender").value = "Male";
    document.getElementById("inputHeight").value = "180";
    document.getElementById("inputWeight").value = "74";
    document.getElementById("inputGoal").value = "Muscle Gain";
    document.getElementById("inputActivity").value = "Moderately Active";
    document.getElementById("inputSleep").value = "7.5";
    document.getElementById("inputDiet").value = "Non-Vegetarian";
    document.getElementById("inputMedical").value = "None";
    stressSlider.value = 3;
    stressSlider.dispatchEvent(new Event("input"));
    showToast("Loaded Profile: Vikram (Athletic Muscle Builder)");
  });

  // Jump to Psychological Assessment shortcut
  document.getElementById("jumpToPsyAssessmentBtn")?.addEventListener("click", () => {
    switchTab("wellness-tab");
    setTimeout(() => {
      document.getElementById("psyAssessmentSection")?.scrollIntoView({ behavior: "smooth" });
    }, 200);
  });

  // Form Submit handler
  const form = document.getElementById("assessmentForm");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById("submitAssessmentBtn");
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing Biometrics & ML Engine...`;

      const payload = {
        name: document.getElementById("inputName").value,
        age: parseInt(document.getElementById("inputAge").value),
        gender: document.getElementById("inputGender").value,
        height_cm: parseFloat(document.getElementById("inputHeight").value),
        weight_kg: parseFloat(document.getElementById("inputWeight").value),
        goal: document.getElementById("inputGoal").value,
        activity_level: document.getElementById("inputActivity").value,
        sleep_hours: parseFloat(document.getElementById("inputSleep").value),
        dietary_preference: document.getElementById("inputDiet").value,
        medical_condition: document.getElementById("inputMedical").value,
        stress_level: parseInt(document.getElementById("inputStress").value)
      };

      try {
        const resp = await fetch("/api/user/assess", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const res = await resp.json();

        if (res.status === "success") {
          activeUser = { ...res.user, id: res.user_id };
          activePlan = res.recommendations;
          localStorage.setItem("wellnex_user_id", res.user_id);

          renderAppDashboard(activeUser, activePlan);
          showToast(`Welcome ${activeUser.name}! Your personalized plan has been created!`);
          switchTab("dashboard-tab");
        } else {
          showToast(`Error: ${res.message}`, "error");
        }
      } catch (err) {
        showToast(`Connection error: ${err.message}`, "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Generate My Personalized Plan`;
      }
    });
  }
}

// ==========================================================================
// 3. INITIAL LOAD & DATA POPULATION
// ==========================================================================
async function loadInitialData() {
  const savedUserId = localStorage.getItem("wellnex_user_id") || localStorage.getItem("fitmind_user_id");
  if (savedUserId) {
    try {
      const resp = await fetch(`/api/user/${savedUserId}/profile`);
      const data = await resp.json();
      if (data.status === "success" && data.user && data.recommendations) {
        activeUser = data.user;
        activePlan = data.recommendations;
        renderAppDashboard(activeUser, activePlan);
        return;
      }
    } catch (e) {
      console.log("Could not load cached user, triggering default assessment demo.");
    }
  }

  // Auto-run standard initial assessment so the app is immediately populated
  const defaultPayload = {
    name: "Rahul Sharma",
    age: 26,
    gender: "Male",
    height_cm: 175,
    weight_kg: 78,
    goal: "Weight Loss",
    activity_level: "Lightly Active",
    sleep_hours: 6.5,
    dietary_preference: "Vegetarian",
    medical_condition: "None",
    stress_level: 6
  };

  try {
    const resp = await fetch("/api/user/assess", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(defaultPayload)
    });
    const res = await resp.json();
    if (res.status === "success") {
      activeUser = { ...res.user, id: res.user_id };
      activePlan = res.recommendations;
      localStorage.setItem("wellnex_user_id", res.user_id);
      renderAppDashboard(activeUser, activePlan);
      fetchScreeningHistory(res.user_id);
    }
  } catch (err) {
    console.error("Initial assess error:", err);
  }
}

// ==========================================================================
// 4. RENDER DASHBOARD & SUB-VIEWS
// ==========================================================================
function renderAppDashboard(user, recs) {
  if (!user || !recs) return;

  const biometrics = recs.biometrics;
  const ml = recs.ml_insights;
  const workout = recs.workout_plan;
  const diet = recs.diet_plan;
  const mental = recs.mental_wellness_plan;

  // Header user label
  const headerName = document.getElementById("headerUserName");
  if (headerName) headerName.textContent = user.name || "Profile";

  // Archetype Banner
  document.getElementById("clusterNumber").textContent = `#${ml.cluster_id + 1}`;
  document.getElementById("archetypeName").textContent = ml.archetype.name;
  document.getElementById("archetypeDesc").textContent = ml.archetype.summary || "Tailored physiological & mental wellness regimen.";

  const healthAlertBox = document.getElementById("healthAlertBox");
  const healthAlertText = document.getElementById("healthAlertText");
  if (ml.health_alert) {
    healthAlertBox.style.display = "inline-flex";
    healthAlertText.textContent = ml.health_alert;
  } else {
    healthAlertBox.style.display = "none";
  }

  // Stat Cards
  document.getElementById("bmiValue").textContent = biometrics.bmi;
  const bmiBadge = document.getElementById("bmiCategoryBadge");
  bmiBadge.textContent = biometrics.bmi_category;
  if (biometrics.bmi < 18.5) {
    bmiBadge.className = "badge badge-cyan";
  } else if (biometrics.bmi < 25.0) {
    bmiBadge.className = "badge badge-emerald";
  } else if (biometrics.bmi < 30.0) {
    bmiBadge.className = "badge badge-warning";
  } else {
    bmiBadge.className = "badge badge-danger";
  }
  bmiBadge.style.backgroundColor = "";
  bmiBadge.style.color = "";

  document.getElementById("targetCalValue").innerHTML = `${biometrics.target_calories} <small>kcal</small>`;
  document.getElementById("tdeeDesc").textContent = `Estimated TDEE: ${biometrics.tdee} kcal (${user.goal})`;

  document.getElementById("stressStateVal").textContent = `${mental.stress_state.split(' ')[0]} (${mental.stress_level}/10)`;
  document.getElementById("stressActionText").textContent = `${mental.daily_breathing_sessions} Breathwork session(s) recommended`;

  // Workout Overview Card
  document.getElementById("todayIntensityBadge").textContent = `${workout.recommended_intensity} Intensity`;
  document.getElementById("todayFocusTitle").textContent = workout.schedule[0].focus;
  document.getElementById("todayWarmupSnippet").textContent = `Warm-up: ${workout.schedule[0].warmup}`;

  const exList = document.getElementById("todayExercisesSnippet");
  exList.innerHTML = "";
  workout.schedule[0].exercises.slice(0, 3).forEach(ex => {
    const item = document.createElement("div");
    item.className = "quick-ex-item";
    item.innerHTML = `<span><i class="fa-solid fa-angle-right"></i> ${ex.name}</span> <small>${ex.sets} × ${ex.reps}</small>`;
    exList.appendChild(item);
  });

  // Nutrition Overview Card
  document.getElementById("dietStrategyBadge").textContent = diet.strategy_title;
  document.getElementById("previewProtein").textContent = `${biometrics.macros.protein_g}g`;
  document.getElementById("previewCarbs").textContent = `${biometrics.macros.carbs_g}g`;
  document.getElementById("previewFats").textContent = `${biometrics.macros.fats_g}g`;

  const totalMacros = biometrics.macros.protein_g + biometrics.macros.carbs_g + biometrics.macros.fats_g;
  document.getElementById("barProtein").style.width = `${Math.round((biometrics.macros.protein_g / totalMacros) * 100)}%`;
  document.getElementById("barCarbs").style.width = `${Math.round((biometrics.macros.carbs_g / totalMacros) * 100)}%`;
  document.getElementById("barFats").style.width = `${Math.round((biometrics.macros.fats_g / totalMacros) * 100)}%`;

  if (mental.wellness_tips && mental.wellness_tips.length > 0) {
    document.getElementById("dailyMindTipText").textContent = mental.wellness_tips[0].desc;
  }

  // Render Full Workout Section
  renderWorkoutSection(workout);

  // Render Full Nutrition Section
  renderNutritionSection(diet, biometrics);

  // Render Mental Wellness Section
  renderWellnessSection(mental);

  // Render User Profile Section
  renderProfileSection(user, recs);
}

// ==========================================================================
// 5. WORKOUT TAB RENDERER
// ==========================================================================
function renderWorkoutSection(workout) {
  document.getElementById("workoutSplitHeader").textContent = `Split: ${workout.split_name} • Intensity: ${workout.recommended_intensity}`;
  document.getElementById("totalWorkoutsCount").textContent = workout.schedule.length;

  const tabsNav = document.getElementById("dayTabsNav");
  tabsNav.innerHTML = "";

  workout.schedule.forEach((dayPlan, idx) => {
    const btn = document.createElement("button");
    btn.className = `day-tab-btn ${idx === currentActiveDayIndex ? 'active' : ''}`;
    btn.innerHTML = `<i class="fa-solid fa-calendar-day"></i> ${dayPlan.day.split(' ')[0]} ${dayPlan.day.split(' ')[1] || ''}`;
    btn.addEventListener("click", () => {
      currentActiveDayIndex = idx;
      document.querySelectorAll(".day-tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderDayWorkout(workout.schedule[idx]);
    });
    tabsNav.appendChild(btn);
  });

  renderDayWorkout(workout.schedule[currentActiveDayIndex]);
}

function renderDayWorkout(dayPlan) {
  const container = document.getElementById("activeDayContent");
  container.innerHTML = `
    <div class="day-overview-bar">
      <div>
        <h3><i class="fa-solid fa-dumbbell text-primary"></i> ${dayPlan.day}: ${dayPlan.focus}</h3>
        <p class="text-muted" style="font-size: 0.84rem; margin-top: 0.2rem;">${dayPlan.warmup} | ${dayPlan.cooldown}</p>
      </div>
      <span class="badge badge-primary">${dayPlan.intensity_badge}</span>
    </div>
    <div class="exercise-cards-grid" id="dayCardsGrid"></div>
  `;

  const cardsGrid = document.getElementById("dayCardsGrid");
  dayPlan.exercises.forEach((ex, i) => {
    const card = document.createElement("div");
    card.className = "exercise-card";
    card.innerHTML = `
      <div class="ex-header">
        <div class="ex-title">${ex.name}</div>
        <span class="badge badge-cyan"><i class="fa-solid fa-stopwatch"></i> ${ex.rest} rest</span>
      </div>
      <div class="ex-meta">
        <span><i class="fa-solid fa-layer-group"></i> ${ex.sets}</span>
        <span><i class="fa-solid fa-repeat"></i> ${ex.reps}</span>
      </div>
      <div class="ex-tip">
        <strong>Form Cue:</strong> ${ex.tip}
      </div>
      <button class="ex-check-btn" onclick="toggleExerciseComplete(this)">
        <i class="fa-regular fa-square"></i> Mark Exercise Complete
      </button>
    `;
    cardsGrid.appendChild(card);
  });
}

function toggleExerciseComplete(btn) {
  const card = btn.closest(".exercise-card");
  const isChecked = btn.classList.contains("checked");

  if (!isChecked) {
    btn.classList.add("checked");
    card.classList.add("completed");
    btn.innerHTML = `<i class="fa-solid fa-square-check"></i> Completed`;
    playChime(600, 0.1);
    updateCompletedWorkoutsCount();
  } else {
    btn.classList.remove("checked");
    card.classList.remove("completed");
    btn.innerHTML = `<i class="fa-regular fa-square"></i> Mark Exercise Complete`;
    updateCompletedWorkoutsCount();
  }
}

function updateCompletedWorkoutsCount() {
  const completedCount = document.querySelectorAll(".exercise-card.completed").length;
  document.getElementById("completedWorkoutsCount").textContent = completedCount;
}

// ==========================================================================
// 6. NUTRITION TAB RENDERER
// ==========================================================================
function renderNutritionSection(diet, biometrics) {
  document.getElementById("dietTotalCalories").textContent = diet.target_calories;
  document.getElementById("macroProteinVal").textContent = `${biometrics.macros.protein_g} g`;
  document.getElementById("macroCarbsVal").textContent = `${biometrics.macros.carbs_g} g`;
  document.getElementById("macroFatsVal").textContent = `${biometrics.macros.fats_g} g`;
  document.getElementById("macroWaterVal").textContent = `${diet.water_target_liters} Liters`;

  // Diet medical conditions note
  const dietAlert = document.getElementById("dietConditionNotes");
  const dietAlertText = document.getElementById("dietConditionText");
  if (diet.special_diet_guidance && diet.special_diet_guidance.length > 0) {
    dietAlert.style.display = "flex";
    dietAlertText.textContent = diet.special_diet_guidance.join(" ");
  } else {
    dietAlert.style.display = "none";
  }

  // Render 4 meals
  const container = document.getElementById("mealsContainer");
  container.innerHTML = "";

  const slots = [
    { key: "breakfast", label: "Breakfast (Morning Energizer)", icon: "fa-mug-saucer" },
    { key: "lunch", label: "Lunch (Sustained Power)", icon: "fa-bowl-rice" },
    { key: "evening_snack", label: "Snack (Pre/Post Fuel)", icon: "fa-apple-whole" },
    { key: "dinner", label: "Dinner (Restorative & Light)", icon: "fa-plate-wheat" }
  ];

  slots.forEach(slot => {
    const meal = diet.meals[slot.key];
    if (!meal) return;

    const card = document.createElement("div");
    card.className = "meal-card";
    card.innerHTML = `
      <div class="meal-slot-badge"><i class="fa-solid ${slot.icon}"></i> ${slot.label}</div>
      <div class="meal-name">${meal.name}</div>
      <div class="meal-desc">${meal.desc}</div>
      <div class="meal-stats">
        <span><i class="fa-solid fa-fire text-amber"></i> ${meal.calories} kcal</span>
        <span><i class="fa-solid fa-drumstick-bite text-emerald"></i> P: ${meal.protein}</span>
        <span><i class="fa-solid fa-wheat-awn text-blue"></i> C: ${meal.carbs}</span>
        <span>F: ${meal.fats}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

// Hydration buttons on dashboard
let currentWaterLogged = 1.5;
document.getElementById("addWaterBtn")?.addEventListener("click", () => {
  currentWaterLogged = Math.min(5.0, currentWaterLogged + 0.25);
  document.getElementById("waterIntakeVal").innerHTML = `${currentWaterLogged.toFixed(2)} / 3.0 <small>Liters</small>`;
  playChime(750, 0.08);
  showToast(`Logged 250ml water (Total: ${currentWaterLogged.toFixed(2)}L)`);
});
document.getElementById("resetWaterBtn")?.addEventListener("click", () => {
  currentWaterLogged = 0;
  document.getElementById("waterIntakeVal").innerHTML = `0.0 / 3.0 <small>Liters</small>`;
  showToast("Hydration tracker reset for today.");
});

// ==========================================================================
// 7. MENTAL WELLNESS: 4-7-8 BREATHING PACER & MEDITATION TIMER
// ==========================================================================
function setupBreathingPacer() {
  const startBtn = document.getElementById("startBreathBtn");
  const stopBtn = document.getElementById("stopBreathBtn");
  const circle = document.getElementById("breathingCircle");
  const actionText = document.getElementById("breathActionText");
  const timerNum = document.getElementById("breathTimerNum");
  const cyclesLabel = document.getElementById("breathCyclesDone");

  function setPacerState(state, seconds, labelText) {
    breathState = state;
    breathTimeRemaining = seconds;
    actionText.textContent = labelText;
    timerNum.textContent = seconds;

    circle.className = `breathing-circle ${state}`;
  }

  function tickBreathing() {
    breathTimeRemaining--;
    timerNum.textContent = breathTimeRemaining > 0 ? breathTimeRemaining : 1;

    if (breathTimeRemaining <= 0) {
      if (breathState === "inhale") {
        playChime(520, 0.2); // Calm chime
        setPacerState("hold", 7, "Hold");
      } else if (breathState === "hold") {
        playChime(440, 0.25); // Lower release chime
        setPacerState("exhale", 8, "Exhale Slowly");
      } else if (breathState === "exhale") {
        breathCycles++;
        cyclesLabel.textContent = breathCycles;
        playChime(660, 0.2); // Fresh inhale chime
        setPacerState("inhale", 4, "Inhale Deeply");
      }
    }
  }

  startBtn.addEventListener("click", () => {
    initAudioContext();
    startBtn.disabled = true;
    stopBtn.disabled = false;

    breathCycles = 0;
    cyclesLabel.textContent = "0";
    playChime(660, 0.2);
    setPacerState("inhale", 4, "Inhale Deeply");

    clearInterval(breathInterval);
    breathInterval = setInterval(tickBreathing, 1000);
  });

  stopBtn.addEventListener("click", () => {
    clearInterval(breathInterval);
    startBtn.disabled = false;
    stopBtn.disabled = true;
    circle.className = "breathing-circle";
    actionText.textContent = "Paused";
    timerNum.textContent = "--";
  });
}

function setupMeditationTimer() {
  const timeDisplay = document.getElementById("meditationTimeDisplay");
  const startBtn = document.getElementById("startMeditationBtn");
  const resetBtn = document.getElementById("resetMeditationBtn");
  const presetBtns = document.querySelectorAll(".preset-time-btn");

  presetBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      presetBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const seconds = parseInt(btn.getAttribute("data-time"));
      meditationTotalSeconds = seconds;
      meditationSecondsLeft = seconds;
      updateMeditationDisplay();
      if (isMeditationRunning) {
        clearInterval(meditationInterval);
        isMeditationRunning = false;
        startBtn.innerHTML = `<i class="fa-solid fa-play"></i> Begin Meditation`;
      }
    });
  });

  function updateMeditationDisplay() {
    const mins = Math.floor(meditationSecondsLeft / 60);
    const secs = meditationSecondsLeft % 60;
    timeDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  startBtn.addEventListener("click", () => {
    initAudioContext();
    if (!isMeditationRunning) {
      isMeditationRunning = true;
      startBtn.innerHTML = `<i class="fa-solid fa-pause"></i> Pause Meditation`;
      startBtn.className = "btn btn-outline";
      playChime(432, 0.5); // 432 Hz healing tone

      meditationInterval = setInterval(() => {
        meditationSecondsLeft--;
        updateMeditationDisplay();

        if (meditationSecondsLeft <= 0) {
          clearInterval(meditationInterval);
          isMeditationRunning = false;
          startBtn.innerHTML = `<i class="fa-solid fa-play"></i> Begin Meditation`;
          startBtn.className = "btn btn-success";
          playChime(528, 1.0);
          showToast("Meditation session complete. Namaste 🙏");
        }
      }, 1000);
    } else {
      clearInterval(meditationInterval);
      isMeditationRunning = false;
      startBtn.innerHTML = `<i class="fa-solid fa-play"></i> Resume Meditation`;
      startBtn.className = "btn btn-success";
    }
  });

  resetBtn.addEventListener("click", () => {
    clearInterval(meditationInterval);
    isMeditationRunning = false;
    meditationSecondsLeft = meditationTotalSeconds;
    updateMeditationDisplay();
    startBtn.innerHTML = `<i class="fa-solid fa-play"></i> Begin Meditation`;
    startBtn.className = "btn btn-success";
  });

  updateMeditationDisplay();
}

function renderWellnessSection(mental) {
  const container = document.getElementById("wellnessTipsContainer");
  container.innerHTML = "";

  mental.wellness_tips.forEach(tip => {
    const card = document.createElement("div");
    card.className = "wellness-tip-card";
    card.innerHTML = `
      <strong><i class="fa-solid fa-sparkles text-purple"></i> ${tip.title}</strong>
      <p>${tip.desc}</p>
    `;
    container.appendChild(card);
  });

  if (activeUser && activeUser.id) {
    fetchScreeningHistory(activeUser.id);
  }
}

// ==========================================================================
// 8. STANDARDIZED PSYCHOLOGICAL ASSESSMENT (PSS-4 & GAD-7)
// ==========================================================================
const PSY_SCALES = {
  "PSS-4": {
    name: "PSS-4 Perceived Stress Scale",
    description: "Cohen's Perceived Stress Scale (PSS-4) measures the degree to which situations in your life are appraised as unpredictable, uncontrollable, and overloading over the last month.",
    maxScore: 16,
    timeEstimate: "~1-2 Minutes",
    options: [
      { val: 0, label: "0 - Never" },
      { val: 1, label: "1 - Almost Never" },
      { val: 2, label: "2 - Sometimes" },
      { val: 3, label: "3 - Fairly Often" },
      { val: 4, label: "4 - Very Often" }
    ],
    questions: [
      { id: "q1", text: "In the last month, how often have you felt that you were unable to control the important things in your life?", reversed: false },
      { id: "q2", text: "In the last month, how often have you felt confident about your ability to handle your personal problems?", reversed: true },
      { id: "q3", text: "In the last month, how often have you felt that things were going your way?", reversed: true },
      { id: "q4", text: "In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?", reversed: false }
    ]
  },
  "GAD-7": {
    name: "GAD-7 Generalized Anxiety Screener",
    description: "Validated clinical instrument measuring generalized anxiety symptoms over the past 2 weeks (Spitzer et al., 2006).",
    maxScore: 21,
    timeEstimate: "~2-3 Minutes",
    options: [
      { val: 0, label: "0 - Not at all" },
      { val: 1, label: "1 - Several days" },
      { val: 2, label: "2 - Over half days" },
      { val: 3, label: "3 - Nearly every day" }
    ],
    questions: [
      { id: "q1", text: "Feeling nervous, anxious, or on edge?", reversed: false },
      { id: "q2", text: "Not being able to stop or control worrying?", reversed: false },
      { id: "q3", text: "Worrying too much about different things?", reversed: false },
      { id: "q4", text: "Trouble relaxing?", reversed: false },
      { id: "q5", text: "Being so restless that it is hard to sit still?", reversed: false },
      { id: "q6", text: "Becoming easily annoyed or irritable?", reversed: false },
      { id: "q7", text: "Feeling afraid, as if something awful might happen?", reversed: false }
    ]
  }
};

let currentPsyScale = "PSS-4";
let psyAnswers = {};
let latestScreeningData = null;

function setupPsychologicalAssessment() {
  const container = document.getElementById("psyQuestionsContainer");
  const form = document.getElementById("psyScreeningForm");
  const pssBtn = document.getElementById("btnScalePSS");
  const gadBtn = document.getElementById("btnScaleGAD");
  const resetBtn = document.getElementById("btnResetScreening");
  const syncBtn = document.getElementById("btnSyncStressProfile");

  if (!container || !form) return;

  // Scale switcher
  pssBtn?.addEventListener("click", () => switchPsyScale("PSS-4"));
  gadBtn?.addEventListener("click", () => switchPsyScale("GAD-7"));

  // Reset button
  resetBtn?.addEventListener("click", () => {
    psyAnswers = {};
    renderPsyQuestions(currentPsyScale);
    const resultCard = document.getElementById("psyResultCard");
    if (resultCard) resultCard.style.display = "none";
    updatePsyProgress();
  });

  // Sync stress with profile
  syncBtn?.addEventListener("click", handleSyncStressWithProfile);

  // Form submission
  const submitBtn = document.getElementById("btnSubmitScreening");

  async function submitAssessment(e) {
    if (e) e.preventDefault();
    const scale = PSY_SCALES[currentPsyScale];
    const totalQ = scale.questions.length;
    const answeredCount = Object.keys(psyAnswers).length;

    if (answeredCount < totalQ) {
      showToast(`Please answer all ${totalQ} questions to calculate clinical score.`, "error");
      return;
    }

    try {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing...`;
      }

      const payload = {
        scale_type: currentPsyScale,
        responses: psyAnswers,
        user_id: activeUser ? activeUser.id : null
      };

      const resp = await fetch("/api/mental/screening", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const res = await resp.json();
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-calculator"></i> Calculate Clinical Score`;
      }

      if (res.status === "success") {
        latestScreeningData = res;
        renderPsyResult(res);
        try {
          if (typeof initAudioContext === "function") initAudioContext();
          if (typeof playChime === "function") playChime(580, 0.25);
        } catch (audioErr) {}
        showToast(`${currentPsyScale} Score: ${res.score}/${res.max_score} (${res.severity_level})`);

        if (activeUser && activeUser.id) {
          fetchScreeningHistory(activeUser.id);
        }
      } else {
        showToast(res.message || "Screening calculation failed", "error");
      }
    } catch (err) {
      console.error("Screening submit error:", err);
      showToast(`Failed to evaluate: ${err.message}`, "error");
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-calculator"></i> Calculate Clinical Score`;
      }
    }
  }

  form.addEventListener("submit", submitAssessment);
  submitBtn?.addEventListener("click", submitAssessment);

  // Initial render of questions
  renderPsyQuestions(currentPsyScale);
}

function switchPsyScale(scaleKey) {
  currentPsyScale = scaleKey;
  psyAnswers = {};

  const pssBtn = document.getElementById("btnScalePSS");
  const gadBtn = document.getElementById("btnScaleGAD");
  if (scaleKey === "PSS-4") {
    pssBtn?.classList.add("active");
    gadBtn?.classList.remove("active");
  } else {
    gadBtn?.classList.add("active");
    pssBtn?.classList.remove("active");
  }

  const resultCard = document.getElementById("psyResultCard");
  if (resultCard) resultCard.style.display = "none";
  renderPsyQuestions(scaleKey);
}

function renderPsyQuestions(scaleKey) {
  const scale = PSY_SCALES[scaleKey];
  const container = document.getElementById("psyQuestionsContainer");
  const descEl = document.getElementById("psyScaleDescription");
  const countBadge = document.getElementById("psyQuestionCountBadge");

  if (!container || !scale) return;

  if (descEl) descEl.textContent = scale.description;
  if (countBadge) countBadge.innerHTML = `<i class="fa-solid fa-list-check"></i> ${scale.questions.length} Questions`;

  container.innerHTML = "";

  scale.questions.forEach((q, idx) => {
    const card = document.createElement("div");
    card.className = `psy-q-card ${psyAnswers[q.id] !== undefined ? "answered" : ""}`;
    card.id = `card-${q.id}`;

    let optionsHtml = "";
    scale.options.forEach(opt => {
      const isChecked = psyAnswers[q.id] === opt.val;
      optionsHtml += `
        <label class="psy-opt-chip ${isChecked ? "active" : ""}">
          <input type="radio" name="opt-${q.id}" value="${opt.val}" ${isChecked ? "checked" : ""}>
          <span>${opt.label}</span>
        </label>
      `;
    });

    card.innerHTML = `
      <div class="psy-q-header">
        <div class="psy-q-num">${idx + 1}</div>
        <div class="psy-q-text">${q.text}</div>
      </div>
      <div class="psy-options-grid">
        ${optionsHtml}
      </div>
    `;

    // Attach click listeners to chips
    card.querySelectorAll('input[type="radio"]').forEach(radio => {
      radio.addEventListener("change", (e) => {
        psyAnswers[q.id] = parseInt(e.target.value);
        card.classList.add("answered");
        card.querySelectorAll(".psy-opt-chip").forEach(chip => chip.classList.remove("active"));
        radio.closest(".psy-opt-chip").classList.add("active");
        updatePsyProgress();
      });
    });

    container.appendChild(card);
  });

  updatePsyProgress();
}

function updatePsyProgress() {
  const scale = PSY_SCALES[currentPsyScale];
  if (!scale) return;
  const total = scale.questions.length;
  const count = Object.keys(psyAnswers).length;
  const progressEl = document.getElementById("psyAnsweredProgress");
  if (progressEl) {
    if (count === total) {
      progressEl.innerHTML = `<i class="fa-solid fa-check text-success"></i> All ${total} Questions Answered`;
    } else {
      progressEl.textContent = `Answered: ${count} / ${total}`;
    }
  }
}

function renderPsyResult(data) {
  const card = document.getElementById("psyResultCard");
  if (!card) return;

  document.getElementById("psyScoreNum").textContent = data.score;
  document.getElementById("psyScoreMax").textContent = `/ ${data.max_score}`;
  document.getElementById("psyScaleNameLabel").textContent = `${data.scale_type} Clinical Index`;

  const badge = document.getElementById("psySeverityBadge");
  const gauge = document.getElementById("psyGaugeCircle");
  badge.textContent = data.severity_level;

  badge.className = "psy-severity-badge";
  let borderColor = "#0d9488";

  const sevLower = data.severity_level.toLowerCase();
  if (sevLower.includes("low") || sevLower.includes("minimal")) {
    badge.classList.add("severity-minimal");
    borderColor = "#16a34a";
  } else if (sevLower.includes("mild")) {
    badge.classList.add("severity-mild");
    borderColor = "#eab308";
  } else if (sevLower.includes("moderate")) {
    badge.classList.add("severity-moderate");
    borderColor = "#f97316";
  } else {
    badge.classList.add("severity-severe");
    borderColor = "#e11d48";
  }

  if (gauge) {
    gauge.style.borderColor = borderColor;
  }

  document.getElementById("psyFeedbackText").textContent = data.feedback;

  const tipsList = document.getElementById("psyTipsList");
  tipsList.innerHTML = "";
  (data.recommended_actions || []).forEach(tip => {
    const li = document.createElement("li");
    li.textContent = tip;
    tipsList.appendChild(li);
  });

  const syncBtn = document.getElementById("btnSyncStressProfile");
  if (syncBtn) {
    syncBtn.disabled = false;
    syncBtn.innerHTML = `<i class="fa-solid fa-bolt"></i> Sync with your profile`;
  }

  card.style.display = "block";
  setTimeout(() => {
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, 100);
}

async function handleSyncStressWithProfile() {
  if (!latestScreeningData) {
    showToast("Please calculate a clinical screening score first.", "warning");
    return;
  }
  if (!activeUser || !activeUser.id) {
    showToast("Please complete your baseline assessment first to sync profile.", "warning");
    return;
  }

  const score = latestScreeningData.score;
  const maxScore = latestScreeningData.max_score;
  // Map normalized score (0 to max) to 1 to 10
  let mappedStress = Math.round((score / maxScore) * 9) + 1;
  mappedStress = Math.max(1, Math.min(10, mappedStress));

  try {
    const syncBtn = document.getElementById("btnSyncStressProfile");
    syncBtn.disabled = true;
    syncBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Syncing...`;

    const resp = await fetch("/api/mental/sync-stress", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: activeUser.id,
        stress_level: mappedStress
      })
    });

    const res = await resp.json();
    syncBtn.disabled = false;
    syncBtn.innerHTML = `<i class="fa-solid fa-check"></i> Synchronized!`;

    if (res.status === "success") {
      activeUser.stress_level = mappedStress;
      activePlan = res.recommendations;

      // Re-render dashboard & tabs with updated recommendations
      renderAppDashboard(activeUser, activePlan);

      // Also update slider on assessment form
      const stressSlider = document.getElementById("inputStress");
      if (stressSlider) {
        stressSlider.value = mappedStress;
        stressSlider.dispatchEvent(new Event("input"));
      }

      playChime(660, 0.25);
      showToast(`Profile stress updated to ${mappedStress}/10! Plan dynamically recalibrated.`);
    } else {
      showToast(res.message || "Failed to sync stress level.", "error");
    }
  } catch (err) {
    console.error("Sync stress error:", err);
    showToast(`Sync failed: ${err.message}`, "error");
    const syncBtn = document.getElementById("btnSyncStressProfile");
    if (syncBtn) {
      syncBtn.disabled = false;
      syncBtn.innerHTML = `<i class="fa-solid fa-bolt"></i> Sync with your profile`;
    }
  }
}

async function fetchScreeningHistory(userId) {
  if (!userId) return;
  try {
    const resp = await fetch(`/api/mental/screening/${userId}`);
    const data = await resp.json();
    if (data.status === "success" && data.history && data.history.length > 0) {
      const section = document.getElementById("psyHistorySection");
      const list = document.getElementById("psyHistoryList");
      if (!section || !list) return;

      list.innerHTML = "";
      data.history.forEach(item => {
        const pill = document.createElement("span");
        pill.className = "psy-history-pill";
        const dateStr = item.created_at ? item.created_at.substring(0, 10) : "Recent";
        pill.innerHTML = `<i class="fa-solid fa-calendar text-teal"></i> ${dateStr} - <strong>${item.scale_type}</strong>: ${item.score}/${item.max_score} (${item.severity_level})`;
        list.appendChild(pill);
      });
      section.style.display = "block";
    }
  } catch (e) {
    console.error("Failed to fetch screening history:", e);
  }
}

// ==========================================================================
// 7. USER PROFILE SECTION RENDERER
// ==========================================================================
function renderProfileSection(user, recs) {
  if (!user || !recs) return;

  const biometrics = recs.biometrics;
  const ml = recs.ml_insights || {};
  const workout = recs.workout_plan || {};
  const diet = recs.diet_plan || {};
  const mental = recs.mental_wellness_plan || {};

  // User Initials & Full Name
  const initials = user.name
    ? user.name.trim().split(/\s+/).map(w => w[0]).join("").toUpperCase().slice(0, 2)
    : "WN";
  const initialsEl = document.getElementById("profileInitials");
  if (initialsEl) initialsEl.textContent = initials;

  const nameEl = document.getElementById("profileFullName");
  if (nameEl) nameEl.textContent = user.name;

  const cohortBadge = document.getElementById("profileCohortBadge");
  if (cohortBadge) {
    const clusterNum = (ml.cluster_id !== undefined ? ml.cluster_id : 0) + 1;
    cohortBadge.innerHTML = `<i class="fa-solid fa-id-badge"></i> Cohort #${clusterNum}`;
  }

  const heroSub = document.getElementById("profileHeroSubtitle");
  if (heroSub) {
    const timeStr = user.created_at ? new Date(user.created_at).toLocaleDateString() : "Active Member";
    heroSub.textContent = `Personalized Health & Wellness Plan • ${timeStr}`;
  }

  // Quick Hero Stat Pills
  const goalEl = document.getElementById("profileGoalText");
  if (goalEl) goalEl.textContent = user.goal;

  const stressEl = document.getElementById("profileStressText");
  if (stressEl) stressEl.textContent = `${user.stress_level} / 10`;

  const sleepEl = document.getElementById("profileSleepText");
  if (sleepEl) sleepEl.textContent = `${user.sleep_hours} hrs`;

  const medEl = document.getElementById("profileMedicalText");
  if (medEl) medEl.textContent = user.medical_condition || "None";

  // 1. Physical Biometrics
  const ageVal = document.getElementById("profAgeVal");
  if (ageVal) ageVal.textContent = `${user.age} Years`;

  const genderVal = document.getElementById("profGenderVal");
  if (genderVal) genderVal.textContent = user.gender;

  const heightVal = document.getElementById("profHeightVal");
  if (heightVal) {
    const totalInches = user.height_cm / 2.54;
    const ft = Math.floor(totalInches / 12);
    const inRem = Math.round(totalInches % 12);
    heightVal.textContent = `${user.height_cm} cm (${ft} ft ${inRem} in)`;
  }

  const weightVal = document.getElementById("profWeightVal");
  if (weightVal) weightVal.textContent = `${user.weight_kg} kg`;

  const bmiVal = document.getElementById("profBmiVal");
  if (bmiVal) bmiVal.textContent = biometrics.bmi;

  const bmiBadge = document.getElementById("profBmiBadge");
  if (bmiBadge) {
    bmiBadge.textContent = biometrics.bmi_category;
    if (biometrics.bmi < 18.5) bmiBadge.className = "badge badge-cyan";
    else if (biometrics.bmi < 25.0) bmiBadge.className = "badge badge-emerald";
    else if (biometrics.bmi < 30.0) bmiBadge.className = "badge badge-warning";
    else bmiBadge.className = "badge badge-danger";
  }

  // BMR Calculation (Mifflin-St Jeor Formula)
  const isFemale = (user.gender || "").toLowerCase() === "female";
  const bmr = isFemale
    ? Math.round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161)
    : Math.round(10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5);
  const bmrEl = document.getElementById("profBmrVal");
  if (bmrEl) bmrEl.textContent = `${bmr.toLocaleString()} kcal/day`;

  const tdeeEl = document.getElementById("profTdeeVal");
  if (tdeeEl) tdeeEl.textContent = `${biometrics.tdee?.toLocaleString() || bmr} kcal/day`;

  // 2. Lifestyle & Health Status
  const goalDetail = document.getElementById("profGoalDetailVal");
  if (goalDetail) goalDetail.textContent = user.goal;

  const activityEl = document.getElementById("profActivityVal");
  if (activityEl) activityEl.textContent = user.activity_level;

  const sleepDetail = document.getElementById("profSleepVal");
  if (sleepDetail) sleepDetail.textContent = `${user.sleep_hours} hours/night`;

  const dietEl = document.getElementById("profDietVal");
  if (dietEl) dietEl.textContent = user.dietary_preference;

  const stressNum = document.getElementById("profStressNum");
  if (stressNum) stressNum.textContent = `${user.stress_level} / 10`;

  const stressBadge = document.getElementById("profStressBadge");
  if (stressBadge) {
    if (user.stress_level >= 8) {
      stressBadge.textContent = "High / Burnout";
      stressBadge.className = "badge badge-danger";
    } else if (user.stress_level >= 5) {
      stressBadge.textContent = "Moderate";
      stressBadge.className = "badge badge-warning";
    } else {
      stressBadge.textContent = "Calm / Low";
      stressBadge.className = "badge badge-emerald";
    }
  }

  const medicalDetail = document.getElementById("profMedicalVal");
  if (medicalDetail) medicalDetail.textContent = user.medical_condition || "None";

  const archEl = document.getElementById("profArchetypeName");
  if (archEl) archEl.textContent = ml.archetype?.name || "Cardio & Weight Management Achiever";

  // 3. Active Regimen Targets
  const calTarget = document.getElementById("profCalTarget");
  if (calTarget) calTarget.textContent = `${biometrics.target_calories?.toLocaleString() || 1940} kcal`;

  const proteinTarget = document.getElementById("profProteinTarget");
  if (proteinTarget) proteinTarget.textContent = `${biometrics.macros?.protein_g || 120} g`;

  const carbsTarget = document.getElementById("profCarbsTarget");
  if (carbsTarget) carbsTarget.textContent = `${biometrics.macros?.carbs_g || 190} g`;

  const fatsTarget = document.getElementById("profFatsTarget");
  if (fatsTarget) fatsTarget.textContent = `${biometrics.macros?.fats_g || 54} g`;

  const waterTarget = document.getElementById("profWaterTarget");
  if (waterTarget) waterTarget.textContent = `${diet.water_target_liters || 3.0} Liters`;

  const splitTarget = document.getElementById("profSplitTarget");
  if (splitTarget) splitTarget.textContent = `${workout.split_name || 'Cardio & Strength'} (${workout.recommended_intensity || 'Moderate'})`;

  const breathTarget = document.getElementById("profBreathTarget");
  if (breathTarget) breathTarget.textContent = `${mental.daily_breathing_sessions || 2} Daily Session(s) (4-7-8 Drill)`;
}

// Web Audio API Gentle Synthesizer for Chimes (Zero external sound file dependencies)
function initAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
}

function playChime(frequency = 520, duration = 0.3) {
  try {
    initAudioContext();
    if (audioCtx.state === "suspended") {
      audioCtx.resume();
    }
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(frequency, audioCtx.currentTime);

    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + duration);
  } catch (e) {
    // Audio might be blocked until user gesture, safely ignore
  }
}

// ==========================================================================
// 8. PROGRESS LOGGING & CHART.JS ANALYTICS
// ==========================================================================
function setupProgressTracking() {
  const form = document.getElementById("progressForm");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!activeUser) {
        showToast("Please complete your assessment first!", "error");
        return;
      }

      const payload = {
        weight_kg: parseFloat(document.getElementById("logWeight").value),
        workouts_completed: parseInt(document.getElementById("logWorkouts").value),
        mood_rating: parseInt(document.getElementById("logMood").value),
        stress_rating: parseInt(document.getElementById("logStress").value),
        notes: document.getElementById("logNotes").value
      };

      try {
        const resp = await fetch(`/api/user/${activeUser.id}/progress`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.status === "success") {
          showToast("Daily progress logged successfully! 📈");
          form.reset();
          fetchProgressHistory(activeUser.id);
        }
      } catch (err) {
        showToast(`Failed to log: ${err.message}`, "error");
      }
    });
  }
}

async function fetchProgressHistory(userId) {
  try {
    const resp = await fetch(`/api/user/${userId}/progress`);
    const data = await resp.json();
    if (data.status === "success" && data.history) {
      renderProgressCharts(data.history);
    }
  } catch (e) {
    console.error("Progress fetch error:", e);
  }
}

function renderProgressCharts(history) {
  // If fewer than 2 data points, generate a smooth 7-day projection starting from user's current weight
  let dates = [];
  let weights = [];
  let moods = [];
  let stresses = [];

  if (history && history.length >= 2) {
    dates = history.map(h => h.log_date || "Day");
    weights = history.map(h => h.weight_kg);
    moods = history.map(h => h.mood_rating || 7);
    stresses = history.map(h => h.stress_rating || 5);
  } else {
    // Generate realistic 7-day initial preview
    const baseW = activeUser ? activeUser.weight_kg : 78;
    const baseS = activeUser ? activeUser.stress_level : 6;
    dates = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Today"];
    weights = [baseW, baseW - 0.2, baseW - 0.3, baseW - 0.5, baseW - 0.4, baseW - 0.7, baseW - 0.9];
    moods = [6, 6, 7, 7, 8, 8, 9];
    stresses = [baseS, baseS, baseS - 1, baseS - 1, baseS - 2, baseS - 2, Math.max(1, baseS - 3)];
  }

  // 1. Weight Chart
  const ctxWeight = document.getElementById("weightHistoryChart")?.getContext("2d");
  if (ctxWeight) {
    if (weightChart) weightChart.destroy();
    weightChart = new Chart(ctxWeight, {
      type: "line",
      data: {
        labels: dates,
        datasets: [{
          label: "Body Weight (kg)",
          data: weights,
          borderColor: "#0d9488",
          backgroundColor: "rgba(13, 148, 136, 0.08)",
          fill: true,
          tension: 0.35,
          pointBackgroundColor: "#0d9488",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#475569", font: { family: "Plus Jakarta Sans", weight: "600" } } }
        },
        scales: {
          x: { ticks: { color: "#64748b" }, grid: { color: "#f1f5f9" } },
          y: { ticks: { color: "#64748b" }, grid: { color: "#f1f5f9" } }
        }
      }
    });
  }

  // 2. Mood vs Stress Chart
  const ctxMood = document.getElementById("moodStressChart")?.getContext("2d");
  if (ctxMood) {
    if (moodStressChart) moodStressChart.destroy();
    moodStressChart = new Chart(ctxMood, {
      type: "line",
      data: {
        labels: dates,
        datasets: [
          {
            label: "Mood (1-10)",
            data: moods,
            borderColor: "#10b981",
            backgroundColor: "transparent",
            tension: 0.35,
            pointBackgroundColor: "#10b981",
            pointBorderColor: "#ffffff",
            pointBorderWidth: 2,
            pointRadius: 4
          },
          {
            label: "Stress Level (1-10)",
            data: stresses,
            borderColor: "#f43f5e",
            backgroundColor: "transparent",
            tension: 0.35,
            pointBackgroundColor: "#f43f5e",
            pointBorderColor: "#ffffff",
            pointBorderWidth: 2,
            pointRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#475569", font: { family: "Plus Jakarta Sans", weight: "600" } } }
        },
        scales: {
          x: { ticks: { color: "#64748b" }, grid: { color: "#f1f5f9" } },
          y: { min: 1, max: 10, ticks: { color: "#64748b" }, grid: { color: "#f1f5f9" } }
        }
      }
    });
  }
}

// ==========================================================================
// 9. ADAPTIVE FEEDBACK MODULE
// ==========================================================================
function setupFeedbackLoop() {
  const stars = document.querySelectorAll("#starRating i");
  const ratingInput = document.getElementById("feedbackRating");

  stars.forEach(star => {
    star.addEventListener("click", () => {
      const r = parseInt(star.getAttribute("data-rating"));
      ratingInput.value = r;
      stars.forEach((s, idx) => {
        if (idx < r) s.classList.add("active");
        else s.classList.remove("active");
      });
    });
  });

  // Radio button active styling
  document.querySelectorAll(".diff-btn input").forEach(radio => {
    radio.addEventListener("change", (e) => {
      document.querySelectorAll(".diff-btn").forEach(b => b.classList.remove("active"));
      e.target.closest(".diff-btn").classList.add("active");
    });
  });

  // Submit Feedback
  const form = document.getElementById("feedbackForm");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!activeUser) {
        showToast("Please complete your assessment first!", "error");
        return;
      }

      const submitBtn = document.getElementById("submitFeedbackBtn");
      submitBtn.disabled = true;

      const difficulty = document.querySelector('input[name="difficulty"]:checked')?.value || "Just Right";
      const payload = {
        rating: parseInt(ratingInput.value),
        difficulty_feedback: difficulty,
        energy_level: document.getElementById("feedbackEnergy").value,
        comments: document.getElementById("feedbackComments").value
      };

      try {
        const resp = await fetch(`/api/user/${activeUser.id}/feedback`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const res = await resp.json();

        const alertBox = document.getElementById("feedbackResultAlert");
        alertBox.style.display = "block";

        if (res.adapted) {
          alertBox.className = "medical-alert-box";
          alertBox.innerHTML = `<i class="fa-solid fa-arrows-rotate"></i> <strong>Adaptive Plan Recalibration:</strong> Based on your feedback (${difficulty}), workout intensity has been recalibrated to <strong>${res.updated_plan.recommended_intensity}</strong>!`;
          if (activePlan) {
            activePlan.workout_plan = res.updated_plan;
            renderWorkoutSection(res.updated_plan);
          }
          showToast("Workout plan adapted in real-time based on your feedback!");
        } else {
          alertBox.className = "medical-alert-box";
          alertBox.style.borderColor = "var(--success-border)";
          alertBox.style.background = "var(--success-light)";
          alertBox.style.color = "var(--success)";
          alertBox.innerHTML = `<i class="fa-solid fa-check-circle"></i> Thank you! Your feedback has been recorded and applied to your routine.`;
          showToast("Feedback saved successfully!");
        }
      } catch (err) {
        showToast(`Feedback error: ${err.message}`, "error");
      } finally {
        submitBtn.disabled = false;
      }
    });
  }
}

// ==========================================================================
// 10. ML METRICS & SHOWCASE (ACADEMIC DEMONSTRATION)
// ==========================================================================
async function fetchMLMetrics() {
  try {
    const resp = await fetch("/api/ml/metrics");
    const data = await resp.json();

    if (data.status === "success" && data.metrics) {
      const m = data.metrics.metrics;
      if (document.getElementById("mlIntensityAcc")) {
        document.getElementById("mlIntensityAcc").textContent = `${m.intensity_accuracy}%`;
        document.getElementById("mlSplitAcc").textContent = `${m.split_accuracy}%`;
        document.getElementById("mlDietAcc").textContent = `${m.diet_accuracy}%`;
      }

      // Populate K-Means clusters
      const clustersContainer = document.getElementById("clustersContainer");
      if (clustersContainer && data.metrics.cluster_profiles) {
        clustersContainer.innerHTML = "";
        Object.keys(data.metrics.cluster_profiles).forEach(k => {
          const prof = data.metrics.cluster_profiles[k];
          const cCard = document.createElement("div");
          cCard.className = "cluster-card";
          cCard.innerHTML = `
            <h4><i class="fa-solid fa-cubes text-cyan"></i> Cluster #${parseInt(k)+1}: ${prof.name}</h4>
            <p>${prof.summary}</p>
            <div class="cluster-stats-row">
              <span>Avg BMI: ${prof.avg_bmi}</span>
              <span>Stress: ${prof.avg_stress}/10</span>
              <span>Sleep: ${prof.avg_sleep}h</span>
            </div>
          `;
          clustersContainer.appendChild(cCard);
        });
      }
    }
  } catch (e) {
    console.error("ML Metrics load error:", e);
  }
}

// ==========================================================================
// 11. AI CHATBOT INTERFACE
// ==========================================================================
function setupChatbot() {
  const fabBtn = document.getElementById("chatToggleBtn");
  const drawer = document.getElementById("chatDrawer");
  const closeBtn = document.getElementById("chatCloseBtn");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const messagesBox = document.getElementById("chatMessages");

  fabBtn?.addEventListener("click", () => {
    drawer.classList.toggle("open");
    if (drawer.classList.contains("open")) {
      chatInput.focus();
    }
  });

  closeBtn?.addEventListener("click", () => {
    drawer.classList.remove("open");
  });

  // Prompt chips
  document.querySelectorAll(".chip-btn").forEach(chip => {
    chip.addEventListener("click", () => {
      const query = chip.getAttribute("data-query");
      chatInput.value = query;
      chatForm.dispatchEvent(new Event("submit"));
    });
  });

  chatForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;

    // Append User Bubble
    appendChatMessage(text, "user");
    chatInput.value = "";

    // Show Typing Indicator
    const typingId = appendTypingIndicator();

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          user_id: activeUser ? activeUser.id : null
        })
      });
      const data = await resp.json();
      removeTypingIndicator(typingId);

      if (data.status === "success") {
        appendChatMessage(data.response, "bot");
      } else {
        appendChatMessage("Sorry, I encountered an issue. Please try again.", "bot");
      }
    } catch (err) {
      removeTypingIndicator(typingId);
      appendChatMessage(`Connection failed: ${err.message}`, "bot");
    }
  });

  function appendChatMessage(msg, sender) {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${sender}-bubble`;

    // Basic markdown conversion for bolding and bullet points
    let formatted = msg
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n- (.*?)/g, '<br>• $1')
      .replace(/\n1\. (.*?)/g, '<br>1. $1')
      .replace(/\n2\. (.*?)/g, '<br>2. $1')
      .replace(/\n3\. (.*?)/g, '<br>3. $1');

    bubble.innerHTML = `<p>${formatted}</p>`;
    messagesBox.appendChild(bubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function appendTypingIndicator() {
    const id = `typing-${Date.now()}`;
    const bubble = document.createElement("div");
    bubble.id = id;
    bubble.className = "chat-bubble bot-bubble";
    bubble.innerHTML = `<p><i class="fa-solid fa-circle-notch fa-spin text-primary"></i> WellNex Guide is replying...</p>`;
    messagesBox.appendChild(bubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }
}

// ==========================================================================
// 12. TOAST NOTIFICATIONS
// ==========================================================================
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";
  const icon = type === "success" ? "fa-circle-check text-success" : "fa-circle-exclamation text-danger";
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
