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
    
    # --- PART 2: AI RISK CALCULATOR (FULL) ---
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

            # Decision & Explainability
            if risk_score > 0.7:
                st.error("🚨 REJECT APPLICATION")
            elif risk_score > 0.3:
                st.warning("⚠️ MANUAL REVIEW")
            else:
                st.success("✅ AUTO-APPROVE")
            
            with st.expander("Why this score?"):
                 st.write(f"**Health Burden:** {(p_costs/p_income)*100:.1f}% of Income")
                 st.write(f"**BMI Factor:** {p_bmi:.1f} (Normal: 18-25)")

        except Exception as e:
            st.error(f"Prediction Error: {e}")

    st.divider()

    # --- PART 3: SCENARIO SIMULATION ---
    st.subheader("🚨 Chaos Simulation")
    
    if 'batch_count' not in st.session_state:
        st.session_state.batch_count = 0

    st.write(f"**Batches Injected:** {st.session_state.batch_count}")
    
    scenario = st.selectbox("Select Scenario:", ["📉 Economic Recession", "病毒 Health Crisis", "📈 Market Boom"])

    if st.button(f"Inject {scenario}"):
        with st.spinner(f"Simulating {scenario}..."):
            try:
                cursor = conn.raw_connection.cursor()
                new_emails = [f"live_{st.session_state.batch_count}_{random.randint(1000,9999)}@demo.com" for _ in range(50)]
                
                values_bank = []
                values_ins = []
                
                for email in new_emails:
                    if "Recession" in scenario:
                        inc = random.randint(20000, 40000)
                        status = 'Default'
                        costs = random.randint(1000, 5000)
                    elif "Health" in scenario:
                        inc = random.randint(50000, 80000)
                        status = 'Fully Paid'
                        costs = random.randint(40000, 90000)
                    else:
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
        # Dynamic Risk Threshold
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

# Feature 2: KPIs (Dynamic)
total_users = df_filtered['TOTAL_CUSTOMERS'].sum()
avg_med_cost = df_filtered['AVG_MEDICAL_COSTS'].mean() if not df_filtered.empty else 0
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

    fig.add_trace(
        go.Bar(x=df_filtered['CREDIT_GRADE'], y=df_filtered['TOTAL_CUSTOMERS'], name="Volume", marker_color='#83c9ff'),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=df_filtered['CREDIT_GRADE'], y=df_filtered['COST_TO_INCOME_RATIO'], name="Risk Ratio (%)", mode='lines+markers', line=dict(color='#ff4b4b', width=4)),
        secondary_y=True
    )
    
    # DYNAMIC LINE
    fig.add_hrect(y0=risk_threshold, y1=risk_threshold+0.5, line_width=0, fillcolor="red", opacity=0.5, annotation_text="Threshold", annotation_position="top right")

    fig.update_layout(
        height=450,
        margin=dict(t=30, b=0, l=0, r=0),
        xaxis=dict(title="Credit Grade"),
        yaxis=dict(title="Customer Volume"),
        yaxis2=dict(title="Risk Ratio (%)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

# 5. CORTEX AI AGENT (CHATBOT)
st.divider()
st.subheader("🤖 AI Risk Analyst Agent")
st.caption("Ask questions about the filtered data (e.g., 'Why is Grade G risky?', 'Summarize the medical costs')")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask the AI Risk Officer..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            try:
                data_context = df_filtered.to_string()
                full_prompt = f"""
                [ROLE]
                You are a Senior Risk Officer. Analyze this dataset:
                {data_context}
                [QUESTION]
                {prompt}
                [INSTRUCTION]
                Answer strictly based on the data. Be concise.
                """
                prompt_clean = full_prompt.replace("'", "''")
                cortex_query = f"SELECT snowflake.cortex.COMPLETE('llama3-8b', '{prompt_clean}') as response"
                result = conn.query(cortex_query, ttl=0)
                response_text = result.iloc[0]['RESPONSE']
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error("AI Error (Likely token limit or region).")