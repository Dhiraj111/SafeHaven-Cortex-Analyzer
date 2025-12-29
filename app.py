import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="SafeHaven Analytics", page_icon="🛡️")

# 2. Connect to Snowflake
conn = st.connection("snowflake")

# ==========================================
# ⚡ SIDEBAR: MLOPS & SIMULATION
# ==========================================
with st.sidebar:
    st.title("⚡ Control Center")
    
    # --- PART 1: MLOPS MONITOR (DEBUG MODE) ---
    st.subheader("⚙️ MLOps Pipeline")
    
    try:
        cursor = conn.raw_connection.cursor()
        cursor.execute("LIST @CLEAN_ROOM_DB.ANALYSIS.MODEL_STAGE")
        result = cursor.fetchall() 
        
        if result:
            last_mod = result[0][3] 
            st.caption(f"🧠 Model Last Retrained:")
            st.code(f"{last_mod}")
            st.success("✅ Auto-Retraining Active")
        else:
            st.error("⚠️ Stage is Empty!")
            st.info("Run: CALL CLEAN_ROOM_DB.ANALYSIS.TRAIN_RISK_MODEL();")
            
    except Exception as e:
        st.error(f"Connection Error: {e}")

    st.divider()
    
    # --- PART 2: AI RISK CALCULATOR (INTERACTIVE) ---
    st.subheader("🔮 AI Risk Calculator")
    
    # Auto-Calculate BMI from Height/Weight
    col_h, col_w = st.columns(2)
    with col_h:
        p_height = st.number_input("Ht (m)", 1.50, 2.20, 1.75)
    with col_w:
        p_weight = st.number_input("Wt (kg)", 40, 150, 70)
    
    p_bmi = p_weight / (p_height ** 2)
    
    p_income = st.number_input("Annual Income ($)", value=50000, step=5000)
    p_costs = st.number_input("Medical Costs ($)", value=20000, step=1000)
    p_age = st.slider("Age", 18, 80, 35)
    
    if st.button("Calculate Risk Probability", type="primary"):
        try:
            sql_predict = f"""
            SELECT CLEAN_ROOM_DB.ANALYSIS.PREDICT_RISK(
                {p_income}, {p_age}, {p_bmi}, {p_costs}
            ) as PROBABILITY
            """
            df_pred = conn.query(sql_predict, ttl=0)
            risk_score = df_pred.iloc[0]['PROBABILITY']
            risk_pct = risk_score * 100
            
            # Gauge Chart
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risk_pct,
                title = {'text': "Default Probability (%)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "black"},
                    'steps': [
                        {'range': [0, 30], 'color': "#00cc96"},
                        {'range': [30, 70], 'color': "#ffa15a"},
                        {'range': [70, 100], 'color': "#ef553b"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': risk_pct}
                }
            ))
            fig_gauge.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)

            if risk_score > 0.7:
                st.error("🚨 REJECT APPLICATION")
            elif risk_score > 0.3:
                st.warning("⚠️ MANUAL REVIEW")
            else:
                st.success("✅ AUTO-APPROVE")
                
        except Exception as e:
            st.error(f"Prediction Error: {e}")

    st.divider()

    # --- PART 3: SCENARIO SIMULATION (NEW!) ---
    st.subheader("🚨 Chaos Simulation")
    
    if 'batch_count' not in st.session_state:
        st.session_state.batch_count = 0

    st.write(f"**Batches Injected:** {st.session_state.batch_count}")
    
    # NEW: Choose your disaster
    scenario = st.selectbox("Select Scenario:", ["📉 Economic Recession", "病毒 Health Crisis", "📈 Market Boom"])

    if st.button(f"Inject {scenario}"):
        with st.spinner(f"Simulating {scenario}..."):
            try:
                cursor = conn.raw_connection.cursor()
                new_emails = [f"live_{st.session_state.batch_count}_{random.randint(1000,9999)}@demo.com" for _ in range(50)]
                
                values_bank = []
                values_ins = []
                
                for email in new_emails:
                    # Logic changes based on scenario!
                    if "Recession" in scenario:
                        # Low Income, High Defaults
                        inc = random.randint(20000, 40000)
                        status = 'Default'
                        costs = random.randint(1000, 5000)
                    elif "Health" in scenario:
                        # Normal Income, High Medical Costs
                        inc = random.randint(50000, 80000)
                        status = 'Fully Paid'
                        costs = random.randint(40000, 90000) # HUGE COSTS
                    else: # Boom
                        inc = random.randint(90000, 150000)
                        status = 'Fully Paid'
                        costs = random.randint(1000, 3000)

                    values_bank.append(f"('{email}', 50000, '60 months', 25.5, 'G', {inc}, '{status}')")
                    values_ins.append(f"('{email}', 45, 28.5, {costs}, 'yes', 'southeast')")

                sql_bank = f"INSERT INTO BANK_DB.DATA.LOAN_CUSTOMERS (email, loan_amnt, term, int_rate, grade, annual_inc, loan_status) VALUES {','.join(values_bank)}"
                sql_ins = f"INSERT INTO INSURER_DB.DATA.MEDICAL_CLIENTS (email, age, bmi, charges, smoker, region) VALUES {','.join(values_ins)}"
                
                cursor.execute(sql_bank)
                cursor.execute(sql_ins)
                cursor.execute("ALTER DYNAMIC TABLE CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS REFRESH")
                conn.raw_connection.commit()
                
                st.session_state.batch_count += 1
                st.toast(f"⚠️ {scenario} Started! Watch charts update.", icon="📉")
                time.sleep(2) 
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")

    # --- PART 4: RESET ---
    if st.button("🔄 Reset System"):
        with st.spinner("Cleaning database..."):
            cursor = conn.raw_connection.cursor()
            cursor.execute("DELETE FROM BANK_DB.DATA.LOAN_CUSTOMERS WHERE EMAIL LIKE 'live_%'")
            cursor.execute("DELETE FROM INSURER_DB.DATA.MEDICAL_CLIENTS WHERE EMAIL LIKE 'live_%'")
            cursor.execute("ALTER DYNAMIC TABLE CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS REFRESH")
            conn.raw_connection.commit()
            st.session_state.batch_count = 0
            st.success("Reset Complete.")
            time.sleep(2)
            st.rerun()

# ==========================================
# 📊 MAIN DASHBOARD
# ==========================================

st.title("🛡️ SafeHaven: Privacy-Safe Risk Analysis")
st.markdown("### Cross-Industry Risk Monitoring System (Powered by Snowpark ML)")

# 3. Load Data
query = "SELECT * FROM CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS ORDER BY CREDIT_GRADE"
df = conn.query(query, ttl=0) 

# --- INTERACTIVE FILTER & THRESHOLD ---
with st.expander("🔍 Risk Officer Controls", expanded=True):
    col_ctrl1, col_ctrl2 = st.columns([1, 2])
    
    with col_ctrl1:
        # Dynamic Risk Threshold Slider
        risk_threshold = st.slider("Define 'High Risk' Threshold (Cost-to-Income %)", 0, 50, 20)
        st.caption(f"Flagging any grade > {risk_threshold}% exposure")
        
    with col_ctrl2:
        all_grades = df['CREDIT_GRADE'].unique().tolist()
        selected_grades = st.multiselect("Filter Grades:", all_grades, default=all_grades)

# Apply Filter
if selected_grades:
    df_filtered = df[df['CREDIT_GRADE'].isin(selected_grades)]
else:
    df_filtered = df

# Feature 2: KPIs (Dynamic based on Slider!)
total_users = df_filtered['TOTAL_CUSTOMERS'].sum()
avg_med_cost = df_filtered['AVG_MEDICAL_COSTS'].mean() if not df_filtered.empty else 0

# Count how many grades exceed the USER'S threshold
risky_grades = df_filtered[df_filtered['COST_TO_INCOME_RATIO'] > risk_threshold]
high_risk_vol = risky_grades['TOTAL_CUSTOMERS'].sum()

k1, k2, k3 = st.columns(3)
k1.metric("Total Customers", f"{total_users:,.0f}")
k2.metric("Avg Medical Exposure", f"${avg_med_cost:,.0f}")
k3.metric(f"Risky Customers (>{risk_threshold}%)", f"{high_risk_vol}", delta="Above Threshold", delta_color="inverse")

st.divider()

# 4. Charts
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Live Activity Feed")
    # Highlight rows that exceed the user's threshold
    def highlight_risk(val):
        color = '#ff4b4b' if val > risk_threshold else ''
        return f'background-color: {color}'

    st.dataframe(
        df_filtered[['CREDIT_GRADE', 'TOTAL_CUSTOMERS', 'COST_TO_INCOME_RATIO']]
        .style.map(highlight_risk, subset=['COST_TO_INCOME_RATIO'])
        .format({"COST_TO_INCOME_RATIO": "{:.2f}%"}),
        use_container_width=True
    )

with col2:
    st.subheader("📊 Financial vs. Health Risk Correlation")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar Trace
    fig.add_trace(
        go.Bar(x=df_filtered['CREDIT_GRADE'], y=df_filtered['TOTAL_CUSTOMERS'], name="Volume", marker_color='#83c9ff'),
        secondary_y=False
    )

    # Line Trace
    fig.add_trace(
        go.Scatter(x=df_filtered['CREDIT_GRADE'], y=df_filtered['COST_TO_INCOME_RATIO'], name="Risk Ratio (%)", mode='lines+markers', line=dict(color='#ff4b4b', width=4)),
        secondary_y=True
    )
    
    # DYNAMIC THRESHOLD LINE (Moves with Slider!)
    fig.add_hrect(y0=risk_threshold, y1=risk_threshold+0.5, line_width=0, fillcolor="red", opacity=0.5, annotation_text="High Risk Threshold", annotation_position="top right")

    fig.update_layout(
        height=450,
        margin=dict(t=30, b=0, l=0, r=0),
        xaxis=dict(title="Credit Grade"),
        yaxis=dict(title="Customer Volume"),
        yaxis2=dict(title="Risk Ratio (%)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

# 5. Cortex AI Analysis
st.divider()
st.subheader("🤖 Cortex AI Executive Summary")

if st.button("Generate AI Insight"):
    with st.spinner("Cortex AI is analyzing the correlation..."):
        try:
            data_context = df_filtered.to_string()
            prompt = f"""
            You are a Risk Officer. Analyze this dataset:
            {data_context}
            
            1. Which Credit Grade has the worst 'COST_TO_INCOME_RATIO'?
            2. Are any grades exceeding the safety threshold of {risk_threshold}%?
            3. Provide a brief recommendation.
            """
            prompt_clean = prompt.replace("'", "''")
            cortex_query = f"SELECT snowflake.cortex.COMPLETE('llama3-8b', '{prompt_clean}') as response"
            result = conn.query(cortex_query, ttl=0)
            st.success(result.iloc[0]['RESPONSE'])
            
        except Exception as e:
            st.warning("Simulated AI Response.")
            st.info("**AI Assessment:** CRITICAL CORRELATION DETECTED. Multiple grades exceed your defined risk threshold.")