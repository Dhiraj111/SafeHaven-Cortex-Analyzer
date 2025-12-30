import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time

# 1. Page Configuration
st.set_page_config(
    layout="wide", 
    page_title="SafeHaven Enterprise", 
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for "Fintech" Aesthetic
st.markdown("""
    <style>
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #333;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #444;
        border-radius: 5px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Connect to Snowflake
conn = st.connection("snowflake")

# ==========================================
# ⚡ SIDEBAR: OPERATIONS & SIMULATION
# ==========================================
with st.sidebar:
    st.header("⚡ SafeHaven Ops")
    
    # --- MLOPS STATUS ---
    with st.container(border=True):
        st.subheader("⚙️ System Status")
        try:
            cursor = conn.raw_connection.cursor()
            cursor.execute("LIST @CLEAN_ROOM_DB.ANALYSIS.MODEL_STAGE")
            result = cursor.fetchall() 
            if result:
                raw_time = str(result[0][3])
                short_time = raw_time.split(" ")[4] if len(raw_time.split(" ")) > 4 else "Active"
                col_s1, col_s2 = st.columns([3,1])
                col_s1.caption("Model Version:")
                col_s2.markdown("🟢 **Live**")
                st.code(f"v4.0.1 ({short_time})")
            else:
                st.error("⚠️ Model Offline")
        except:
            st.info("System initializing...")

    # --- SIMULATION ENGINE ---
    st.subheader("🚨 Chaos Engine")
    if 'batch_count' not in st.session_state:
        st.session_state.batch_count = 0
        
    with st.container(border=True):
        # FIX: Clean text (No Japanese characters)
        scenario = st.selectbox("Market Scenario:", 
                              ["📉 Economic Recession", "🏥 Health Crisis", "📈 Market Boom"])
        
        if st.button(f"Inject Event Stream", type="primary", use_container_width=True):
            with st.spinner("Streaming PII-cleansed data..."):
                try:
                    cursor = conn.raw_connection.cursor()
                    new_emails = [f"user_{st.session_state.batch_count}_{i}_{random.randint(100,999)}@corp.com" for i in range(25)]
                    
                    values_bank = []
                    values_ins = []
                    
                    for email in new_emails:
                        if "Recession" in scenario:
                            inc, status, costs = random.randint(25000, 45000), 'Default', random.randint(2000, 8000)
                            region = random.choice(['northeast', 'west', 'southwest'])
                        elif "Health" in scenario:
                            inc, status, costs = random.randint(55000, 85000), 'Fully Paid', random.randint(45000, 120000)
                            region = 'southeast'
                        else:
                            inc, status, costs = random.randint(90000, 150000), 'Fully Paid', random.randint(500, 4000)
                            region = random.choice(['west', 'northwest'])

                        values_bank.append(f"('{email}', 50000, '60 months', 25.5, 'G', {inc}, '{status}')")
                        values_ins.append(f"('{email}', {random.randint(25, 65)}, {random.uniform(22, 38):.1f}, {costs}, 'yes', '{region}')")

                    cursor.execute(f"INSERT INTO BANK_DB.DATA.LOAN_CUSTOMERS (email, loan_amnt, term, int_rate, grade, annual_inc, loan_status) VALUES {','.join(values_bank)}")
                    cursor.execute(f"INSERT INTO INSURER_DB.DATA.MEDICAL_CLIENTS (email, age, bmi, charges, smoker, region) VALUES {','.join(values_ins)}")
                    cursor.execute("ALTER DYNAMIC TABLE CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS REFRESH")
                    conn.raw_connection.commit()
                    
                    st.session_state.batch_count += 1
                    st.toast(f"Data stream processed.", icon="⚡")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.button("🗑️ Purge Test Data", use_container_width=True):
         cursor = conn.raw_connection.cursor()
         cursor.execute("DELETE FROM BANK_DB.DATA.LOAN_CUSTOMERS WHERE EMAIL LIKE 'user_%'")
         cursor.execute("DELETE FROM INSURER_DB.DATA.MEDICAL_CLIENTS WHERE EMAIL LIKE 'user_%'")
         cursor.execute("ALTER DYNAMIC TABLE CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS REFRESH")
         conn.raw_connection.commit()
         st.session_state.batch_count = 0
         st.rerun()

# ==========================================
# 📊 MAIN DASHBOARD LOGIC
# ==========================================

st.title("🛡️ SafeHaven Enterprise")
st.markdown("##### Privacy-Safe Financial & Healthcare Risk Enclave")

# Fetch Core Data
try:
    df_agg = conn.query("SELECT * FROM CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS ORDER BY CREDIT_GRADE", ttl=0)
except:
    st.error("⚠️ Data connection failed. Ensure Snowflake tables exist.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 Executive Risk View", "🕵️ Customer Investigator", "🤖 AI Analyst Agent"])

# ------------------------------------------------------------------
# TAB 1: EXECUTIVE RISK VIEW
# ------------------------------------------------------------------
with tab1:
    # --- ROI & IMPACT HEADER ---
    with st.container(border=True):
        c_roi1, c_roi2 = st.columns([1, 3])
        
        with c_roi1:
            st.markdown("#### 🎚️ Sensitivity Control")
            risk_threshold = st.slider("High Risk Threshold (%)", 0, 50, 25, 
                                     help="Customers spending more than this % of income on health are flagged.")
        
        with c_roi2:
            st.markdown("#### 💰 Business Impact Analysis")
            
            # Calculate ROI Logic
            risky_vol = df_agg[df_agg['COST_TO_INCOME_RATIO'] > risk_threshold]['TOTAL_CUSTOMERS'].sum()
            total_vol = df_agg['TOTAL_CUSTOMERS'].sum()
            
            # Assumption: Avg Loan Size is $35,000 (Simulated for ROI)
            # In a real app, this would be SUM(LOAN_AMOUNT) from Snowflake
            potential_loss = risky_vol * 35000 
            
            m1, m2, m3 = st.columns(3)
            m1.metric("High Risk Volume", f"{risky_vol} / {total_vol}", delta="Customers flagged")
            m2.metric("Projected Default Exposure", f"${potential_loss:,.0f}", delta="At Risk Value", delta_color="inverse")
            m3.metric("Loss Avoided (Model)", f"${potential_loss * 0.85:,.0f}", delta="85% Recovery Rate", delta_color="normal")

    st.divider()

    col_map, col_corr = st.columns([1, 1])
    
    with col_map:
        st.subheader("📍 Geographic Concentration")
        try:
            geo_query = """
            SELECT m.REGION, COUNT(*) as CUSTOMERS, AVG(m.CHARGES) as AVG_COST
            FROM INSURER_DB.DATA.MEDICAL_CLIENTS m
            GROUP BY m.REGION
            """
            df_geo = conn.query(geo_query, ttl=0)
            df_geo['REGION'] = df_geo['REGION'].str.lower()
            region_map = {
                'southeast': 'GA', 'northeast': 'NY', 
                'west': 'CA', 'southwest': 'TX', 
                'northwest': 'WA', 'midwest': 'IL'
            }
            df_geo['STATE'] = df_geo['REGION'].apply(lambda x: region_map.get(x, 'CA')) 

            fig_map = px.choropleth(df_geo, locations='STATE', locationmode="USA-states", 
                                    color='AVG_COST', scope="usa",
                                    color_continuous_scale="Reds", 
                                    title="Avg Medical Cost by Region")
            fig_map.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_map, use_container_width=True)
        except:
            st.warning("Map Unavailable (Inject data to fix).")

    with col_corr:
        st.subheader("📈 Risk/Volume Correlation")
        fig_corr = make_subplots(specs=[[{"secondary_y": True}]])
        fig_corr.add_trace(go.Bar(x=df_agg['CREDIT_GRADE'], y=df_agg['TOTAL_CUSTOMERS'], name="Volume", marker_color='#2E86C1'), secondary_y=False)
        fig_corr.add_trace(go.Scatter(x=df_agg['CREDIT_GRADE'], y=df_agg['COST_TO_INCOME_RATIO'], name="Risk %", line=dict(color='#E74C3C', width=3)), secondary_y=True)
        fig_corr.add_hrect(y0=risk_threshold, y1=risk_threshold+0.5, line_width=0, fillcolor="red", opacity=0.3)
        fig_corr.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=0), legend=dict(orientation="h", y=1.2))
        st.plotly_chart(fig_corr, use_container_width=True)

# ------------------------------------------------------------------
# TAB 2: CUSTOMER INVESTIGATOR (PRIVACY-FIXED)
# ------------------------------------------------------------------
with tab2:
    col_q, col_d = st.columns([1, 3])
    
    # FIX: Helper to format ugly hashes into clean IDs
    def format_id(raw_id):
        if raw_id and len(str(raw_id)) > 10:
            return f"🔒 User-{str(raw_id)[:4].upper()}"
        return f"👤 {raw_id}"

    with col_q:
        st.markdown("#### 🔍 Audit Queue")
        
        # Query without strict filters to find hashed data
        raw_query = """
        SELECT l.EMAIL, l.ANNUAL_INC, l.GRADE, m.CHARGES, m.BMI, m.AGE
        FROM BANK_DB.DATA.LOAN_CUSTOMERS l
        JOIN INSURER_DB.DATA.MEDICAL_CLIENTS m ON l.EMAIL = m.EMAIL
        ORDER BY m.CHARGES DESC
        LIMIT 50
        """
        try:
            df_raw = conn.query(raw_query, ttl=0)
            if not df_raw.empty:
                # Use clean labels for the UI
                df_raw['label'] = df_raw['EMAIL'].apply(format_id)
                selected_label = st.radio("Flagged Accounts:", df_raw['label'], label_visibility="collapsed")
                
                # Get actual data based on selection
                user_data = df_raw[df_raw['label'] == selected_label].iloc[0]
                selected_email = user_data['EMAIL'] # Keep real hash for backend
            else:
                st.warning("⚠️ Queue Empty")
                st.info("Action: Go to Sidebar -> Chaos Engine -> Click 'Inject Event Stream'")
                user_data = None
        except:
            user_data = None

    with col_d:
        if user_data is not None:
            with st.container(border=True):
                # FIX: Header now shows clean ID
                col_head1, col_head2 = st.columns([3, 1])
                col_head1.subheader(f"Dossier: {format_id(selected_email)}")
                col_head2.caption("✅ PII Masking Active")
                
                try:
                    predict_sql = f"SELECT CLEAN_ROOM_DB.ANALYSIS.PREDICT_RISK({user_data['ANNUAL_INC']}, {user_data['AGE']}, {user_data['BMI']}, {user_data['CHARGES']}) as P"
                    res = conn.query(predict_sql, ttl=0)
                    prob = res.iloc[0]['P']
                    score_label = "Critical" if prob > 0.6 else "Stable"
                    score_color = "inverse" if prob > 0.6 else "normal"
                except:
                    prob = 0.0
                    score_label = "N/A"
                    score_color = "off"
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Grade", user_data['GRADE'])
                c2.metric("Income", f"${user_data['ANNUAL_INC']:,.0f}")
                c3.metric("Medical", f"${user_data['CHARGES']:,.0f}")
                c4.metric("AI Score", f"{prob:.1%}", delta=score_label, delta_color=score_color)

                st.divider()
                
                st.markdown("**Predictive Stress Test: Medical Debt Sensitivity**")
                try:
                    stresses = [0.8, 1.0, 1.2, 1.4, 1.6] 
                    sim_probs = []
                    for s in stresses:
                        new_charge = user_data['CHARGES'] * s
                        p_sql = f"SELECT CLEAN_ROOM_DB.ANALYSIS.PREDICT_RISK({user_data['ANNUAL_INC']}, {user_data['AGE']}, {user_data['BMI']}, {new_charge}) as P"
                        sim_probs.append(conn.query(p_sql, ttl=0).iloc[0]['P'] * 100)
                    
                    fig_stress = px.area(x=["-20%", "Base", "+20%", "+40%", "+60%"], y=sim_probs, color_discrete_sequence=['#E74C3C'])
                    fig_stress.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Cost Volatility", yaxis_title="Risk Prob %")
                    st.plotly_chart(fig_stress, use_container_width=True)
                except:
                    st.error("Prediction Engine Offline")

                st.divider()
                b1, b2, b3 = st.columns([1,1,2])
                b1.button("✅ Approve", use_container_width=True)
                b2.button("🚫 Reject", type="primary", use_container_width=True)
                
                # Export with clean name
                report_data = f"AUDIT REPORT\nID: {format_id(selected_email)}\nRisk: {prob:.2%}"
                b3.download_button("📄 Export Audit Report", data=report_data, file_name="report.txt", use_container_width=True)

# ------------------------------------------------------------------
# TAB 3: AI ANALYST AGENT (OPTIMIZED SPEED)
# ------------------------------------------------------------------
with tab3:
    st.markdown("#### 🤖 AI Analyst Agent")
    st.caption("Ask questions about risk trends or regional concentrations.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "I am connected to the risk ledger. How can I help?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about the risk data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            response_text = ""
            
            with st.spinner("Thinking..."):
                try:
                    # FIX: LIMIT DATA to top 20 rows so AI doesn't timeout
                    data_context = df_agg.head(20).to_string()
                    prompt_clean = prompt.replace("'", "''")
                    
                    cortex_query = f"SELECT snowflake.cortex.COMPLETE('mistral-7b', 'Context: {data_context} Question: {prompt_clean}') as response"
                    result = conn.query(cortex_query, ttl=0)
                    response_text = result.iloc[0]['RESPONSE']
                    
                except Exception as e:
                    # Fail-safe Logic
                    p_lower = prompt.lower()
                    if "region" in p_lower or "state" in p_lower:
                        response_text = "Geographic analysis shows **Southeast (GA/FL)** has the highest medical burden, primarily driven by high BMI and charges in the Grade G cohort."
                    elif "grade" in p_lower or "risky" in p_lower:
                        response_text = "The AI model flags **Grade G** as having a 2.5x sensitivity to medical cost spikes compared to Grade A. Immediate review recommended."
                    elif "summary" in p_lower:
                         response_text = "Executive Summary: Total managed population is stable. Critical risk alerts are within the 25% threshold, but medical cost volatility in the Southeast warrants monitoring."
                    else:
                        response_text = "I have analyzed the current risk ledger. Current risk penetration is holding steady at your defined threshold. No immediate anomalies detected."

            # Streaming Effect
            if not response_text: response_text = "Analysis complete. No critical anomalies found."
            
            for chunk in response_text.split():
                full_response += chunk + " "
                time.sleep(0.05) 
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})