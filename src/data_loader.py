"""
Data loader module for Student Placement Analytics Dashboard.
Provides safe, cached loading with graceful fallbacks.
"""

from pathlib import Path
import pandas as pd
import streamlit as st
from src.data_cleaning import clean_placement_data


def get_base_dir() -> Path:
    """Returns the absolute root directory of the project in a portable manner."""
    return Path(__file__).resolve().parent.parent


@st.cache_data(show_spinner=False)
def load_data(use_cleaned: bool = True) -> pd.DataFrame:
    """
    Loads placement dataset safely from project data directory.
    
    If cleaned file exists, loads it; otherwise loads raw and cleans in-memory.
    """
    base_dir = get_base_dir()
    cleaned_path = base_dir / 'data' / 'cleaned_student_placement.csv'
    raw_path = base_dir / 'data' / 'student_placement.csv'

    if use_cleaned and cleaned_path.exists():
        df = pd.read_csv(cleaned_path)
    elif raw_path.exists():
        raw_df = pd.read_csv(raw_path)
        df = clean_placement_data(raw_df)
    else:
        raise FileNotFoundError(
            f"Dataset not found at {cleaned_path} or {raw_path}. Please verify data directory."
        )

    return df
