# Formula 1 Race Performance Analysis (2018-2024)

A data science project that analyzes F1 race data to understand what factors help drivers score more points, and builds machine learning models to predict race results.

---

## What This Project Does

This project answers a simple question: **What makes an F1 driver score points?**

We look at 7 years of F1 data (2018-2024) and find out:

- How important is qualifying position?
- Does the team (constructor) matter?
- Can we predict how many points a driver will score?

---

## Key Findings

| Finding                       | Details                                                         |
| ----------------------------- | --------------------------------------------------------------- |
| Qualifying is crucial         | Starting P1-3 gives you median 18 points, P11-20 gives median 0 |
| Team matters a lot            | Mercedes, Red Bull, Ferrari average 10-15 points per race       |
| Track type changes everything | Monaco: 67% win from pole, Monza: only 14%                      |
| Decision Tree wins            | After tuning, beats Linear Regression (R² 0.565 vs 0.515)       |

---

## Project Structure

```
f1-race-analysis/
│
├── data/
│   ├── raw/                    # Original CSV files from Ergast API
│   │   ├── races.csv
│   │   ├── results.csv
│   │   ├── drivers.csv
│   │   ├── constructors.csv
│   │   └── status.csv
│   │
│   └── processed/              # Cleaned datasets we created
│       ├── f1_base_2018_2024.csv
│       └── processed_f1_2018_2024.csv
│
├── notebooks/
│   ├── 01_data_exploration.ipynb      # Load and explore raw data
│   ├── 02_data_preprocessing.ipynb    # Clean data and create features
│   ├── 03_eda_visualization.ipynb     # Charts and analysis
│   └── 04_machine_learning.ipynb      # Build and compare models
│
├── src/
│   ├── data_processing.py      # Functions for cleaning and features
│   ├── visualization.py        # Functions for making plots
│   └── models.py               # Functions for ML models
│
├── reports/
│   └── figures/                # All saved charts (PNG files)
│
├── README.md                   # You are here
├── DATA_DICTIONARY.md          # What each column means
└── requirements.txt            # Python packages needed
```

---

## How to Run This Project

### Step 1: Install Python packages

```bash
pip install pandas numpy matplotlib scikit-learn
```

Or if you have the requirements file:

```bash
pip install -r requirements.txt
```

### Step 2: Get the data

Download F1 data from Kaggle -> (kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020)  and put the CSV files in `data/raw/`.

You need these files:

- races.csv
- results.csv
- drivers.csv
- constructors.csv
- status.csv

### Step 3: Run the notebooks in order

1. **01_data_exploration.ipynb** - Loads raw data and creates base dataset
2. **02_data_preprocessing.ipynb** - Cleans data and adds new features
3. **03_eda_visualization.ipynb** - Makes all the charts
4. **04_machine_learning.ipynb** - Trains and tests the models

---

## The Notebooks

### Notebook 1: Data Exploration

- Loads 5 CSV files from Ergast database
- Checks for missing values
- Merges tables together
- Filters to 2018-2024 only
- Saves: `f1_base_2018_2024.csv`

### Notebook 2: Data Preprocessing

- Cleans grid position (grid=0 means unknown, not pole)
- Creates new features like `position_gain` and `is_podium`
- Adds historical features (driver's past average points, team strength)
- Uses `shift(1)` to avoid data leakage
- Saves: `processed_f1_2018_2024.csv`

### Notebook 3: EDA & Visualization

- Creates 11 charts to understand the data
- Shows correlation between features and points
- Compares different tracks (Monaco vs Monza)
- Explains what each chart means

### Notebook 4: Machine Learning

- Explains why we use Regression (not Classification or Clustering)
- Splits data by time (2018-2022 for training, 2023-2024 for testing)
- Trains Linear Regression and Decision Tree models
- Tunes Decision Tree to find best max_depth
- Compares them using R² and MSE
- Decision Tree (max_depth=3) wins!

---

## Preventing Data Leakage

Data leakage happens when your model accidentally uses future information to predict the past. took several steps to prevent this:

### 1. Time-Based Split

- Training: 2018-2022 (past seasons)
- Testing: 2023-2024 (future seasons)
- never train on future data

### 2. Historical Features with shift(1)

All "past" features only use data from BEFORE each race:

```python
driver_avg_points_past = expanding().mean().shift(1)
```

This means: "average of all races before this one"

### 3. Constructor Features at Race Level

fixed a subtle bug where teammate results could leak within the same race. Now constructor stats are aggregated at the RACE level first, then expanded over races.

### 4. No Post-Race Features

Features like `position_gain` and `is_podium` are calculated AFTER the race. We don't use them for prediction - only for analysis.

---

## Why Regression?

We chose **Regression** because our target variable `points` is a continuous number (0, 1, 2, 4, 6, 8, 10, 12, 15, 18, 25, 26).

| Problem Type   | When to Use             | Our Case                     |
| -------------- | ----------------------- | ---------------------------- |
| **Regression** | Predict a NUMBER        | "How many points?" ✅        |
| Classification | Predict a CATEGORY      | "Will driver win? Yes/No"    |
| Clustering     | Find GROUPS (no target) | "Which drivers are similar?" |

Since we want to predict the actual number of points, Regression is the right choice.

---

## Features We Created

We didn't just use the raw data. We created new features to help the model:

| Feature                     | What it means                                      |
| --------------------------- | -------------------------------------------------- |
| `grid_clean`                | Qualifying position (with unknowns removed)        |
| `position_gain`             | How many places gained/lost during race (EDA only) |
| `is_podium`                 | Did they finish top 3? (EDA only)                  |
| `driver_avg_points_past`    | Driver's average points in previous races          |
| `driver_consistency_past`   | How consistent is the driver? (lower = better)     |
| `constructor_strength_past` | Team's average points in previous races            |

**Important:** All historical features use only PAST data. We never use future information to predict - that would be cheating (data leakage).

---

## Model Results

We tested two models and tuned the Decision Tree:

### Before Tuning

| Model                   | R²    | MSE   |
| ----------------------- | ----- | ----- |
| Linear Regression       | 0.515 | 25.81 |
| Decision Tree (depth=8) | 0.417 | 31.07 |

Decision Tree was overfitting with max_depth=8!

### After Tuning

| Model                       | R²        | MSE       |
| --------------------------- | --------- | --------- |
| **Decision Tree (depth=3)** | **0.565** | **23.18** |
| Linear Regression           | 0.515     | 25.81     |

**Winner: Decision Tree (max_depth=3)**

Why? A shallower tree (depth=3) doesn't overfit. It captures the main patterns without memorizing noise.

### What the Results Mean

- **R² = 0.565**: Our model explains 56.5% of the variance in race points
- **MSE = 23.18**: On average, predictions are off by about √23.18 ≈ 4.8 points
- The remaining ~44% of variance comes from things we don't measure (weather, crashes, strategy, luck)

---

## Feature Importance

The Decision Tree tells us which features matter most:

| Feature                   | Importance |
| ------------------------- | ---------- |
| constructor_strength_past | 74.1%      |
| grid_clean                | 22.0%      |
| driver_avg_points_past    | 3.9%       |
| Other features            | <1%        |

**Key Insight:** Team strength (74%) and qualifying (22%) explain almost all the predictions. In F1, the car matters most!

---

## Visualizations

We created these charts (saved in `reports/figures/`):

**EDA Charts:**

1. Points Distribution - Most drivers score 0 points
2. Average Points by Year - Stable around 5 points
3. Grid vs Points Scatter - Clear negative correlation
4. Grid Bucket Boxplot - P1-3 vs P4-10 vs P11-20
5. Constructor Strength vs Points - Strong positive correlation
6. Driver Consistency vs Points
7. Top 10 Constructors
8. Top 15 Drivers
9. Correlation Heatmap
10. Correlation Bar Chart
11. Pole Win Rate by Track - Monaco 67% vs Monza 14%

**ML Charts:**

1. R² Comparison
2. MSE Comparison
3. Predicted vs Actual
4. Residuals Analysis
5. Feature Importance

---

1. **Qualifying is everything** - If you don't qualify well, you probably won't score points
2. **The car matters most** - Constructor strength is 74% of the model's decisions
3. **Some tracks are special** - At Monaco you can't overtake, at Monza you can
4. **Tuning matters** - Decision Tree went from R²=0.42 to R²=0.57 after tuning
5. **Shallow trees generalize better** - max_depth=3 beats max_depth=8
6. **Data leakage is sneaky** - Even same-race teammate data can leak!
