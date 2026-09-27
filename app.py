"""
Student Performance & Placement Analytics Dashboard
Built with Streamlit, Pandas, and Plotly.
Investigating factors associated with student placement outcomes.
"""

import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_data
from src.analysis import (
    compute_kpis,
    compute_academic_band_analysis,
    compute_group_metrics,
    compute_interaction_breakdown,
    compute_correlations,
    identify_pattern_breaks
)
from src.insights import generate_key_findings

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Performance & Placement Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CUSTOM CSS STYLING
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Typography & Spacing */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    
    /* Header Container */
    .header-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 24px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        color: #FFFFFF;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-box h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #FFFFFF !important;
    }
    .header-box p {
        margin: 8px 0 0 0;
        font-size: 1.05rem;
        color: #94A3B8;
    }
    .badge-bar {
        margin-top: 12px;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    .badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.12);
        color: #E2E8F0;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    /* KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 4px;
    }

    /* Section Headers */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 28px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-subtitle {
        font-size: 0.9rem;
        color: #64748B;
        margin-bottom: 18px;
    }

    /* Pattern Break Cards */
    .exception-card {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        border-radius: 0 8px 8px 0;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .exception-card.alert {
        border-left-color: #EF4444;
        background: #FEF2F2;
    }
    .exception-card.success {
        border-left-color: #10B981;
        background: #F0FDF4;
    }
    .exception-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 2px;
    }
    .exception-body {
        font-size: 0.84rem;
        color: #334155;
    }

    /* Insight Card */
    .insight-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .insight-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 8px;
    }
    .insight-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #475569;
        margin-top: 6px;
        margin-bottom: 2px;
    }
    .insight-text {
        font-size: 0.88rem;
        color: #1E293B;
        line-height: 1.45;
        margin-bottom: 8px;
    }
    .insight-interp {
        font-size: 0.86rem;
        color: #475569;
        line-height: 1.45;
        background: #F1F5F9;
        padding: 10px 12px;
        border-radius: 6px;
        border-left: 3px solid #64748B;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# DATA LOADING & SESSION STATE
# -----------------------------------------------------------------------------
@st.cache_data
def get_cached_dataset():
    return load_data()

raw_df = get_cached_dataset()

# Helper for resetting filters
def reset_filter_state():
    st.session_state['sel_degree_type'] = []
    st.session_state['sel_gender'] = []
    st.session_state['sel_status'] = []
    st.session_state['sel_workex'] = []
    st.session_state['sel_specialisation'] = []
    st.session_state['sel_degree_range'] = (float(raw_df['degree_percentage'].min()), float(raw_df['degree_percentage'].max()))

# Initialize state keys if absent
if 'sel_degree_type' not in st.session_state:
    st.session_state['sel_degree_type'] = []
if 'sel_gender' not in st.session_state:
    st.session_state['sel_gender'] = []
if 'sel_status' not in st.session_state:
    st.session_state['sel_status'] = []
if 'sel_workex' not in st.session_state:
    st.session_state['sel_workex'] = []
if 'sel_specialisation' not in st.session_state:
    st.session_state['sel_specialisation'] = []
if 'sel_degree_range' not in st.session_state:
    st.session_state['sel_degree_range'] = (float(raw_df['degree_percentage'].min()), float(raw_df['degree_percentage'].max()))


# -----------------------------------------------------------------------------
# SIDEBAR: INTERACTIVE FILTERS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔍 Filter Cohort")
    st.caption("Customize dataset dimensions. All charts and KPIs update in real-time.")

    # Reset button
    if st.button("↺ Reset All Filters", use_container_width=True):
        reset_filter_state()
        st.rerun()

    st.markdown("---")

    # Filter 1: Undergraduate Degree Field
    degree_options = sorted(raw_df['degree_type_label'].dropna().unique().tolist())
    sel_degree = st.multiselect(
        "Undergraduate Degree Stream",
        options=degree_options,
        default=st.session_state['sel_degree_type'],
        key='sel_degree_type',
        placeholder="All Degree Streams"
    )

    # Filter 2: Work Experience
    workex_options = sorted(raw_df['work_experience'].dropna().unique().tolist())
    sel_workex = st.multiselect(
        "Prior Work Experience",
        options=workex_options,
        default=st.session_state['sel_workex'],
        key='sel_workex',
        placeholder="All Candidates (Yes / No)"
    )

    # Filter 3: MBA Specialisation
    spec_options = sorted(raw_df['mba_specialisation_label'].dropna().unique().tolist())
    sel_spec = st.multiselect(
        "MBA Specialisation",
        options=spec_options,
        default=st.session_state['sel_specialisation'],
        key='sel_specialisation',
        placeholder="All Specialisations"
    )

    # Filter 4: Gender
    gender_options = sorted(raw_df['gender_label'].dropna().unique().tolist())
    sel_gender = st.multiselect(
        "Gender",
        options=gender_options,
        default=st.session_state['sel_gender'],
        key='sel_gender',
        placeholder="All Genders"
    )

    # Filter 5: Placement Outcome
    status_options = sorted(raw_df['placement_status'].dropna().unique().tolist())
    sel_status = st.multiselect(
        "Placement Outcome",
        options=status_options,
        default=st.session_state['sel_status'],
        key='sel_status',
        placeholder="All Outcomes (Placed & Unplaced)"
    )

    # Filter 6: Degree Score Range
    min_deg = float(raw_df['degree_percentage'].min())
    max_deg = float(raw_df['degree_percentage'].max())
    sel_range = st.slider(
        "Degree Percentage Range (%)",
        min_value=min_deg,
        max_value=max_deg,
        value=st.session_state['sel_degree_range'],
        step=1.0,
        key='sel_degree_range'
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.75rem; color:#64748B; line-height:1.4;">
        <strong>Dataset Provenance:</strong><br>
        Campus Recruitment Records, Jain University Bangalore (CC0 Public Domain via Kaggle).
        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------------------------------------------------------
# APPLY FILTERS
# -----------------------------------------------------------------------------
filtered_df = raw_df.copy()

if sel_degree:
    filtered_df = filtered_df[filtered_df['degree_type_label'].isin(sel_degree)]
if sel_workex:
    filtered_df = filtered_df[filtered_df['work_experience'].isin(sel_workex)]
if sel_spec:
    filtered_df = filtered_df[filtered_df['mba_specialisation_label'].isin(sel_spec)]
if sel_gender:
    filtered_df = filtered_df[filtered_df['gender_label'].isin(sel_gender)]
if sel_status:
    filtered_df = filtered_df[filtered_df['placement_status'].isin(sel_status)]

filtered_df = filtered_df[
    (filtered_df['degree_percentage'] >= sel_range[0]) &
    (filtered_df['degree_percentage'] <= sel_range[1])
]


# -----------------------------------------------------------------------------
# DASHBOARD HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <h1>Student Performance & Placement Analytics</h1>
    <p>Exploring the factors associated with student placement outcomes and discovering where patterns break</p>
    <div class="badge-bar">
        <span class="badge">📊 Empirical Cohort: Jain University</span>
        <span class="badge">⚖️ Association ≠ Causation</span>
        <span class="badge">🎯 Transparent Statistical Thresholds</span>
        <span class="badge">💼 Real Placements & Salary Packages</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Filter cohort status pill
col_status1, col_status2 = st.columns([3, 1])
with col_status1:
    st.markdown(
        f"**Active Cohort:** Displaying **{len(filtered_df):,}** of **{len(raw_df):,}** total students "
        f"({(len(filtered_df)/len(raw_df)*100):.1f}% of institutional dataset)"
    )
with col_status2:
    if len(filtered_df) < len(raw_df):
        st.caption("⚡ Filters currently applied")
    else:
        st.caption("✓ Full baseline dataset active")


# Guard: Check for empty filter result
if len(filtered_df) == 0:
    st.warning("⚠️ No students match your selected filter criteria. Please adjust or reset filters in the sidebar.")
    st.stop()


# -----------------------------------------------------------------------------
# SECTION A: EXECUTIVE OVERVIEW (KPIs)
# -----------------------------------------------------------------------------
kpis = compute_kpis(filtered_df)

st.markdown('<div class="section-title">📌 Executive Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">High-level placement indicators for the active student cohort</div>', unsafe_allow_html=True)

kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)

with kpi_c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Students</div>
        <div class="kpi-value">{kpis['total_students']:,}</div>
        <div class="kpi-subtext">Active cohort sample</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Placed Students</div>
        <div class="kpi-value" style="color: #059669;">{kpis['placed_students']:,}</div>
        <div class="kpi-subtext">{kpis['unplaced_students']:,} not placed</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Placement Rate</div>
        <div class="kpi-value" style="color: #2563EB;">{kpis['placement_rate']:.1f}%</div>
        <div class="kpi-subtext">Placed / Total cohort</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c4:
    if kpis['avg_salary'] is not None:
        salary_text = f"₹{kpis['avg_salary']:,.0f}"
        sub_text = f"Median: ₹{kpis['median_salary']:,.0f}"
    else:
        salary_text = "N/A"
        sub_text = "No placed offers in slice"

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Average Package</div>
        <div class="kpi-value">{salary_text}</div>
        <div class="kpi-subtext">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Work Experience</div>
        <div class="kpi-value">{kpis['workex_pct']:.1f}%</div>
        <div class="kpi-subtext">{kpis['students_with_workex']:,} students with experience</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SECTION B: ACADEMIC PERFORMANCE ANALYSIS
# -----------------------------------------------------------------------------
st.markdown('<div class="section-title">🎓 Academic Performance Associations</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">'
    'Evaluating how secondary education, higher secondary, undergraduate degree, and MBA performance relate to placement'
    '</div>',
    unsafe_allow_html=True
)

tab_acad1, tab_acad2 = st.tabs(["📊 Performance Bands & Distributions", "📈 Statistical Correlation Matrix"])

with tab_acad1:
    ac_col1, ac_col2 = st.columns([1, 1])

    with ac_col1:
        # Degree band placement rate bar chart
        deg_band_df = compute_academic_band_analysis(filtered_df, 'degree_band')
        if not deg_band_df.empty:
            fig_band = px.bar(
                deg_band_df,
                x='degree_band',
                y='placement_rate',
                text=deg_band_df['placement_rate'].apply(lambda v: f"{v:.1f}%"),
                custom_data=['total_students', 'placed_students', 'placement_rate'],
                color='placement_rate',
                color_continuous_scale=['#93C5FD', '#1E40AF'],
                labels={'degree_band': 'Degree Performance Band', 'placement_rate': 'Placement Rate (%)'},
                title="Placement Rate by Undergraduate Degree Band",
                category_orders={'degree_band': ['<60% (Pass / Low)', '60–70% (First Class)', '70–80% (Distinction)', '80%+ (High Distinction)']}
            )
            fig_band.update_traces(
                hovertemplate="<b>Degree Band:</b> %{x}<br><b>Total Students:</b> %{customdata[0]}<br><b>Placed:</b> %{customdata[1]}<br><b>Placement Rate:</b> %{customdata[2]:.1f}%<extra></extra>",
                textposition='outside'
            )
            fig_band.update_layout(
                yaxis=dict(range=[0, 115], title="Placement Rate (%)"),
                xaxis=dict(title=""),
                coloraxis_showscale=False,
                margin=dict(t=60, b=20, l=40, r=20),
                height=390
            )
            st.plotly_chart(fig_band, use_container_width=True)
        else:
            st.info("Insufficient band data in this filtered slice.")

    with ac_col2:
        # Box plot comparing distributions across milestones for Placed vs Not Placed
        academic_scores = []
        for row_idx, row in filtered_df.iterrows():
            academic_scores.append({'Milestone': '10th (SSC)', 'Percentage': row['ssc_percentage'], 'Outcome': row['placement_status']})
            academic_scores.append({'Milestone': '12th (HSC)', 'Percentage': row['hsc_percentage'], 'Outcome': row['placement_status']})
            academic_scores.append({'Milestone': 'Degree', 'Percentage': row['degree_percentage'], 'Outcome': row['placement_status']})
            academic_scores.append({'Milestone': 'Employability', 'Percentage': row['employability_score'], 'Outcome': row['placement_status']})
            academic_scores.append({'Milestone': 'MBA', 'Percentage': row['mba_percentage'], 'Outcome': row['placement_status']})

        dist_df = pd.DataFrame(academic_scores)
        fig_dist = px.box(
            dist_df,
            x='Milestone',
            y='Percentage',
            color='Outcome',
            color_discrete_map={'Placed': '#059669', 'Not Placed': '#DC2626'},
            title="Score Distribution across Academic Milestones",
            category_orders={'Milestone': ['10th (SSC)', '12th (HSC)', 'Degree', 'Employability', 'MBA']}
        )
        fig_dist.update_layout(
            yaxis=dict(title="Score Percentage (%)"),
            xaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, title=""),
            margin=dict(t=65, b=20, l=40, r=20),
            height=390
        )
        st.plotly_chart(fig_dist, use_container_width=True)

with tab_acad2:
    corr_df = compute_correlations(filtered_df)
    if not corr_df.empty:
        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.markdown("##### Point-Biserial Correlations with Placement Outcome")
            try:
                styled_corr = corr_df.style.background_gradient(subset=['Correlation with Placement (r)'], cmap='Blues')
            except (ImportError, ModuleNotFoundError):
                styled_corr = corr_df
            st.dataframe(
                styled_corr,
                use_container_width=True,
                hide_index=True
            )
        with c_right:
            st.markdown("##### Key Takeaway")
            st.markdown(
                r"""
                - **Early Academics (10th/SSC & 12th/HSC)** show the strongest positive linear association with placement in this cohort (\(r > 0.49\)).
                - **Degree Percentage** also demonstrates substantial positive association (\(r \approx 0.48\)).
                - **MBA Score (\(r \approx 0.08\)) and Employability Test (\(r \approx 0.13\))** have much weaker linear correlations with final placement status.
                """
            )
    else:
        st.info("Correlation analysis requires at least 5 observations with placement outcomes.")


# -----------------------------------------------------------------------------
# SECTION C: EXPERIENCE & SKILLS ANALYSIS
# -----------------------------------------------------------------------------
st.markdown('<div class="section-title">💼 Experience & Candidate Attributes</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">'
    'Analyzing prior work experience and field specialisation associations with placement and salary packages'
    '</div>',
    unsafe_allow_html=True
)

exp_col1, exp_col2 = st.columns(2)

with exp_col1:
    # Work Experience Placement Comparison
    workex_df = compute_group_metrics(filtered_df, 'work_experience')
    if not workex_df.empty:
        fig_workex = px.bar(
            workex_df,
            x='work_experience',
            y='placement_rate',
            text=workex_df['placement_rate'].apply(lambda v: f"{v:.1f}%"),
            custom_data=['total_students', 'placed_students', 'placement_rate'],
            color='work_experience',
            color_discrete_map={'Yes': '#2563EB', 'No': '#94A3B8'},
            title="Placement Rate by Prior Work Experience"
        )
        fig_workex.update_traces(
            hovertemplate="<b>Prior Experience:</b> %{x}<br><b>Total Students:</b> %{customdata[0]}<br><b>Placed:</b> %{customdata[1]}<br><b>Placement Rate:</b> %{customdata[2]:.1f}%<extra></extra>",
            textposition='outside'
        )
        fig_workex.update_layout(
            yaxis=dict(range=[0, 105], title="Placement Rate (%)"),
            xaxis=dict(title="Prior Work Experience"),
            showlegend=False,
            margin=dict(t=50, b=20, l=40, r=20),
            height=370
        )
        st.plotly_chart(fig_workex, use_container_width=True)

with exp_col2:
    # Salary vs Work Experience (Placed students only)
    placed_subset = filtered_df[filtered_df['is_placed'] == 1].dropna(subset=['salary'])
    if not placed_subset.empty:
        fig_salary = px.box(
            placed_subset,
            x='work_experience',
            y='salary',
            color='work_experience',
            color_discrete_map={'Yes': '#2563EB', 'No': '#94A3B8'},
            title="Salary Package Distribution by Prior Work Experience (Placed Only)",
            points='all'
        )
        fig_salary.update_layout(
            yaxis=dict(title="Salary Package (INR)"),
            xaxis=dict(title="Prior Work Experience"),
            showlegend=False,
            margin=dict(t=50, b=20, l=40, r=20),
            height=370
        )
        st.plotly_chart(fig_salary, use_container_width=True)
    else:
        st.info("No salary information available for the currently filtered placed students.")


# -----------------------------------------------------------------------------
# SECTION D: MULTI-DIMENSIONAL BREAKDOWNS
# -----------------------------------------------------------------------------
st.markdown('<div class="section-title">🔬 Multi-Dimensional Subgroup Breakdowns</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">'
    'Testing whether associations remain consistent across subgroups (Degree field, MBA Specialisation, and Academic Tiers)'
    '</div>',
    unsafe_allow_html=True
)

bk_col1, bk_col2 = st.columns(2)

with bk_col1:
    # Interaction: Academic Tier + Work Experience
    # Creates simple median split for robust interaction visualization
    df_interact = filtered_df.copy()
    if 'degree_percentage' in df_interact.columns and 'work_experience' in df_interact.columns:
        med_val = df_interact['degree_percentage'].median()
        df_interact['academic_tier'] = np.where(
            df_interact['degree_percentage'] >= med_val,
            f'Top Half (≥ {med_val:.0f}%)',
            f'Lower Half (< {med_val:.0f}%)'
        )
        inter_df = compute_interaction_breakdown(df_interact, 'academic_tier', 'work_experience')
        if not inter_df.empty:
            fig_inter = px.bar(
                inter_df,
                x='academic_tier',
                y='placement_rate',
                color='work_experience',
                barmode='group',
                text=inter_df['placement_rate'].apply(lambda v: f"{v:.1f}%"),
                custom_data=['total_students', 'placed_students'],
                color_discrete_map={'Yes': '#1D4ED8', 'No': '#93C5FD'},
                title="Interaction: Academic Tier × Work Experience on Placement Rate"
            )
            fig_inter.update_traces(
                hovertemplate="<b>Academic Tier:</b> %{x}<br><b>Work Experience:</b> %{data.name}<br><b>Placed:</b> %{customdata[1]}/%{customdata[0]}<br><b>Rate:</b> %{y:.1f}%<extra></extra>",
                textposition='outside'
            )
            fig_inter.update_layout(
                yaxis=dict(range=[0, 115], title="Placement Rate (%)"),
                xaxis=dict(title="Academic Tier"),
                legend=dict(title="Work Experience"),
                margin=dict(t=50, b=20, l=40, r=20),
                height=380
            )
            st.plotly_chart(fig_inter, use_container_width=True)

with bk_col2:
    # Specialisation × Degree Discipline Breakdown
    spec_deg_df = compute_interaction_breakdown(filtered_df, 'mba_specialisation_label', 'degree_type_label')
    if not spec_deg_df.empty:
        fig_spec = px.bar(
            spec_deg_df,
            x='mba_specialisation_label',
            y='placement_rate',
            color='degree_type_label',
            barmode='group',
            text=spec_deg_df['placement_rate'].apply(lambda v: f"{v:.0f}%"),
            custom_data=['total_students', 'placed_students'],
            color_discrete_sequence=['#0284C7', '#0D9488', '#F59E0B'],
            title="Placement Rate by MBA Specialisation & Degree Stream"
        )
        fig_spec.update_traces(
            hovertemplate="<b>Specialisation:</b> %{x}<br><b>Stream:</b> %{data.name}<br><b>Placed:</b> %{customdata[1]}/%{customdata[0]}<br><b>Rate:</b> %{y:.1f}%<extra></extra>",
            textposition='outside'
        )
        fig_spec.update_layout(
            yaxis=dict(range=[0, 115], title="Placement Rate (%)"),
            xaxis=dict(title="MBA Specialisation"),
            legend=dict(title="Degree Stream"),
            margin=dict(t=50, b=20, l=40, r=20),
            height=380
        )
        st.plotly_chart(fig_spec, use_container_width=True)


# -----------------------------------------------------------------------------
# SECTION E: EXCEPTIONS & PATTERN BREAKS (REQUIRED)
# -----------------------------------------------------------------------------
st.markdown('<div class="section-title">⚡ Pattern Breaks & Exception Analysis</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">'
    'Identifying and analyzing observations where the general positive academic or experience patterns did not hold'
    '</div>',
    unsafe_allow_html=True
)

breaks = identify_pattern_breaks(filtered_df)

ex_c1, ex_c2, ex_c3, ex_c4 = st.columns(4)

with ex_c1:
    st.markdown(f"""
    <div class="exception-card alert">
        <div class="exception-title">High Academic & Unplaced</div>
        <div class="kpi-value" style="font-size: 1.5rem; color: #DC2626;">{breaks['high_acad_count']}</div>
        <div class="exception-body">Degree ≥ {breaks['high_acad_threshold']}% (Top Quartile) but NOT placed</div>
    </div>
    """, unsafe_allow_html=True)

with ex_c2:
    st.markdown(f"""
    <div class="exception-card success">
        <div class="exception-title">Lower Academic & Placed</div>
        <div class="kpi-value" style="font-size: 1.5rem; color: #059669;">{breaks['low_acad_count']}</div>
        <div class="exception-body">Degree < {breaks['low_acad_threshold']}% (Below Median) but PLACED</div>
    </div>
    """, unsafe_allow_html=True)

with ex_c3:
    st.markdown(f"""
    <div class="exception-card alert">
        <div class="exception-title">Experience & Unplaced</div>
        <div class="kpi-value" style="font-size: 1.5rem; color: #D97706;">{breaks['workex_not_placed_count']}</div>
        <div class="exception-body">Had prior work experience but were NOT placed</div>
    </div>
    """, unsafe_allow_html=True)

with ex_c4:
    st.markdown(f"""
    <div class="exception-card success">
        <div class="exception-title">No Experience & Placed</div>
        <div class="kpi-value" style="font-size: 1.5rem; color: #2563EB;">{breaks['no_workex_placed_count']}</div>
        <div class="exception-body">Zero prior work experience yet successfully PLACED</div>
    </div>
    """, unsafe_allow_html=True)

# Exception Drilldown Explorer
with st.expander("🔍 Deep-Dive: Inspect Individual Student Exception Records", expanded=False):
    exc_tab1, exc_tab2, exc_tab3 = st.tabs([
        f"High Academic + Unplaced ({breaks['high_acad_count']})",
        f"Lower Academic + Placed ({breaks['low_acad_count']})",
        f"Work Experience + Unplaced ({breaks['workex_not_placed_count']})"
    ])

    display_cols = [
        'student_id', 'degree_percentage', 'work_experience', 'employability_score',
        'mba_specialisation_label', 'mba_percentage', 'placement_status'
    ]

    with exc_tab1:
        st.markdown(
            f"**Cohort Context:** These {breaks['high_acad_count']} students achieved top-quartile undergraduate degree "
            f"marks (≥ {breaks['high_acad_threshold']}%), yet did not receive an on-campus placement offer. "
            f"Notice that **{len(breaks['high_acad_not_placed'][breaks['high_acad_not_placed']['work_experience'] == 'No'])} "
            f"of these {breaks['high_acad_count']} students had zero prior work experience**."
        )
        if not breaks['high_acad_not_placed'].empty:
            st.dataframe(
                breaks['high_acad_not_placed'][display_cols],
                use_container_width=True,
                hide_index=True
            )

    with exc_tab2:
        st.markdown(
            f"**Cohort Context:** These {breaks['low_acad_count']} students scored below the median degree score "
            f"(< {breaks['low_acad_threshold']}%), yet successfully secured placement offers. "
            f"Many compensated through prior work experience or strong performance in interviews and aptitude."
        )
        if not breaks['low_acad_placed'].empty:
            st.dataframe(
                breaks['low_acad_placed'][display_cols],
                use_container_width=True,
                hide_index=True
            )

    with exc_tab3:
        st.markdown(
            f"**Cohort Context:** While work experience provided a +26.9 percentage point overall lift in placement rate, "
            f"these {breaks['workex_not_placed_count']} experienced candidates were still not placed, demonstrating that experience "
            f"is not a deterministic guarantee of placement."
        )
        if not breaks['workex_not_placed'].empty:
            st.dataframe(
                breaks['workex_not_placed'][display_cols],
                use_container_width=True,
                hide_index=True
            )


# -----------------------------------------------------------------------------
# SECTION F: KEY FINDINGS & EXECUTIVE INSIGHTS
# -----------------------------------------------------------------------------
st.markdown('<div class="section-title">💡 Evidence-Based Key Findings</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">'
    'Synthesized empirical findings strictly adhering to non-causal analytical interpretation'
    '</div>',
    unsafe_allow_html=True
)

findings = generate_key_findings(filtered_df)

for f in findings:
    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">{f['title']}</div>
        <div class="insight-label">Observed Finding:</div>
        <div class="insight-text"><strong>{f['finding']}</strong></div>
        <div class="insight-label">Empirical Evidence:</div>
        <div class="insight-text">{f['evidence']}</div>
        <div class="insight-label">Analytical Interpretation:</div>
        <div class="insight-interp">{f['interpretation']}</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# FOOTER & METHODOLOGY NOTE
# -----------------------------------------------------------------------------
st.markdown("---")
with st.expander("ℹ️ Analytical Methodology, Data Provenance & Study Limitations"):
    st.markdown("""
    ### Methodology & Analytical Framework
    - **Causality vs. Association:** All patterns presented represent statistical associations in observational institutional recruitment data. We make **no causal claims** (e.g., having work experience does not directly cause an offer; it is associated with a higher observed rate).
    - **Data Source:** Campus Recruitment Dataset from Jain University, Bangalore (collected by Ben Roshan, published under CC0: Public Domain on Kaggle).
    - **Sample Attributes:** 215 students, 148 placed, 67 unplaced. Salaries are documented exclusively for placed students.
    - **Threshold Definition:** Exception thresholds are derived transparently from sample distribution quantiles (75th percentile for high academic tier, 50th percentile/median for lower tier).
    - **Sampling Limitations:** The dataset originates from a single management institution during a specific placement cycle and may not generalize across all institutions, geography, or industry sectors.
    """)
