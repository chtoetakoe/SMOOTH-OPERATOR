# Data Dictionary

This document explains what each column in datasets means.

---

## Raw Data

These are the original files downloaded. They come from the Ergast F1 database.

### races.csv

Information about each Grand Prix race.

| Column    | Type | Description                           | Example                   |
| --------- | ---- | ------------------------------------- | ------------------------- |
| raceId    | int  | Unique ID for each race               | 1050                      |
| year      | int  | Season year                           | 2023                      |
| round     | int  | Race number in the season             | 1                         |
| circuitId | int  | Which track (links to circuits table) | 1                         |
| name      | text | Name of the Grand Prix                | "Australian Grand Prix"   |
| date      | date | Date of the race                      | "2023-03-05"              |
| time      | text | Start time (UTC)                      | "05:00:00"                |
| url       | text | Wikipedia link                        | "https://en.wikipedia..." |

### results.csv

Race results for each driver in each race. This is main table.

| Column          | Type  | Description                                 | Example       |
| --------------- | ----- | ------------------------------------------- | ------------- |
| resultId        | int   | Unique ID for this result                   | 25000         |
| raceId          | int   | Which race (links to races)                 | 1050          |
| driverId        | int   | Which driver (links to drivers)             | 830           |
| constructorId   | int   | Which team (links to constructors)          | 9             |
| number          | int   | Car number                                  | 1             |
| grid            | int   | Starting position (0 = pit lane or unknown) | 1             |
| position        | text  | Finishing position (can be "R" for retired) | "1"           |
| positionText    | text  | Same as position but always text            | "1"           |
| positionOrder   | int   | Finishing position as number                | 1             |
| points          | float | Points scored                               | 25.0          |
| laps            | int   | Laps completed                              | 58            |
| time            | text  | Finishing time or gap                       | "1:33:56.736" |
| milliseconds    | int   | Finish time in ms                           | 5636736       |
| fastestLap      | int   | Which lap was fastest                       | 45            |
| rank            | int   | Fastest lap ranking                         | 1             |
| fastestLapTime  | text  | Fastest lap time                            | "1:20.235"    |
| fastestLapSpeed | float | Speed in km/h                               | 230.5         |
| statusId        | int   | How they finished (links to status)         | 1             |

### drivers.csv

Information about each driver.

| Column      | Type | Description               | Example                   |
| ----------- | ---- | ------------------------- | ------------------------- |
| driverId    | int  | Unique ID                 | 830                       |
| driverRef   | text | Short name (used in URLs) | "max_verstappen"          |
| number      | int  | Permanent car number      | 1                         |
| code        | text | 3-letter code             | "VER"                     |
| forename    | text | First name                | "Max"                     |
| surname     | text | Last name                 | "Verstappen"              |
| dob         | date | Date of birth             | "1997-09-30"              |
| nationality | text | Country                   | "Dutch"                   |
| url         | text | Wikipedia link            | "https://en.wikipedia..." |

### constructors.csv

Information about each team (constructor = team in F1).

| Column         | Type | Description    | Example                   |
| -------------- | ---- | -------------- | ------------------------- |
| constructorId  | int  | Unique ID      | 9                         |
| constructorRef | text | Short name     | "red_bull"                |
| name           | text | Full team name | "Red Bull"                |
| nationality    | text | Country        | "Austrian"                |
| url            | text | Wikipedia link | "https://en.wikipedia..." |

### status.csv

Lookup table for how a driver finished the race.

| Column   | Type | Description   | Example    |
| -------- | ---- | ------------- | ---------- |
| statusId | int  | Unique ID     | 1          |
| status   | text | What happened | "Finished" |

Common status values:

- "Finished" = completed the race
- "Accident" = crashed
- "Engine" = engine failure
- "Gearbox" = gearbox problem
- "+1 Lap" = finished one lap behind
- "Did not start" = DNS

---

## Processed Data (what was created)

After cleaning and adding features these datasets were created

### f1_base_2018_2024.csv

Created by Notebook 01. Basic merged dataset filtered to 2018-2024.

| Column          | Type  | Description                        |
| --------------- | ----- | ---------------------------------- |
| raceId          | int   | Race ID                            |
| year            | int   | Season year                        |
| round           | int   | Race number in season              |
| name            | text  | Grand Prix name                    |
| date            | date  | Race date                          |
| driverId        | int   | Driver ID                          |
| driverName      | text  | Full name (e.g., "Max Verstappen") |
| nationality     | text  | Driver's country                   |
| constructorId   | int   | Team ID                            |
| constructorName | text  | Team name (e.g., "Red Bull")       |
| grid            | int   | Starting position                  |
| positionOrder   | int   | Finishing position                 |
| points          | float | Points scored                      |
| statusId        | int   | Finish status ID                   |

### processed_f1_2018_2024.csv

Created by Notebook 02. This is final dataset with all features

#### Original Columns (from base dataset)

| Column          | Type  | Description                     |
| --------------- | ----- | ------------------------------- |
| raceId          | int   | Race ID                         |
| year            | int   | Season year                     |
| round           | int   | Race number                     |
| name            | text  | Grand Prix name                 |
| date            | date  | Race date                       |
| driverId        | int   | Driver ID                       |
| driverName      | text  | Driver full name                |
| nationality     | text  | Driver's country                |
| constructorId   | int   | Team ID                         |
| constructorName | text  | Team name                       |
| grid            | int   | Original grid (0 = unknown)     |
| positionOrder   | int   | Finishing position              |
| points          | float | Points scored (TARGET VARIABLE) |

#### Cleaned Columns

| Column     | Type  | Description                                                                                                                                  |
| ---------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| grid_clean | float | Grid position with 0 replaced by NaN. This is better for analysis because 0 doesn't mean pole position - it means unknown or pit lane start. |

#### Race-Level Features (created in Notebook 02)

| Column        | Type  | Description                                                                                                                  |
| ------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------- |
| position_gain | float | `grid_clean - positionOrder`. Positive = gained positions during race. Example: Started P10, finished P5 → position_gain = 5 |
| is_podium     | int   | 1 if finished P1, P2, or P3. 0 otherwise.                                                                                    |

#### Status Flags (created in Notebook 02)

| Column      | Type | Description                                   |
| ----------- | ---- | --------------------------------------------- |
| is_finished | int  | 1 if driver completed the race                |
| is_dnf      | int  | 1 if Did Not Finish (crash, mechanical, etc.) |
| is_dns      | int  | 1 if Did Not Start                            |

#### Historical Features (created in Notebook 02)

These are the most important features. They use **only past data** to avoid data leakage.

| Column                      | Type  | Description                                                                                                                                                                                                                     |
| --------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| driver_races_past           | int   | How many races this driver has done before this race. Example: If this is Hamilton's 300th race, value is 299.                                                                                                                  |
| driver_avg_points_past      | float | Driver's average points per race BEFORE this race. Calculated using `expanding().mean().shift(1)` so we never use future data.                                                                                                  |
| driver_consistency_past     | float | Standard deviation of driver's past finishing positions. Lower = more consistent. A driver who always finishes P3-P5 has low consistency (good). A driver who finishes P1 one race and P15 the next has high consistency (bad). |
| constructor_races_past      | int   | How many races this team has done before this race.                                                                                                                                                                             |
| constructor_strength_past   | float | Team's average points per race BEFORE this race. High value = strong team like Red Bull or Mercedes.                                                                                                                            |
| constructor_avg_finish_past | float | Team's average finishing position. Lower = better.                                                                                                                                                                              |

---

## Understanding the Historical Features

### Why "past" matters

only use data from BEFORE each race to calculate features. This is super important.

**Wrong way (data leakage):**

```
Driver's average points = average of ALL their races
```

This is wrong because we're using future races to predict current race.

**Right way (no leakage):**

```
Driver's average points = average of races BEFORE this one
```

This is correct because we only know past information.

### Example

Let's say Max Verstappen has these results:

- Race 1: 25 points
- Race 2: 18 points
- Race 3: 25 points
- Race 4: ? (we want to predict this)

For Race 4, his `driver_avg_points_past` would be:

```
(25 + 18 + 25) / 3 = 22.67 points
```

We DON'T include Race 4's result because that's what we're trying to predict!

### The shift(1) trick

In our code, we use:

```python
expanding().mean().shift(1)
```

- `expanding()` = calculate using all data up to current row
- `mean()` = take the average
- `shift(1)` = move everything down one row (so current row uses only PAST data)

This is the key technique that prevents data leakage.

---

## Feature Correlations with Points

Based on our EDA (Notebook 03), here's how each feature relates to points:

| Feature                   | Correlation | Meaning                                                |
| ------------------------- | ----------- | ------------------------------------------------------ |
| positionOrder             | -0.85       | Strong negative (obvious - position determines points) |
| is_podium                 | +0.84       | Strong positive (top 3 get lots of points)             |
| grid_clean                | -0.66       | Strong negative (better qualifying = more points)      |
| constructor_strength_past | +0.65       | Strong positive (good team = more points)              |
| driver_avg_points_past    | +0.62       | Strong positive (good driver = more points)            |
| position_gain             | +0.35       | Moderate positive (gaining positions helps)            |
| driver_consistency_past   | -0.15       | Weak negative (more consistent = slightly more points) |

---

## Notes

- All dates are in YYYY-MM-DD format
- Points follow F1 scoring: P1=25, P2=18, P3=15, P4=12, P5=10, P6=8, P7=6, P8=4, P9=2, P10=1
- Fastest lap bonus (+1 point) is included in some races
- Sprint race points are separate but included in our dataset
- NaN values mean the data is missing or not applicable
