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
# ⚡ SIDEBAR: SIMULATION & PREDICTION
# ==========================================
with st.sidebar:
    st.title("⚡ Control Center")
    
    # --- PART 1: AI PREDICTOR (NEW!) ---
    st.subheader("🔮 AI Risk Calculator")
    st.info("Test the Machine Learning Model directly.")
    
    # Inputs for the Model
    p_income = st.number_input("Annual Income ($)", value=50000, step=5000)
    p_costs = st.number_input("Medical Costs ($)", value=20000, step=1000)
    p_age = st.slider("Age", 18, 80, 35)
    p_bmi = st.slider("BMI", 15.0, 50.0, 25.0)
    
    if st.button("Calculate Risk Probability", type="primary"):
        try:
            # Call the Snowflake UDF we created
            sql_predict = f"""
            SELECT CLEAN_ROOM_DB.ANALYSIS.PREDICT_RISK(
                {p_income}, {p_age}, {p_bmi}, {p_costs}
            ) as PROBABILITY
            """
            df_pred = conn.query(sql_predict, ttl=0)
            risk_score = df_pred.iloc[0]['PROBABILITY']
            
            # Show Result
            if risk_score > 0.7:
                st.error(f"High Default Risk: {risk_score:.1%}")
            elif risk_score > 0.3:
                st.warning(f"Moderate Risk: {risk_score:.1%}")
            else:
                st.success(f"Low Risk: {risk_score:.1%}")
                
        except Exception as e:
            st.error(f"Prediction Error: {e}")

    st.divider()

    # --- PART 2: LIVE SIMULATION ---
    st.subheader("🚨 Chaos Simulation")
    
    # Track batches in session state
    if 'batch_count' not in st.session_state:
        st.session_state.batch_count = 0

    st.write(f"**Batches Injected:** {st.session_state.batch_count}")

    if st.button("Inject Batch (50 Users)"):
        with st.spinner("Simulating market event..."):
            try:
                cursor = conn.raw_connection.cursor()
                
                # A. Generate Fake Data
                new_emails = [f"live_{st.session_state.batch_count}_{random.randint(1000,9999)}@demo.com" for _ in range(50)]
                
                # B. Insert High Risk Data
                values_bank = []
                values_ins = []
                for email in new_emails:
                    values_bank.append(f"('{email}', 50000, '60 months', 25.5, 'G', 45000, 'Default')")
                    values_ins.append(f"('{email}', 65, 35.5, 50000, 'yes', 'southeast')")

                sql_bank = f"INSERT INTO BANK_DB.DATA.LOAN_CUSTOMERS (email, loan_amnt, term, int_rate, grade, annual_inc, loan_status) VALUES {','.join(values_bank)}"
                sql_ins = f"INSERT INTO INSURER_DB.DATA.MEDICAL_CLIENTS (email, age, bmi, charges, smoker, region) VALUES {','.join(values_ins)}"
                
                cursor.execute(sql_bank)
                cursor.execute(sql_ins)
                cursor.execute("ALTER DYNAMIC TABLE CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS REFRESH")
                conn.raw_connection.commit()
                
                st.session_state.batch_count += 1
                st.toast(f"⚠️ 50 Records Injected!", icon="🚨")
                time.sleep(2) 
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")

    # --- PART 3: RESET ---
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

# Feature 2: KPIs
total_users = df['TOTAL_CUSTOMERS'].sum()
avg_med_cost = df['AVG_MEDICAL_COSTS'].mean()
high_risk_users = df[df['CREDIT_GRADE'].isin(['F', 'G'])]['TOTAL_CUSTOMERS'].sum()

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Monitored Customers", f"{total_users:,.0f}", delta=f"+{st.session_state.batch_count * 50} New")
kpi2.metric("Avg Medical Exposure", f"${avg_med_cost:,.0f}", delta_color="inverse")
kpi3.metric("CRITICAL RISK ALERTS (Grade F/G)", f"{high_risk_users}", delta="Requires Attention", delta_color="inverse")

st.divider()

# 4. Charts
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Live Activity Feed")
    st.dataframe(
        df[['CREDIT_GRADE', 'TOTAL_CUSTOMERS', 'COST_TO_INCOME_RATIO']].style.highlight_max(axis=0, color='#ff4b4b'), 
        use_container_width=True
    )
    if st.session_state.batch_count > 0:
        st.warning(f"⚠️ ANOMALY: {st.session_state.batch_count} batch(es) ingested.")

with col2:
    st.subheader("📊 Financial vs. Health Risk Correlation")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar Trace (Volume)
    fig.add_trace(
        go.Bar(x=df['CREDIT_GRADE'], y=df['TOTAL_CUSTOMERS'], name="Customer Volume", marker_color='#83c9ff'),
        secondary_y=False
    )

    # Line Trace (Risk)
    fig.add_trace(
        go.Scatter(x=df['CREDIT_GRADE'], y=df['COST_TO_INCOME_RATIO'], name="Risk Ratio (%)", mode='lines+markers', line=dict(color='#ff4b4b', width=4)),
        secondary_y=True
    )

    fig.update_layout(
        height=450,
        margin=dict(t=30, b=0, l=0, r=0),
        xaxis=dict(title="Credit Grade"),
        yaxis=dict(title="Customer Volume (Count)"),
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
            data_context = df.to_string()
            prompt = f"""
            You are a Risk Officer. Analyze this live dataset:
            {data_context}
            
            1. Identify which Credit Grade has the highest 'COST_TO_INCOME_RATIO'.
            2. Warn about the trend between low credit scores and high medical costs.
            3. Keep it brief and professional.
            """
            prompt_clean = prompt.replace("'", "''")
            cortex_query = f"SELECT snowflake.cortex.COMPLETE('llama3-8b', '{prompt_clean}') as response"
            result = conn.query(cortex_query, ttl=0)
            st.success(result.iloc[0]['RESPONSE'])
            
        except Exception as e:
            st.warning("Simulated AI Response (Region Limit).")
            st.info("**AI Assessment:** CRITICAL CORRELATION DETECTED. Grade G customers now show a Cost-to-Income ratio exceeding 25%, indicating extreme financial fragility.")