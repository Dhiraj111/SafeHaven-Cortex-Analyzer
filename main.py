import streamlit as st
import time
from src.ui.styles import setup_page
from src.backend.database import SnowflakeManager
from src.services.risk_engine import ChaosEngine, StressTester
from src.services.ai_service import get_ai_response, stream_text
from src.services.utils import format_id, calculate_roi
from src.ui.charts import render_map, render_correlation, render_stress_chart

# 1. Setup
setup_page()
db = SnowflakeManager()

# 2. Sidebar Logic
with st.sidebar:
    st.header("⚡ SafeHaven Ops")
    
    # System Status
    with st.container(border=True):
        st.subheader("⚙️ System Status")
        status = db.get_system_status()
        if status:
            st.markdown("🟢 **Live**")
            short_time = str(status).split(" ")[4] if len(str(status).split(" ")) > 4 else "Active"
            st.code(f"v4.0.1 ({short_time})")
        else:
            st.error("⚠️ Model Offline")

    # Chaos Engine
    st.subheader("🚨 Chaos Engine")
    if 'batch_count' not in st.session_state: st.session_state.batch_count = 0
    
    with st.container(border=True):
        scenario = st.selectbox("Market Scenario:", ["📉 Economic Recession", "🏥 Health Crisis", "📈 Market Boom"])
        
        # --- SECURE INJECTION LOGIC STARTS HERE ---
        if st.button("Inject Event Stream", type="primary", use_container_width=True):
            with st.spinner("Streaming PII-cleansed data..."):
                # 1. Get Raw Data Tuples (Secure, not strings)
                v_bank_tuples, v_ins_tuples = ChaosEngine.generate_batch(scenario, st.session_state.batch_count)
                
                # FIX: Use '?' placeholders instead of '%s' for Snowflake compatibility
                sql_bank = "INSERT INTO BANK_DB.DATA.LOAN_CUSTOMERS (email, loan_amnt, term, int_rate, grade, annual_inc, loan_status) VALUES (?, ?, ?, ?, ?, ?, ?)"
                sql_ins = "INSERT INTO INSURER_DB.DATA.MEDICAL_CLIENTS (email, age, bmi, charges, smoker, region) VALUES (?, ?, ?, ?, ?, ?)"

                # 3. Secure Bulk Insert
                if db.bulk_insert(sql_bank, v_bank_tuples) and db.bulk_insert(sql_ins, v_ins_tuples):
                    db.run_command("ALTER DYNAMIC TABLE CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS REFRESH")
                    st.session_state.batch_count += 1
                    st.toast("Data stream processed securely.", icon="🔒")
                    time.sleep(1)
                    st.rerun()
        # --- SECURE INJECTION LOGIC ENDS HERE ---

    if st.button("🗑️ Purge Test Data", use_container_width=True):
         db.run_command("DELETE FROM BANK_DB.DATA.LOAN_CUSTOMERS WHERE EMAIL LIKE 'user_%'")
         db.run_command("DELETE FROM INSURER_DB.DATA.MEDICAL_CLIENTS WHERE EMAIL LIKE 'user_%'")
         db.run_command("ALTER DYNAMIC TABLE CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS REFRESH")
         st.session_state.batch_count = 0
         st.rerun()

# 3. Main Dashboard
st.title("🛡️ SafeHaven Enterprise")
st.markdown("##### Privacy-Safe Financial & Healthcare Risk Enclave")

df_agg = db.get_dashboard_data()
if df_agg.empty:
    st.error("Connection Failed or Data Empty")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 Executive Risk View", "🕵️ Customer Investigator", "🤖 AI Analyst Agent"])

# --- TAB 1: EXECUTIVE ---
with tab1:
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        with c1:
            risk_thresh = st.slider("High Risk Threshold (%)", 0, 50, 25)
        with c2:
            risky_vol = df_agg[df_agg['COST_TO_INCOME_RATIO'] > risk_thresh]['TOTAL_CUSTOMERS'].sum()
            loss, saved = calculate_roi(risky_vol)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("High Risk Volume", f"{risky_vol} / {df_agg['TOTAL_CUSTOMERS'].sum()}")
            m2.metric("Projected Exposure", f"${loss:,.0f}", delta="At Risk", delta_color="inverse")
            m3.metric("Loss Avoided", f"${saved:,.0f}", delta="85% Recovery")

    col_map, col_corr = st.columns([1, 1])
    with col_map:
        st.subheader("📍 Geographic Concentration")
        try:
            df_geo = db.get_geo_data()
            st.plotly_chart(render_map(df_geo), use_container_width=True)
        except: st.warning("Map Unavailable")
    
    with col_corr:
        st.subheader("📈 Risk/Volume Correlation")
        st.plotly_chart(render_correlation(df_agg, risk_thresh), use_container_width=True)

# --- TAB 2: INVESTIGATOR ---
with tab2:
    col_q, col_d = st.columns([1, 3])
    with col_q:
        st.markdown("#### 🔍 Audit Queue")
        df_raw = db.get_audit_queue()
        
        if not df_raw.empty:
            df_raw['label'] = df_raw['EMAIL'].apply(format_id)
            sel_label = st.radio("Flagged Accounts:", df_raw['label'], label_visibility="collapsed")
            user_data = df_raw[df_raw['label'] == sel_label].iloc[0]
        else:
            st.warning("⚠️ Queue Empty")
            user_data = None

    with col_d:
        if user_data is not None:
            with st.container(border=True):
                h1, h2 = st.columns([3, 1])
                h1.subheader(f"Dossier: {format_id(user_data['EMAIL'])}")
                h2.caption("✅ PII Masking Active")
                
                prob = db.predict_risk(
                    int(user_data['ANNUAL_INC']), 
                    int(user_data['AGE']), 
                    float(user_data['BMI']), 
                    float(user_data['CHARGES'])
                )
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Grade", user_data['GRADE'])
                c2.metric("Income", f"${user_data['ANNUAL_INC']:,.0f}")
                c3.metric("Medical", f"${user_data['CHARGES']:,.0f}")
                c4.metric("AI Score", f"{prob:.1%}", delta="Critical" if prob > 0.6 else "Stable", delta_color="inverse" if prob > 0.6 else "normal")

                st.divider()
                st.markdown("**Predictive Stress Test**")
                probs = StressTester.run_simulation(db, user_data)
                st.plotly_chart(render_stress_chart(probs), use_container_width=True)
                
                st.divider()
                b1, b2, b3 = st.columns([1,1,2])
                b1.button("✅ Approve", use_container_width=True)
                b2.button("🚫 Reject", type="primary", use_container_width=True)
                b3.download_button("📄 Export Audit", data=f"Audit: {format_id(user_data['EMAIL'])}", file_name="audit.txt", use_container_width=True)

# --- TAB 3: AI AGENT ---
with tab3:
    st.markdown("#### 🤖 AI Analyst Agent")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "I am connected to the risk ledger. How can I help?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about the risk data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            with st.spinner("Analyzing..."):
                response_text = get_ai_response(db, df_agg, prompt)
            full_resp = stream_text(placeholder, response_text)
            st.session_state.messages.append({"role": "assistant", "content": full_resp})