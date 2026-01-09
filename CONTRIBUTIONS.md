# Project Contributions

---

## Author

| Name                 | Role                          |
| :------------------- | :---------------------------- |
| [Teona Berozashvili] | Data Scientist & Project Lead |

---

## Detailed Work Breakdown

### 1. Data Collection & Exploration (Notebook 01)

- **Tasks:** Ingested raw F1 data (races, results, drivers, constructors, status) from the Ergast Database.
- **Key Accomplishments:**
  - Performed data quality audits using `.missing_report()` to identify `\N` string values and nulls.
  - Merged disparate CSV files into a unified base dataset using relational joins.
  - Standardized the project scope to the modern hybrid era (2018–2024).

### 2. Preprocessing & Feature Engineering (Notebook 02)

- **Tasks:** Transformed raw race data into a "feature store" ready for modeling.
- **Key Accomplishments:**
  - **Domain-Specific Cleaning:** Replaced `grid=0` values with `NaN` to correctly identify pit-lane starts.
  - **Historical Aggregates:** Engineered complex time-aware features (driver/constructor strength and consistency).
  - **Leakage Prevention:** Implemented `.expanding().shift(1)` logic to ensure past averages did not include "future" race results.

### 3. Exploratory Data Analysis (Notebook 03)

- **Tasks:** Investigated variable relationships and validated engineered features.
- **Key Accomplishments:**
  - Developed a suite of 11 F1-branded visualizations using `matplotlib` and `seaborn`.
  - Quantified the correlation between qualifying position and points (-0.66).
  - Conducted deep-dive track analysis comparing pole position value at Monaco vs. Monza.

### 4. Source Modules (`src/` folder)

- **data_processing.py:** Modularized cleaning and aggregate logic (e.g., `add_time_aware_aggregates`, `clean_grid`) for reproducibility.
- **visualization.py:** Built a custom F1-branded plotting library with hex codes for specific team identities and branding colors.
