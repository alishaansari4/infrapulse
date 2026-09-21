import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import io

from core.analytics import silent_gap_index, spend_misalignment_index
from core.ingestion import parse_grievance
from core.ledger import diff_project_impact, SAMPLE_AUDIT_PROJECTS

st.set_page_config(page_title="InfraPulse | DPG Infrastructure Engine", layout="wide")

st.title("🌐 InfraPulse: Bias-Corrected Infrastructure Planning Engine")
st.caption("Track 1: AI for Digital Public Infrastructure & Governance | Digital Public Good")

# Embedded Fallback Datasets (Guarantees zero FileNotFoundError)
EMBEDDED_INDIA_DATA = """district_id,district_name,state,latitude,longitude,population,vulnerability_score,infra_deficit_score,complaint_density,capex_allocated_cr,capex_required_cr
IND_MP_01,Jabalpur,Madhya Pradesh,23.1815,79.9864,2460000,0.38,0.42,88.5,85.0,92.0
IND_MP_02,Mandla,Madhya Pradesh,22.5986,80.3712,1054000,0.84,0.89,4.2,12.0,68.0
IND_MP_03,Dindori,Madhya Pradesh,22.9500,81.0800,704000,0.91,0.94,2.1,8.5,54.0
IND_MP_04,Bhopal,Madhya Pradesh,23.2599,77.4126,2371000,0.32,0.35,94.2,110.0,115.0
IND_BR_01,Patna,Bihar,25.5941,85.1376,5838000,0.45,0.48,76.0,140.0,150.0
IND_BR_02,Kishanganj,Bihar,26.0700,87.9400,1690000,0.86,0.87,6.4,18.0,75.0
IND_CG_01,Bastar,Chhattisgarh,19.1071,81.9535,834000,0.88,0.92,3.8,14.5,80.0
IND_CG_02,Raipur,Chhattisgarh,21.2514,81.6296,2160000,0.36,0.39,82.0,95.0,102.0
IND_MH_01,Gadchiroli,Maharashtra,20.1800,80.0000,1072000,0.82,0.85,5.1,20.0,72.0
IND_MH_02,Nagpur,Maharashtra,21.1458,79.0882,4653000,0.30,0.33,91.0,130.0,135.0"""

EMBEDDED_BRICS_DATA = """district_id,district_name,state,latitude,longitude,population,vulnerability_score,infra_deficit_score,complaint_density,capex_allocated_cr,capex_required_cr
BR_MG_01,Belo Horizonte,Minas Gerais,-19.9167,-43.9345,2520000,0.30,0.34,85.0,75.0,80.0
BR_MG_02,Vale do Jequitinhonha,Minas Gerais,-16.4333,-42.9833,650000,0.89,0.91,3.5,9.0,52.0
BR_MG_03,Montes Claros,Minas Gerais,-16.7350,-43.8617,413000,0.62,0.65,34.0,28.0,40.0
ZA_EC_01,OR Tambo,Eastern Cape,-31.4500,28.7833,1450000,0.92,0.95,4.0,11.0,65.0
ZA_GP_01,Johannesburg,Gauteng,-26.2041,28.0473,5635000,0.35,0.38,92.0,120.0,125.0"""

# Sidebar Navigation
st.sidebar.header("Platform Navigation")
jurisdiction = st.sidebar.selectbox("Active Jurisdiction", ["India (data.gov.in / Bhuvan)", "BRICS Sample (Minas Gerais & Gauteng)"])

@st.cache_data
def get_data(is_india: bool):
    file_target = "data/india_districts.csv" if is_india else "data/brics_sample.csv"
    
    if os.path.exists(file_target):
        df = pd.read_csv(file_target)
    else:
        raw_csv = EMBEDDED_INDIA_DATA if is_india else EMBEDDED_BRICS_DATA
        df = pd.read_csv(io.StringIO(raw_csv))
        
    max_comp = df["complaint_density"].max()
    tot = len(df)
    
    df["silent_gap_index"] = df.apply(
        lambda r: silent_gap_index(r["infra_deficit_score"], r["complaint_density"], max_comp, r["vulnerability_score"]), 
        axis=1
    )
    df["need_rank"] = df["infra_deficit_score"].rank(ascending=False, method="min").astype(int)
    df["spend_rank"] = df["capex_allocated_cr"].rank(ascending=False, method="min").astype(int)
    df["misalignment_index"] = df.apply(
        lambda r: spend_misalignment_index(r["need_rank"], r["spend_rank"], tot), 
        axis=1
    )
    return df

is_india_mode = "India" in jurisdiction
df = get_data(is_india_mode)

tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Silent Gap Map", 
    "📥 Multilingual Ingestion", 
    "📊 Spend-Need Alignment", 
    "📜 Delivery Ledger"
])

# TAB 1: Silent Gap Map
with tab1:
    st.subheader("Objective Satellite Deficit vs. Citizen Feedback Divergence")
    st.markdown("Identifies **Voice Poverty**: Regions where satellite/infrastructure indicators show acute failure, but citizen complaint volume is near-zero.")
    
    fig_map = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        hover_name="district_name",
        hover_data={"vulnerability_score": True, "complaint_density": True, "silent_gap_index": True},
        size="silent_gap_index",
        color="silent_gap_index",
        color_continuous_scale="Reds",
        scope="asia" if is_india_mode else "world",
        title="Voice Poverty & Silent Gap Heatmap"
    )
    if is_india_mode:
        fig_map.update_geos(center=dict(lat=22.5, lon=82.0), projection_scale=4.5)
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.dataframe(
        df[["district_name", "state", "infra_deficit_score", "complaint_density", "silent_gap_index"]]
        .sort_values(by="silent_gap_index", ascending=False)
        .reset_index(drop=True),
        use_container_width=True
    )

# TAB 2: Multilingual Grievance Intake
with tab2:
    st.subheader("Citizen Intake Pipeline with Edge Anonymization")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        complaint_text = st.text_area(
            "Citizen Feedback / Grievance Text (Hindi, Portuguese, or Regional):",
            "हमारे गांव मंडला में पिछले आठ महीने से पानी की मुख्य पाइपलाइन टूटी हुई है, कोई सुनवाई नहीं हो रही। फोन: 9826012345"
        )
        is_anon = st.checkbox("🛡️ Submit Anonymously (Whistleblower Protection / Edge PII Scrubbing)", value=True)
        
        if st.button("Process & Ingest Grievance"):
            with st.spinner("Scrubbing PII locally & extracting structured signals via Gemini..."):
                try:
                    result = parse_grievance(complaint_text, is_anonymous=is_anon)
                    st.success("Grievance Successfully Ingested & Anonymized!")
                    st.json(result)
                except Exception as e:
                    st.error(f"Processing error: {e}")
                    
    with col2:
        st.info(
            "**Digital Public Good (DPG) Privacy-by-Design:**\n\n"
            "- PII (phones, Aadhaar, email) is stripped via local regex prior to API transfer.\n"
            "- Whistleblower mode mints non-reversible SHA-256 tokens.\n"
            "- Fulfills DPGA Indicator 8 (Data Minimization & Do No Harm)."
        )

# TAB 3: Spend-Need Matrix
with tab3:
    st.subheader("Public Investment Misalignment Matrix")
    st.markdown("Cross-references need against public expenditure to flag underfunded regions.")
    
    fig_scatter = px.scatter(
        df,
        x="infra_deficit_score",
        y="capex_allocated_cr",
        size="population",
        color="misalignment_index",
        color_continuous_scale="RdYlGn_r",
        text="district_name",
        labels={"infra_deficit_score": "Infrastructure Deficit (Need)", "capex_allocated_cr": "Allocated Budget (₹ Cr)"},
        title="Fiscal Allocation vs. Empirical Need"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# TAB 4: Delivery Ledger
with tab4:
    st.subheader("Closed-Loop Impact Measurement Ledger")
    st.markdown("Verifies whether completed infrastructure works actually reduced citizen grievances and satellite deficits.")
    
    chosen_prj = st.selectbox(
        "Select Completed Government Project to Audit", 
        list(SAMPLE_AUDIT_PROJECTS.keys()), 
        format_func=lambda k: f"{k}: {SAMPLE_AUDIT_PROJECTS[k]['title']}"
    )
    
    audit_data = diff_project_impact(chosen_prj)
    
    if audit_data:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Complaint Drop", f"-{audit_data['complaint_reduction_pct']}%")
        m2.metric("Deficit Reduction", f"-{audit_data['deficit_reduction_pct']}%")
        m3.metric("Grid Access Gain", f"+{audit_data['grid_gain_pct']}%")
        m4.metric("Integrity Score", f"{audit_data['delivery_integrity_score']}/100")
        
        st.success(f"Audit Status: {audit_data['status']}")
