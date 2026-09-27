"""
Analytical functions and metrics computation for Placement Dashboard.
Computes KPIs, group aggregations, breakdowns, and pattern-break exceptions.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes executive overview key performance indicators.
    """
    total = len(df)
    if total == 0:
        return {
            'total_students': 0,
            'placed_students': 0,
            'unplaced_students': 0,
            'placement_rate': 0.0,
            'avg_salary': None,
            'median_salary': None,
            'students_with_workex': 0,
            'workex_pct': 0.0,
            'avg_degree_pct': 0.0
        }

    placed_count = int(df['is_placed'].sum()) if 'is_placed' in df.columns else 0
    unplaced_count = total - placed_count
    placement_rate = (placed_count / total * 100.0) if total > 0 else 0.0

    # Salary KPIs (Placed students only)
    has_salary = 'salary' in df.columns and df['salary'].dropna().count() > 0
    if has_salary:
        placed_salaries = df.loc[df['is_placed'] == 1, 'salary'].dropna()
        avg_salary = float(placed_salaries.mean()) if len(placed_salaries) > 0 else None
        median_salary = float(placed_salaries.median()) if len(placed_salaries) > 0 else None
    else:
        avg_salary = None
        median_salary = None

    # Work experience KPI
    if 'work_experience' in df.columns:
        workex_count = int((df['work_experience'].str.lower() == 'yes').sum())
        workex_pct = (workex_count / total * 100.0)
    else:
        workex_count = 0
        workex_pct = 0.0

    avg_degree = float(df['degree_percentage'].mean()) if 'degree_percentage' in df.columns else 0.0

    return {
        'total_students': total,
        'placed_students': placed_count,
        'unplaced_students': unplaced_count,
        'placement_rate': placement_rate,
        'avg_salary': avg_salary,
        'median_salary': median_salary,
        'students_with_workex': workex_count,
        'workex_pct': workex_pct,
        'avg_degree_pct': avg_degree
    }


def compute_academic_band_analysis(df: pd.DataFrame, band_col: str = 'degree_band') -> pd.DataFrame:
    """
    Computes placement rates and statistics across academic performance bands.
    """
    if band_col not in df.columns or len(df) == 0:
        return pd.DataFrame()

    grouped = df.groupby(band_col, observed=False).agg(
        total_students=('is_placed', 'count'),
        placed_students=('is_placed', 'sum')
    ).reset_index()

    grouped['placement_rate'] = (grouped['placed_students'] / grouped['total_students'] * 100.0).fillna(0.0)
    return grouped


def compute_group_metrics(df: pd.DataFrame, group_col: str, label_col: str = None) -> pd.DataFrame:
    """
    Computes placement rate, total students, placed count, and average salary for a category.
    """
    if group_col not in df.columns or len(df) == 0:
        return pd.DataFrame()

    active_col = label_col if (label_col and label_col in df.columns) else group_col

    agg_dict = {
        'total_students': ('is_placed', 'count'),
        'placed_students': ('is_placed', 'sum')
    }
    if 'salary' in df.columns:
        agg_dict['avg_salary'] = ('salary', lambda x: x[df.loc[x.index, 'is_placed'] == 1].mean())

    grouped = df.groupby(active_col, observed=False).agg(**agg_dict).reset_index()
    grouped['placement_rate'] = (grouped['placed_students'] / grouped['total_students'] * 100.0).fillna(0.0)

    # Sort descending by total students
    grouped = grouped.sort_values(by='total_students', ascending=False)
    return grouped


def compute_interaction_breakdown(df: pd.DataFrame, factor_a: str, factor_b: str) -> pd.DataFrame:
    """
    Computes placement rate across two interacting categorical dimensions.
    """
    if factor_a not in df.columns or factor_b not in df.columns or len(df) == 0:
        return pd.DataFrame()

    grouped = df.groupby([factor_a, factor_b], observed=False).agg(
        total_students=('is_placed', 'count'),
        placed_students=('is_placed', 'sum')
    ).reset_index()

    grouped['placement_rate'] = (grouped['placed_students'] / grouped['total_students'] * 100.0).fillna(0.0)
    return grouped


def compute_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes correlation between academic/score variables and binary placement outcome.
    """
    potential_vars = [
        ('ssc_percentage', '10th (SSC) %'),
        ('hsc_percentage', '12th (HSC) %'),
        ('degree_percentage', 'Degree %'),
        ('employability_score', 'Employability Score'),
        ('mba_percentage', 'MBA %')
    ]
    records = []
    if 'is_placed' not in df.columns or len(df) < 5:
        return pd.DataFrame()

    for col, display_name in potential_vars:
        if col in df.columns:
            corr_val = df[col].corr(df['is_placed'])
            placed_mean = df.loc[df['is_placed'] == 1, col].mean()
            unplaced_mean = df.loc[df['is_placed'] == 0, col].mean()
            records.append({
                'Variable': display_name,
                'Correlation with Placement (r)': round(corr_val, 3),
                'Placed Mean': round(placed_mean, 2) if pd.notnull(placed_mean) else 0.0,
                'Unplaced Mean': round(unplaced_mean, 2) if pd.notnull(unplaced_mean) else 0.0,
                'Mean Difference': round(placed_mean - unplaced_mean, 2) if (pd.notnull(placed_mean) and pd.notnull(unplaced_mean)) else 0.0
            })

    res = pd.DataFrame(records)
    if not res.empty:
        res = res.sort_values(by='Correlation with Placement (r)', ascending=False)
    return res


def identify_pattern_breaks(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Identifies observations where the typical pattern breaks using transparent quantile/domain rules:
    
    1. High Academic + Not Placed:
       Degree % >= 75th percentile (or >= 72%) AND status == 'Not Placed'
    2. Lower Academic + Placed:
       Degree % < 50th percentile (Median < 66%) AND status == 'Placed'
    3. Work Experience + Not Placed:
       work_experience == 'Yes' AND status == 'Not Placed'
    4. No Work Experience + Placed:
       work_experience == 'No' AND status == 'Placed'
    """
    if len(df) == 0 or 'degree_percentage' not in df.columns:
        return {
            'high_acad_not_placed': pd.DataFrame(),
            'high_acad_count': 0,
            'high_acad_threshold': 0,
            'low_acad_placed': pd.DataFrame(),
            'low_acad_count': 0,
            'low_acad_threshold': 0,
            'workex_not_placed': pd.DataFrame(),
            'workex_not_placed_count': 0,
            'no_workex_placed': pd.DataFrame(),
            'no_workex_placed_count': 0
        }

    q75 = float(df['degree_percentage'].quantile(0.75))
    median = float(df['degree_percentage'].median())

    # 1. High academic, not placed
    high_acad_df = df[(df['degree_percentage'] >= q75) & (df['is_placed'] == 0)].copy()

    # 2. Below median academic, placed
    low_acad_df = df[(df['degree_percentage'] < median) & (df['is_placed'] == 1)].copy()

    # 3. Work experience, not placed
    if 'work_experience' in df.columns:
        workex_not_placed_df = df[(df['work_experience'].str.lower() == 'yes') & (df['is_placed'] == 0)].copy()
        no_workex_placed_df = df[(df['work_experience'].str.lower() == 'no') & (df['is_placed'] == 1)].copy()
    else:
        workex_not_placed_df = pd.DataFrame()
        no_workex_placed_df = pd.DataFrame()

    return {
        'high_acad_not_placed': high_acad_df,
        'high_acad_count': len(high_acad_df),
        'high_acad_threshold': round(q75, 1),
        'low_acad_placed': low_acad_df,
        'low_acad_count': len(low_acad_df),
        'low_acad_threshold': round(median, 1),
        'workex_not_placed': workex_not_placed_df,
        'workex_not_placed_count': len(workex_not_placed_df),
        'no_workex_placed': no_workex_placed_df,
        'no_workex_placed_count': len(no_workex_placed_df)
    }
