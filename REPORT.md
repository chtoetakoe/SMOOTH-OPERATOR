# Formula 1 Race Performance Analysis (2018–2024)

## Predicting Race Points Using Machine Learning

### 1) What this project is about

Formula 1 is a sport where drivers earn points based on how they finish in each race. But points don’t depend only on the driver — the car (team/constructor), starting position, and track characteristics also matter.

This project answers two questions:

1. **What factors help F1 drivers score more points?**
2. **Can we predict how many points a driver will score in a race?**

---

### 2) Data used (where it comes from)

I used public data from the **Ergast F1 Database**, covering the seasons **2018–2024**.

The final dataset contains **2,979 race result rows**, where each row represents a driver’s result in a specific race.

Main tables used:

* races (race info, year, track)
* results (finish position, points, grid position)
* drivers (driver identity)
* constructors (team identity)
* status (DNF / finished status)

**What we predict (target):** `points` scored in a race (from 0 to 26).

---

### 3) What I did step-by-step (high level)

This project follows a standard data science workflow:

**Step A — Data cleaning and preparation**

* Loaded multiple tables and merged them into one dataset.
* Fixed data types and handled missing values.
* Cleaned qualifying position to create a reliable feature (`grid_clean`).

**Step B — Exploratory Data Analysis (EDA)**
I used visualizations and statistics to understand patterns, like:

* How points change depending on qualifying position
* How much team performance affects points
* How track characteristics influence outcomes

**Step C — Feature engineering (creating useful predictors)**
I created features that represent a driver’s and team’s past performance:

* `driver_avg_points_past`: driver’s average points before this race
* `driver_consistency_past`: how stable their past results were
* `constructor_strength_past`: team’s historical strength before this race

**Important:** I designed these features using **only past races**, so the model does not “cheat” by using future information.

**Step D — Machine learning**
I trained models that predict the number of points a driver will score.

---

### 4) Key findings (plain language)

**Finding 1: Starting position matters**
Drivers who qualify near the front score far more points on average. Drivers starting deep in the grid often score zero because only the top 10 score points.

**Finding 2: Team strength matters a lot**
Top constructors (like Red Bull, Mercedes, Ferrari) score significantly more points on average because they consistently have faster cars and better overall performance.

**Finding 3: Different tracks behave differently**
Some tracks make overtaking difficult (for example Monaco), which makes qualifying even more important. Other tracks allow more overtaking (like Monza), so starting position is less “locked in.”

---

### 5) How the prediction works 

The model looks at information available **before** a race result happens:

* the driver’s recent history
* the team’s historical strength
* the driver’s qualifying position
* and other basic context

Using this, it predicts a number: **how many points the driver is expected to score**.

---

### 6) Train/test split (why it was done this way)

Instead of randomly splitting the dataset, I used a **time-based split**, which is more realistic:

* **Training:** 2018–2022 (the “past”)
* **Testing:** 2023–2024 (the “future”)

This simulates a real scenario: learning from past seasons and predicting later seasons.

---

### 7) Models compared and results

I compared two regression models:

* **Linear Regression** (simple baseline)
* **Decision Tree Regressor** (can capture non-linear patterns)

Best result:

* **Decision Tree (max_depth = 3): R² = 0.565**

Interpretation in plain language:

* The model explains a meaningful part of point differences, but not everything — because racing outcomes also depend on unpredictable events like crashes, penalties, strategy, and weather.

---

### 8) What mattered most (main insight)

The model’s strongest predictor was:

1. **Constructor/team strength**
2. **Qualifying position**
3. **Driver historical performance**

Main takeaway:
**In Formula 1, the car/team plays the biggest role in predicting points, and qualifying position is the next most important factor.**

---

### 9) Limitations (what this model can’t fully capture)

This project uses historical results and basic race data, so it cannot directly model:

* tire strategy and pit stops
* weather and track temperature
* safety cars and red flags
* penalties and unexpected DNFs
* real-time car upgrades during a season

These factors can strongly affect points and add randomness.


---

### 10) How to run the project (simple)

1. Create and activate a virtual environment
2. Install dependencies from `requirements.txt`
3. Run notebooks in order: `01 → 02 → 03 → 04`
4. The cleaned dataset is saved in `data/processed/` and model results in `reports/`

---


