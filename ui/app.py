"""
Multi-Agent Medical Diagnosis System - Streamlit UI
Run from project root: streamlit run ui/app.py
"""

import os
import sys
from collections.abc import Iterable

# Fix imports — resolve project root first
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import streamlit as st


def _to_string_list(value):
    """Normalize potentially messy model output into list[str] for display."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, Iterable):
        return [str(item) for item in value if item is not None and str(item).strip()]
    return [str(value)] if str(value).strip() else []

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Medical Multi-Agent System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

    .main-title { font-size: 2.2rem; font-weight: 700; color: #1e3c72; letter-spacing: -0.5px; }
    .subtitle { font-size: 1rem; color: #888; margin-top: 4px; margin-bottom: 24px; }

    .agent-card { background: #f8faff; border: 1px solid #dce8ff; border-radius: 10px; padding: 14px 18px; margin: 8px 0; }
    .agent-card.active { background: #eef4ff; border-color: #1e3c72; border-left: 4px solid #1e3c72; }
    .agent-card.done { background: #f0fff4; border-color: #38a169; border-left: 4px solid #38a169; }

    .urgency-emergency { background:#ffe5e5; color:#c53030; border:2px solid #c53030; padding:12px; border-radius:8px; font-weight:700; font-size:1.1rem; }
    .urgency-urgent { background:#fff3e0; color:#c06000; border:2px solid #e07800; padding:12px; border-radius:8px; font-weight:700; font-size:1.1rem; }
    .urgency-semi-urgent { background:#fffde7; color:#856400; border:2px solid #c8a800; padding:12px; border-radius:8px; font-weight:700; font-size:1.1rem; }
    .urgency-routine { background:#e8f5e9; color:#2e7d32; border:2px solid #38a169; padding:12px; border-radius:8px; font-weight:700; font-size:1.1rem; }

    .diagnosis-card { background:white; border:1px solid #e0e8ff; border-radius:10px; padding:16px; margin:10px 0; }
    .confidence-bar-bg { background:#e0e8f0; border-radius:50px; height:8px; margin:6px 0; }
    .confidence-bar { background:linear-gradient(90deg,#1e3c72,#2a69ac); height:8px; border-radius:50px; }

    .disclaimer-box { background:#fff5f5; border:2px solid #feb2b2; border-radius:10px; padding:16px; color:#742a2a; font-size:0.88rem; margin-top:20px; }
    .source-link { font-family:'IBM Plex Mono',monospace; font-size:0.78rem; color:#2a69ac; }
</style>
""", unsafe_allow_html=True)

# ── Sample Cases ──────────────────────────────────────────────────────────────
SAMPLE_CASES = {
    "Chest Pain (Adult Male)": "I'm a 52-year-old male with sudden chest pain that started 2 hours ago. The pain radiates to my left arm and jaw. I'm sweating and feel nauseous. I take metformin 500mg for type 2 diabetes and lisinopril 10mg for high blood pressure. I'm allergic to aspirin.",
    "Shortness of Breath (Pregnant)": "35-year-old female, 8 months pregnant. Increasing shortness of breath for 3 days, swelling in both legs, persistent cough. I take prenatal vitamins and iron supplements. No known allergies.",
    "Headache & Fever (Child)": "My 8-year-old has had a severe headache for 2 days, high fever (39.5C), stiff neck, and sensitivity to light. They vomited twice this morning. No current medications. Penicillin allergy.",
    "Abdominal Pain (Young Adult)": "22-year-old male, sharp pain in lower right abdomen for 12 hours, started around belly button and moved down. Mild fever, loss of appetite, nausea. No medications. No allergies.",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 Medical Multi-Agent")
    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")

    agents = [
        ("🩺", "Intake Agent",   "Structures patient data"),
        ("🔬", "Research Agent", "Searches PubMed literature"),
        ("💊", "Drug Agent",     "Checks FDA drug data"),
        ("🔍", "Critic Agent",   "Peer reviews analysis"),
        ("📝", "Report Agent",   "Writes final report"),
    ]

    agent_status = st.session_state.get("agent_status", {})
    for icon, name, desc in agents:
        status = agent_status.get(name, "pending")
        css = "agent-card active" if status == "active" else ("agent-card done" if status == "done" else "agent-card")
        ind = "⏳" if status == "active" else ("✅" if status == "done" else "⬜")
        st.markdown(f'<div class="{css}">{ind} <strong>{icon} {name}</strong><br><small style="color:#666">{desc}</small></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Powered by:** Groq (Llama 3.3 70B) + PubMed API + OpenFDA API")
    st.markdown("**⚠️ For educational/demo use only.**")

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🏥 Medical Multi-Agent Diagnostic System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">5 AI agents collaborate · Groq (Llama 3.3 70B) · PubMed · OpenFDA · LangGraph</div>', unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 🧪 Try a Sample Case or Enter Your Own")
sample_choice = st.selectbox("Load a sample case:", ["— Enter manually —"] + list(SAMPLE_CASES.keys()))
default_text = SAMPLE_CASES.get(sample_choice, "") if sample_choice != "— Enter manually —" else ""

patient_input = st.text_area(
    "Patient Description",
    value=default_text,
    height=120,
    placeholder="Describe symptoms, duration, severity, medications, allergies, age, gender...",
)

col1, col2, _ = st.columns([1, 1, 4])
with col1:
    run_btn = st.button("🚀 Run Diagnosis", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ── Run Pipeline ──────────────────────────────────────────────────────────────
if run_btn and patient_input.strip():
    from graph.workflow import run_diagnosis

    st.markdown("---")
    st.markdown("### ⚙️ Running Agent Pipeline...")

    progress_bar = st.progress(0)
    status_text = st.empty()

    agent_names = ["Intake Agent", "Research Agent", "Drug Agent", "Critic Agent", "Report Agent"]
    st.session_state["agent_status"] = {n: "pending" for n in agent_names}

    step_map = {
        "intake":   ("Intake Agent",   20),
        "research": ("Research Agent", 40),
        "drug":     ("Drug Agent",     60),
        "critic":   ("Critic Agent",   80),
        "report":   ("Report Agent",  100),
    }

    def update_progress(step_key, message):
        if step_key in step_map:
            agent_name, pct = step_map[step_key]
            keys = list(step_map.keys())
            idx = keys.index(step_key)
            for i, k in enumerate(keys):
                n = step_map[k][0]
                if i < idx:
                    st.session_state["agent_status"][n] = "done"
                elif i == idx:
                    st.session_state["agent_status"][n] = "active"
            progress_bar.progress(pct)
            status_text.markdown(f"**{message}**")

    with st.spinner(""):
        result = run_diagnosis(patient_input, progress_callback=update_progress)

    for n in agent_names:
        st.session_state["agent_status"][n] = "done"
    progress_bar.progress(100)
    status_text.markdown("**✅ Analysis Complete!**")

    if result.get("error"):
        st.error(f"Error: {result['error']}")
        st.stop()

    st.session_state["result"] = result

elif run_btn and not patient_input.strip():
    st.warning("Please enter a patient description first.")

# ── Display Results ───────────────────────────────────────────────────────────
if "result" in st.session_state:
    result          = st.session_state["result"]
    final_report    = result.get("final_report", {})
    patient_profile = result.get("patient_profile", {})
    research_results= result.get("research_results", {})
    drug_results    = result.get("drug_results", {})
    critic_results  = result.get("critic_results", {})

    st.markdown("---")
    st.markdown("## 📋 Diagnostic Report")

    col_id, col_urg = st.columns([2, 1])
    with col_id:
        st.markdown(f"**Report ID:** `{final_report.get('report_id', 'N/A')}`")
    with col_urg:
        urgency = final_report.get("urgency", "Unknown")
        css_u = urgency.lower().replace(" ", "-")
        st.markdown(f'<div class="urgency-{css_u}">🚨 {urgency.upper()}</div>', unsafe_allow_html=True)

    st.markdown(f"> {final_report.get('executive_summary', '')}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🩺 Patient", "🔬 Diagnoses", "💊 Medications", "🔍 Critic Review", "📝 Full Report"])

    with tab1:
        st.markdown("### Patient Profile")
        symptoms = _to_string_list(patient_profile.get("symptoms"))
        conditions = _to_string_list(patient_profile.get("existing_conditions"))
        medications = _to_string_list(patient_profile.get("current_medications"))
        allergies = _to_string_list(patient_profile.get("allergies"))
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Severity", f"{patient_profile.get('severity', 'N/A')}/10")
            st.markdown(f"**Chief Complaint:** {patient_profile.get('chief_complaint', 'N/A')}")
            st.markdown(f"**Duration:** {patient_profile.get('duration', 'N/A')}")
        with c2:
            st.markdown(f"**Symptoms:** {', '.join(symptoms) or 'None'}")
            st.markdown(f"**Conditions:** {', '.join(conditions) or 'None'}")
            st.markdown(f"**Medications:** {', '.join(medications) or 'None'}")
            st.markdown(f"**Allergies:** {', '.join(allergies) or 'None'}")

    with tab2:
        st.markdown("### Differential Diagnoses")
        st.caption(f"Literature: {research_results.get('literature_summary', 'N/A')}")
        if research_results.get("red_flags"):
            st.warning(f"🚩 Red Flags: {', '.join(research_results['red_flags'])}")

        for dx in final_report.get("final_diagnoses", []):
            conf = dx.get("confidence", 0)
            st.markdown(f"""
            <div class="diagnosis-card">
                <strong>#{dx.get('rank')} {dx.get('condition','Unknown')}</strong> &nbsp; <code>{dx.get('icd10','')}</code>
                <div class="confidence-bar-bg"><div class="confidence-bar" style="width:{conf}%"></div></div>
                <small>Confidence: {conf}%</small>
                <p style="margin:8px 0 4px">{dx.get('reasoning','')}</p>
                <small><strong>Next steps:</strong> {', '.join(dx.get('next_steps',[]))}</small>
            </div>
            """, unsafe_allow_html=True)

        articles = research_results.get("pubmed_articles", [])
        if articles:
            with st.expander("📚 PubMed Sources"):
                for a in articles:
                    st.markdown(f"**{a['title']}** ({a['year']}) — *{a['authors']}*")
                    st.markdown(f"<a class='source-link' href='{a['url']}' target='_blank'>{a['url']}</a>", unsafe_allow_html=True)
                    st.caption(a['abstract'][:300] + "...")
                    st.markdown("---")

    with tab3:
        st.markdown("### Medication Safety")
        st.info(f"**Overall:** {drug_results.get('overall_medication_safety','N/A')}")
        st.markdown(drug_results.get("pharmacist_notes", "No medications to review."))
        for i in drug_results.get("cross_interactions", []):
            sev = {"Severe":"🔴","Moderate":"🟡","Mild":"🟢"}.get(i.get("severity"),"⚪")
            st.markdown(f"{sev} **{i.get('drug_a')} + {i.get('drug_b')}** ({i.get('severity')}): {i.get('interaction')}")
        for c in drug_results.get("contraindications_with_diagnoses", []):
            st.markdown(f"- **{c.get('medication')}** with *{c.get('diagnosis')}*: {c.get('concern')}")

    with tab4:
        st.markdown("### 🔍 Critic Agent Peer Review")
        q = critic_results.get("overall_quality", "N/A")
        qc = {"Excellent":"🟢","Good":"🟢","Acceptable":"🟡","Poor":"🔴"}.get(q,"⚪")
        st.markdown(f"**Quality:** {qc} {q}")
        st.markdown(f"**Verdict:** {critic_results.get('critic_verdict','N/A')}")
        missed = critic_results.get("missed_diagnoses", [])
        if missed:
            st.markdown("#### Diagnoses the Team Missed")
            for m in missed:
                st.markdown(f"- **{m.get('condition')}** ({m.get('likelihood')}): {m.get('reason_it_fits')}")
        for c in critic_results.get("contradictions", []):
            st.markdown(f"⚡ {c}")
        for q2 in critic_results.get("questions_to_investigate", []):
            st.markdown(f"❓ {q2}")

    with tab5:
        st.markdown("#### Immediate Actions")
        for a in final_report.get("recommended_immediate_actions", []):
            st.markdown(f"✅ {a}")
        st.markdown("#### Specialist Referrals")
        for r in final_report.get("specialist_referrals", []):
            st.markdown(f"👨‍⚕️ {r}")
        st.markdown("#### Follow-up")
        st.info(final_report.get("follow_up", "N/A"))
        with st.expander("🔧 Raw JSON"):
            st.json(result)
