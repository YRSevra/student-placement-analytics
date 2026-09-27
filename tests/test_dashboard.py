"""
Unit and integration tests for Placement Analytics project.
Verifies data loading, cleaning, KPIs, breakdowns, and edge cases.
"""

from pathlib import Path
import unittest
import pandas as pd
import numpy as np

from src.data_cleaning import clean_placement_data
from src.analysis import (
    compute_kpis,
    compute_academic_band_analysis,
    compute_group_metrics,
    compute_interaction_breakdown,
    compute_correlations,
    identify_pattern_breaks
)
from src.insights import generate_key_findings


class TestPlacementDashboard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        base_dir = Path(__file__).resolve().parent.parent
        raw_path = base_dir / 'data' / 'student_placement.csv'
        assert raw_path.exists(), "Raw dataset must exist"
        raw_df = pd.read_csv(raw_path)
        cls.df = clean_placement_data(raw_df)

    def test_dataset_shape_and_columns(self):
        """Verifies row count and critical columns."""
        self.assertEqual(len(self.df), 215, "Dataset must have exactly 215 rows")
        expected_cols = [
            'student_id', 'degree_percentage', 'work_experience',
            'placement_status', 'is_placed', 'degree_band'
        ]
        for col in expected_cols:
            self.assertIn(col, self.df.columns, f"Missing critical column: {col}")

    def test_kpi_mathematical_consistency(self):
        """Verifies KPI calculations."""
        kpis = compute_kpis(self.df)
        self.assertEqual(kpis['total_students'], 215)
        self.assertEqual(kpis['placed_students'], 148)
        self.assertEqual(kpis['unplaced_students'], 67)
        expected_rate = (148 / 215) * 100.0
        self.assertAlmostEqual(kpis['placement_rate'], expected_rate, places=2)
        self.assertGreater(kpis['avg_salary'], 280000)
        self.assertEqual(kpis['students_with_workex'], 74)

    def test_kpi_empty_dataframe(self):
        """Ensures app handles empty slices without crashing."""
        empty_df = self.df.iloc[0:0]
        kpis = compute_kpis(empty_df)
        self.assertEqual(kpis['total_students'], 0)
        self.assertEqual(kpis['placed_students'], 0)
        self.assertEqual(kpis['placement_rate'], 0.0)
        self.assertIsNone(kpis['avg_salary'])

    def test_academic_band_analysis(self):
        """Verifies academic band computations."""
        band_df = compute_academic_band_analysis(self.df, 'degree_band')
        self.assertFalse(band_df.empty)
        total_in_bands = band_df['total_students'].sum()
        self.assertEqual(total_in_bands, 215)

    def test_correlations(self):
        """Verifies point-biserial correlations."""
        corr_df = compute_correlations(self.df)
        self.assertFalse(corr_df.empty)
        ssc_row = corr_df[corr_df['Variable'] == '10th (SSC) %']
        self.assertFalse(ssc_row.empty)
        self.assertGreater(ssc_row.iloc[0]['Correlation with Placement (r)'], 0.5)

    def test_pattern_breaks(self):
        """Verifies pattern break thresholds and counts."""
        breaks = identify_pattern_breaks(self.df)
        self.assertGreater(breaks['high_acad_count'], 0)
        self.assertGreater(breaks['low_acad_count'], 0)
        self.assertGreater(breaks['workex_not_placed_count'], 0)
        self.assertGreater(breaks['no_workex_placed_count'], 0)

        # High academic threshold should be 75th percentile (72%)
        self.assertAlmostEqual(breaks['high_acad_threshold'], 72.0, places=1)

    def test_insights_generation(self):
        """Verifies dynamic insight generation formatting."""
        findings = generate_key_findings(self.df)
        self.assertGreaterEqual(len(findings), 3)
        for f in findings:
            self.assertIn('title', f)
            self.assertIn('finding', f)
            self.assertIn('evidence', f)
            self.assertIn('interpretation', f)
            # Ensure non-causal language
            self.assertNotIn("caused placement", f['interpretation'].lower())


if __name__ == '__main__':
    unittest.main()
