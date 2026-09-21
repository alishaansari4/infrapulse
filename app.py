import streamlit as st
import pandas as pd
import plotly.express as px
from core.analytics import silent_gap_index, spend_misalignment_index
from core.ingestion import parse_grievance
from core.ledger import diff_project_impact, SAMPLE_AUDIT_PROJECTS

st.set_page_config(page_title="InfraPulse | DPG Infrastructure Engine", layout="wide")

st.title("🌐 InfraPulse: Bias-Corrected Infrastructure Planning Engine")
st.caption("Track 1: AI for Digital Public Infrastructure & Governance | Digital Public Good")

# Top-level jurisdiction switcher (Fulfills BRICS modularity)
st.sidebar.header("Platform Navigation")
jurisdiction = st.sidebar.selectbox("Active Jurisdiction", ["India (data.gov.in / Bhuvan)", "BRICS Sample (Minas Gerais & Gauteng)"])

data_path = "data/india_districts.csv" if "India" in jurisdiction else "data/brics_sample.csv"

@st.cache_data
def get_data(path: str):
    df = pd.read_csv(path)
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

df = get_data(data_path)

tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Silent Gap Map", 
    "📥 Multilingual Ingestion", 
    "📊 Spend-Need Alignment", 
    "📜 Delivery Ledger"
])

# TAB 1: Silent Gap Map
with tab1:
    st.subheader("Objective Satellite Deficit vs. Citizen Feedback Divergence")
    st.markdown("Identifies **Voice Poverty**: Regions where satellite/infrastructure indicators show acute failure, but complaint volume is near-zero.")
    
    fig_map = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        hover_name="district_name",
        hover_data={"vulnerability_score": True, "complaint_density": True, "silent_gap_index": True},
        size="silent_gap_index",
        color="silent_gap_index",
        color_continuous_scale="Reds",
        scope="asia" if "India" in jurisdiction else "world",
        title="Voice Poverty & Silent Gap Heatmap"
    )
    if "India" in jurisdiction:
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
                    st.error(f"Execution notice: {e}")
                    st.info("Demonstrating offline fallback schema...")
                    st.json({
                        "category": "Water & Sanitation",
                        "urgency_level": "Critical",
                        "location_named": "Mandla",
                        "issue_summary": "Main water pipeline broken for 8 months with zero administrative response.",
                        "detected_language": "Hindi",
                        "tracking_token": "ANON-9A74E82F",
                        "privacy_tier": "Zero-Knowledge Whistleblower Mode (Edge Scrubbed)"
                    })
                    
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
    
    chosen_prj = st.selectbox("Select Completed Government Project to Audit", list(SAMPLE_AUDIT_PROJECTS.keys()), format_func=lambda k: f"{k}: {SAMPLE_AUDIT_PROJECTS[k]['title']}")
    
    audit_data = diff_project_impact(chosen_prj)
    
    if audit_data:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Complaint Drop", f"-{audit_data['complaint_reduction_pct']}%")
        m2.metric("Deficit Reduction", f"-{audit_data['deficit_reduction_pct']}%")
        m3.metric("Grid Access Gain", f"+{audit_data['grid_gain_pct']}%")
        m4.metric("Integrity Score", f"{audit_data['delivery_integrity_score']}/100")
        
        st.success(f"Audit Status: {audit_data['status']}")
