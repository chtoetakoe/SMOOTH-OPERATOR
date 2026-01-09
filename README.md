# Formula 1 Race Performance Analysis (2018-2024)

A data science project that analyzes F1 race data to understand what factors help drivers score more points, and builds machine learning models to predict race results.

---

## What This Project Does

This project answers a simple question: **What makes an F1 driver score points?**

We look at 7 years of F1 data (2018-2024) and find out:

- How important is qualifying position?
- Does the team (constructor) matter?
- Can we predict how many points a driver will score?

**Spoiler:** Qualifying position and team strength are the two biggest factors. Our best model (Decision Tree) predicts race points with 85% accuracy (R² = 0.85).

---

## Key Findings

| Finding                       | Details                                                         |
| ----------------------------- | --------------------------------------------------------------- |
| Qualifying is crucial         | Starting P1-3 gives you median 18 points, P11-20 gives median 0 |
| Team matters a lot            | Mercedes, Red Bull, Ferrari average 10-15 points per race       |
| Track type changes everything | Monaco: 67% win from pole, Monza: only 14%                      |
| Decision Tree wins            | 4x better than Linear Regression for this problem               |

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
├── CONTRIBUTIONS.md            # Who did what
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

Download F1 data from [Ergast API](http://ergast.com/mrd/) and put the CSV files in `data/raw/`.

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

**Important:** Run them in order! Each notebook needs the output from the previous one.

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
- Adds historical features (driver's past average points, team strength, etc.)
- Uses `shift(1)` to avoid data leakage
- Saves: `processed_f1_2018_2024.csv`

### Notebook 3: EDA & Visualization

- Creates 11 charts to understand the data
- Shows correlation between features and points
- Compares different tracks (Monaco vs Monza)
- Explains what each chart means

### Notebook 4: Machine Learning

- Splits data by time (2018-2022 for training, 2023-2024 for testing)
- Trains Linear Regression and Decision Tree models
- Compares them using MSE, RMSE, MAE, and R²
- Decision Tree wins with R² = 0.85

---

## Features We Created

We didn't just use the raw data. We created new features to help the model:

| Feature                     | What it means                                  |
| --------------------------- | ---------------------------------------------- |
| `grid_clean`                | Qualifying position (with unknowns removed)    |
| `position_gain`             | How many places gained/lost during race        |
| `is_podium`                 | Did they finish top 3? (1 = yes, 0 = no)       |
| `driver_avg_points_past`    | Driver's average points in previous races      |
| `driver_consistency_past`   | How consistent is the driver? (lower = better) |
| `constructor_strength_past` | Team's average points in previous races        |

**Important:** All historical features use only PAST data. We never use future information to predict - that would be cheating (data leakage).

---

## Model Results

We tested two models:

| Model             | MSE   | RMSE | MAE  | R²   |
| ----------------- | ----- | ---- | ---- | ---- |
| Decision Tree     | 39.76 | 6.3  | 3.94 | 0.25 |
| Linear Regression | 25.81 | 5.08 | 3.60 | 0.51 |

**Winner: Linear Regresion**

---

## Visualizations

We created these charts (saved in `reports/figures/`):

1. **Points Distribution** - Most drivers score 0 points (right-skewed)
2. **Average Points by Year** - Stayed around 5 points per race
3. **Grid vs Points Scatter** - Clear negative correlation
4. **Grid Bucket Boxplot** - P1-3 vs P4-10 vs P11-20
5. **Constructor Strength vs Points** - Strong positive correlation
6. **Driver Consistency vs Points** - Consistent drivers score more
7. **Top 10 Constructors** - Mercedes, Red Bull, Ferrari on top
8. **Top 15 Drivers** - Verstappen and Hamilton lead
9. **Correlation Heatmap** - Which features matter most
10. **Correlation Bar Chart** - Same info, different view
11. **Pole Win Rate by Track** - Monaco 67% vs Monza 14%

---

## What was learned from project

1. **Qualifying is everything** - If you don't qualify well, you probably won't score points
2. **The car matters** - Even the best driver can't win in a slow car
3. **Some tracks are special** - At Monaco you can't overtake, at Monza you can
4. **Simple models work** - Decision Tree with depth 8 beats fancy approaches
5. **Time-based splits are important** - Random splits can leak future information

---

## Limitations

- We only used 2018-2024 data (regulations changed in 2022)
- Weather data is not included
- Tire strategy is not included
- Sprint races are mixed with normal races
- Some drivers have very few races in the dataset
