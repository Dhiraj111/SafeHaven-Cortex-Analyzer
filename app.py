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
        # Use RAW CURSOR to bypass Streamlit's SQL parser
        cursor = conn.raw_connection.cursor()
        
        # We look for ANY file in the stage to avoid pattern matching errors
        cursor.execute("LIST @CLEAN_ROOM_DB.ANALYSIS.MODEL_STAGE")
        result = cursor.fetchall() # Returns list of tuples
        
        if result:
            # Snowflake LIST returns: [name, size, md5, last_modified]
            # The timestamp is the 4th item (index 3)
            last_mod = result[0][3] 
            
            st.caption(f"🧠 Model Last Retrained:")
            st.code(f"{last_mod}")
            st.success("✅ Auto-Retraining Active")
        else:
            st.error("⚠️ Stage is Empty!")
            st.info("Action Required: Go to Snowflake and run: CALL CLEAN_ROOM_DB.ANALYSIS.TRAIN_RISK_MODEL();")
            
    except Exception as e:
        st.error(f"Connection Error: {e}")

    st.divider()
    
    # --- PART 2: AI RISK CALCULATOR (WITH GAUGE) ---
    st.subheader("🔮 AI Risk Calculator")
    st.info("Test the Machine Learning Model directly.")
    
    # Inputs for the Model
    p_income = st.number_input("Annual Income ($)", value=50000, step=5000)
    p_costs = st.number_input("Medical Costs ($)", value=20000, step=1000)
    p_age = st.slider("Age", 18, 80, 35)
    p_bmi = st.slider("BMI", 15.0, 50.0, 25.0)
    
    if st.button("Calculate Risk Probability", type="primary"):
        try:
            # Call the Snowflake UDF
            sql_predict = f"""
            SELECT CLEAN_ROOM_DB.ANALYSIS.PREDICT_RISK(
                {p_income}, {p_age}, {p_bmi}, {p_costs}
            ) as PROBABILITY
            """
            df_pred = conn.query(sql_predict, ttl=0)
            risk_score = df_pred.iloc[0]['PROBABILITY']
            risk_pct = risk_score * 100
            
            # --- INTERACTIVE GAUGE CHART ---
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risk_pct,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Default Probability (%)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "black"},
                    'steps': [
                        {'range': [0, 30], 'color': "#00cc96"},  # Green (Safe)
                        {'range': [30, 70], 'color': "#ffa15a"}, # Orange (Caution)
                        {'range': [70, 100], 'color': "#ef553b"} # Red (Danger)
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': risk_pct
                    }
                }
            ))
            fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)

            # Decision Logic Display
            if risk_score > 0.7:
                st.error("🚨 AI Recommendation: REJECT APPLICATION")
            elif risk_score > 0.3:
                st.warning("⚠️ AI Recommendation: MANUAL REVIEW REQUIRED")
            else:
                st.success("✅ AI Recommendation: AUTO-APPROVE")
                
        except Exception as e:
            st.error(f"Prediction Error: {e}")

    st.divider()

    # --- PART 3: CHAOS SIMULATION ---
    st.subheader("🚨 Chaos Simulation")
    
    if 'batch_count' not in st.session_state:
        st.session_state.batch_count = 0

    st.write(f"**Batches Injected:** {st.session_state.batch_count}")

    if st.button("Inject Batch (50 Users)"):
        with st.spinner("Simulating market event & Triggering Stream..."):
            try:
                cursor = conn.raw_connection.cursor()
                
                # Generate Fake Data
                new_emails = [f"live_{st.session_state.batch_count}_{random.randint(1000,9999)}@demo.com" for _ in range(50)]
                
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
                st.toast(f"⚠️ Data Injected! Watch the MLOps Timestamp update shortly.", icon="🤖")
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

# 3. Load Data & Filters
query = "SELECT * FROM CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS ORDER BY CREDIT_GRADE"
df = conn.query(query, ttl=0) 

# --- INTERACTIVE DATA EXPLORER ---
with st.expander("🔍 Data Explorer & Filters", expanded=True):
    col_filter, col_metrics = st.columns([1, 3])
    
    with col_filter:
        all_grades = df['CREDIT_GRADE'].unique().tolist()
        selected_grades = st.multiselect(
            "Filter by Credit Grade:", 
            options=all_grades, 
            default=all_grades
        )
    
    with col_metrics:
        # Filter the dataframe based on user selection
        if not selected_grades:
            st.warning("Please select at least one Credit Grade.")
            df_filtered = df
        else:
            df_filtered = df[df['CREDIT_GRADE'].isin(selected_grades)]

        # Calculate KPIs on filtered data
        total_users = df_filtered['TOTAL_CUSTOMERS'].sum()
        avg_med_cost = df_filtered['AVG_MEDICAL_COSTS'].mean() if not df_filtered.empty else 0
        high_risk_users = df_filtered[df_filtered['CREDIT_GRADE'].isin(['F', 'G'])]['TOTAL_CUSTOMERS'].sum()

        k1, k2, k3 = st.columns(3)
        k1.metric("Total Customers", f"{total_users:,.0f}", delta=f"{len(selected_grades)} Grades Selected")
        k2.metric("Avg Medical Exposure", f"${avg_med_cost:,.0f}")
        k3.metric("High Risk Count (F/G)", f"{high_risk_users}", delta_color="inverse")

st.divider()

# 4. Charts (Using Filtered Data)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Live Activity Feed")
    st.dataframe(
        df_filtered[['CREDIT_GRADE', 'TOTAL_CUSTOMERS', 'COST_TO_INCOME_RATIO']].style.highlight_max(axis=0, color='#ff4b4b'), 
        use_container_width=True
    )
    if st.session_state.batch_count > 0:
        st.warning(f"⚠️ ANOMALY: {st.session_state.batch_count} batch(es) ingested.")

with col2:
    st.subheader("📊 Financial vs. Health Risk Correlation")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar Trace (Volume)
    fig.add_trace(
        go.Bar(x=df_filtered['CREDIT_GRADE'], y=df_filtered['TOTAL_CUSTOMERS'], name="Customer Volume", marker_color='#83c9ff'),
        secondary_y=False
    )

    # Line Trace (Risk Ratio)
    fig.add_trace(
        go.Scatter(x=df_filtered['CREDIT_GRADE'], y=df_filtered['COST_TO_INCOME_RATIO'], name="Risk Ratio (%)", mode='lines+markers', line=dict(color='#ff4b4b', width=4)),
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
            # We send the filtered dataframe context to the AI
            data_context = df_filtered.to_string()
            prompt = f"""
            You are a Risk Officer. Analyze this filtered dataset:
            {data_context}
            
            1. Identify which selected Credit Grade has the highest 'COST_TO_INCOME_RATIO'.
            2. Provide a 1-sentence warning about the relationship between these specific grades and medical costs.
            3. Keep it professional.
            """
            prompt_clean = prompt.replace("'", "''")
            cortex_query = f"SELECT snowflake.cortex.COMPLETE('llama3-8b', '{prompt_clean}') as response"
            result = conn.query(cortex_query, ttl=0)
            st.success(result.iloc[0]['RESPONSE'])
            
        except Exception as e:
            st.warning("Simulated AI Response (Region Limit).")
            st.info("**AI Assessment:** CRITICAL CORRELATION DETECTED. The selected cohort shows a Cost-to-Income ratio exceeding safe limits (25%). Immediate review recommended.")