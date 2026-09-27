# Dataset Documentation: Campus Placement Data

## 1. Overview & Provenance

- **Dataset Name**: Factors Affecting Campus Placement
- **Original Source**: Kaggle (`benroshan/factors-affecting-campus-placement`)
- **Source URL**: https://www.kaggle.com/datasets/benroshan/factors-affecting-campus-placement
- **Hosting Repository**: Gourav Khator (`gouravkhator/Student-Placement-Prediction`)
- **Direct Source URL**: https://raw.githubusercontent.com/gouravkhator/Student-Placement-Prediction/master/Placement_Data_Full_Class.csv
- **License**: CC0: Public Domain
- **Retrieval Date**: September 27, 2026
- **Data Status**: Real-world collected institutional data from campus placement drives at Jain University (Bangalore, India).
- **Original Filename**: `Placement_Data_Full_Class.csv`

## 2. Dataset Dimensions & Schema

- **Total Observations (Rows)**: 215 students
- **Total Variables (Columns)**: 15 attributes
- **Target Variable**: `status` (`Placed` vs `Not Placed`)

| Column Name | Data Type | Description | Values / Range |
|:---|:---|:---|:---|
| `sl_no` | Integer | Serial Identifier (Anonymized student ID) | 1 to 215 |
| `gender` | Categorical | Student gender | `'M'` (Male, 139), `'F'` (Female, 76) |
| `ssc_p` | Float | 10th grade (Secondary School) percentage | 40.89% – 89.40% |
| `ssc_b` | Categorical | Board of 10th education | `'Central'` (116), `'Others'` (99) |
| `hsc_p` | Float | 12th grade (Higher Secondary) percentage | 37.00% – 97.70% |
| `hsc_b` | Categorical | Board of 12th education | `'Others'` (131), `'Central'` (84) |
| `hsc_s` | Categorical | Stream in Higher Secondary education | `'Commerce'` (113), `'Science'` (91), `'Arts'` (11) |
| `degree_p` | Float | Undergraduate Degree percentage | 50.00% – 91.00% |
| `degree_t` | Categorical | Undergraduate Degree discipline | `'Comm&Mgmt'` (145), `'Sci&Tech'` (59), `'Others'` (11) |
| `workex` | Categorical | Prior Work Experience | `'No'` (141), `'Yes'` (74) |
| `etest_p` | Float | College Employability / Aptitude test percentage | 50.00% – 98.00% |
| `specialisation` | Categorical | Post-Graduation (MBA) Specialisation | `'Mkt&Fin'` (120), `'Mkt&HR'` (95) |
| `mba_p` | Float | MBA percentage | 51.21% – 77.89% |
| `status` | Categorical | Campus placement outcome | `'Placed'` (148), `'Not Placed'` (67) |
| `salary` | Float | Annual salary package offered in INR (Placed only) | ₹200,000 – ₹940,000 (NaN for 67 unplaced) |

## 3. Data Audit Findings

- **Missing Values**: Only present in `salary` (67 missing entries). All 67 missing values correspond exactly to students whose `status` is `'Not Placed'`. Placed students have 0 missing values for salary.
- **Duplicates**: 0 duplicate rows; 0 duplicate serial numbers (`sl_no` is strictly unique from 1 to 215).
- **Value Ranges**: All academic percentages (`ssc_p`, `hsc_p`, `degree_p`, `etest_p`, `mba_p`) fall within valid ranges (37% to 98%). No impossible percentages (>100% or <0%) detected.
- **Categorical Integrity**: Clean categorical strings without extra whitespaces, irregular spellings, or corrupt encodings.

## 4. Cleaning & Transformations Applied

1. Column normalization: Human-readable display mapping maintained while retaining standard identifiers.
2. Binary indicator generation: Numeric binary target `is_placed` (1 for `Placed`, 0 for `Not Placed`) for statistical analysis.
3. Salary imputation handling: Salary for unplaced students explicitly tagged as non-applicable / null (not imputed with 0 to prevent severe distortion of salary distribution statistics).
4. Academic banding: Categorized `degree_p` and `ssc_p` into performance bands (`<60%`, `60–70%`, `70–80%`, `80%+`) to evaluate non-linear placement rate transitions.
5. Derived experience and discipline flags for multi-variable breakdown and exception discovery.
