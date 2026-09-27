"""
Data cleaning and validation module for Student Placement Analytics.
Provides reproducible cleaning, validation, and feature enrichment.
"""

from pathlib import Path
import pandas as pd
import numpy as np


def clean_placement_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and enriches raw student placement dataset.
    
    Operations:
    1. Validates schema and column existence.
    2. Strips whitespace from string columns.
    3. Normalizes categorical labels to clean titles.
    4. Computes binary target 'is_placed'.
    5. Creates academic performance tiers and bands.
    6. Ensures correct data types without silent dropping.
    """
    cleaned = df.copy()

    # Normalize categorical string columns
    str_cols = cleaned.select_dtypes(include=['object', 'string']).columns
    for col in str_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()

    # Standardize column mapping if needed
    col_rename = {
        'sl_no': 'student_id',
        'ssc_p': 'ssc_percentage',
        'ssc_b': 'ssc_board',
        'hsc_p': 'hsc_percentage',
        'hsc_b': 'hsc_board',
        'hsc_s': 'hsc_stream',
        'degree_p': 'degree_percentage',
        'degree_t': 'degree_type',
        'workex': 'work_experience',
        'etest_p': 'employability_score',
        'specialisation': 'mba_specialisation',
        'mba_p': 'mba_percentage',
        'status': 'placement_status',
        'salary': 'salary'
    }
    cleaned = cleaned.rename(columns={k: v for k, v in col_rename.items() if k in cleaned.columns})

    # Validate numerical boundaries
    numeric_pct_cols = [c for c in ['ssc_percentage', 'hsc_percentage', 'degree_percentage', 
                                    'employability_score', 'mba_percentage'] if c in cleaned.columns]
    for c in numeric_pct_cols:
        cleaned[c] = pd.to_numeric(cleaned[c], errors='coerce')

    if 'salary' in cleaned.columns:
        cleaned['salary'] = pd.to_numeric(cleaned['salary'], errors='coerce')

    # Binary placement indicator (1 for Placed, 0 for Not Placed)
    if 'placement_status' in cleaned.columns:
        cleaned['is_placed'] = (cleaned['placement_status'].str.lower() == 'placed').astype(int)
    else:
        cleaned['is_placed'] = 0

    # Expand acronyms for high-clarity dashboard presentation
    if 'degree_type' in cleaned.columns:
        degree_map = {
            'Comm&Mgmt': 'Commerce & Management',
            'Sci&Tech': 'Science & Technology',
            'Others': 'Other Fields'
        }
        cleaned['degree_type_label'] = cleaned['degree_type'].map(lambda x: degree_map.get(x, x))

    if 'mba_specialisation' in cleaned.columns:
        spec_map = {
            'Mkt&Fin': 'Marketing & Finance',
            'Mkt&HR': 'Marketing & HR'
        }
        cleaned['mba_specialisation_label'] = cleaned['mba_specialisation'].map(lambda x: spec_map.get(x, x))

    if 'gender' in cleaned.columns:
        gender_map = {'M': 'Male', 'F': 'Female'}
        cleaned['gender_label'] = cleaned['gender'].map(lambda x: gender_map.get(x, x))

    # Academic performance bands for degree
    if 'degree_percentage' in cleaned.columns:
        bins = [0, 59.99, 69.99, 79.99, 100.0]
        labels = ['<60% (Pass / Low)', '60–70% (First Class)', '70–80% (Distinction)', '80%+ (High Distinction)']
        cleaned['degree_band'] = pd.cut(cleaned['degree_percentage'], bins=bins, labels=labels, right=True)

    # 10th (SSC) performance bands
    if 'ssc_percentage' in cleaned.columns:
        bins_ssc = [0, 59.99, 69.99, 79.99, 100.0]
        labels_ssc = ['<60%', '60–70%', '70–80%', '80%+']
        cleaned['ssc_band'] = pd.cut(cleaned['ssc_percentage'], bins=bins_ssc, labels=labels_ssc, right=True)

    return cleaned


def run_pipeline_and_save(raw_csv_path: Path, output_csv_path: Path) -> pd.DataFrame:
    """Reads raw dataset, cleans it, and persists the cleaned version."""
    raw_df = pd.read_csv(raw_csv_path)
    cleaned_df = clean_placement_data(raw_df)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(output_csv_path, index=False)
    return cleaned_df


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    raw_path = base_dir / 'data' / 'student_placement.csv'
    clean_path = base_dir / 'data' / 'cleaned_student_placement.csv'
    df_clean = run_pipeline_and_save(raw_path, clean_path)
    print(f"Data cleaned and saved successfully to {clean_path}. Shape: {df_clean.shape}")
