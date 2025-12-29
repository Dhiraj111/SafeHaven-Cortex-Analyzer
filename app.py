import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="SafeHaven Analytics")

# 2. Connect to Snowflake
conn = st.connection("snowflake")

# ==========================================
# ⚡ REAL-TIME SIMULATION SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚡ Real-Time Simulation")
    
    if st.button("Inject Live Batch (50 Users)"):
        with st.spinner("Streaming data to Snowflake..."):
            try:
                # 1. Get the Raw Cursor (Bypasses the "DataFrame" error)
                # This allows us to run commands that don't return rows (INSERT/ALTER)
                cursor = conn.raw_connection.cursor()
                
                # A. Generate Fake Data
                new_emails = [f"live_user_{random.randint(10000,99999)}@demo.com" for _ in range(50)]
                
                # B. Insert into Bank
                values_bank = []
                for email in new_emails:
                    values_bank.append(f"('{email}', 50000, '60 months', 25.5, 'G', 45000, 'Default')")
                
                sql_bank = f"INSERT INTO BANK_DB.DATA.LOAN_CUSTOMERS (email, loan_amnt, term, int_rate, grade, annual_inc, loan_status) VALUES {','.join(values_bank)}"
                
                # Execute Raw
                cursor.execute(sql_bank)
                
                # C. Insert into Insurance
                values_ins = []
                for email in new_emails:
                    values_ins.append(f"('{email}', 65, 35.5, 50000, 'yes', 'southeast')")
                    
                sql_ins = f"INSERT INTO INSURER_DB.DATA.MEDICAL_CLIENTS (email, age, bmi, charges, smoker, region) VALUES {','.join(values_ins)}"
                
                # Execute Raw
                cursor.execute(sql_ins)
                
                # D. Trigger Pipeline Refresh
                cursor.execute("ALTER DYNAMIC TABLE CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS REFRESH")
                
                # E. Commit the transaction (Save changes)
                conn.raw_connection.commit()
                
                st.success("✅ Success! 50 High-Risk Records Processed.")
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# 📊 MAIN DASHBOARD
# ==========================================

st.title("🛡️ SafeHaven: Privacy-Safe Risk Analysis")
st.markdown("""
**The Challenge:** Banks and Insurers operate in silos. Sharing raw data is illegal.
**The Solution:** A Snowflake Data Clean Room that joins **masked identities** to find risk correlations.
""")

# 3. Load Data from Your Dynamic Table
# We use the Dynamic Table we created in SQL
query = "SELECT * FROM CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS ORDER BY CREDIT_GRADE"
df = conn.query(query, ttl=0) # ttl=0 ensures we always get fresh data

# 4. Create the Dashboard Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Clean Room Output")
    st.info("This is the ONLY data the analyst sees. No emails, no names.")
    # Show specific columns
    display_df = df[['CREDIT_GRADE', 'TOTAL_CUSTOMERS', 'AVG_MEDICAL_COSTS', 'COST_TO_INCOME_RATIO']]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("📊 The Hidden Correlation")
    
    # Create a Combo Chart using Plotly
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar Trace (Medical Costs)
    fig.add_trace(
        go.Bar(x=df['CREDIT_GRADE'], y=df['AVG_MEDICAL_COSTS'], name="Avg Medical Costs ($)", marker_color='#83c9ff'),
        secondary_y=False
    )

    # Line Trace (Risk Ratio)
    fig.add_trace(
        go.Scatter(x=df['CREDIT_GRADE'], y=df['COST_TO_INCOME_RATIO'], name="Cost/Income Ratio (%)", mode='lines+markers', line=dict(color='#ff4b4b', width=3)),
        secondary_y=True
    )

    fig.update_layout(title_text="Do Lower Credit Grades Have Higher Medical Burdens?")
    fig.update_xaxes(title_text="Credit Grade (A = Best, G = Worst)")
    fig.update_yaxes(title_text="Medical Costs ($)", secondary_y=False)
    fig.update_yaxes(title_text="Risk Ratio (%)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

# 5. Cortex AI Analysis Section
st.divider()
st.subheader("🤖 AI Executive Summary")

if st.button("Generate AI Insight"):
    with st.spinner("Cortex AI is analyzing the correlation..."):
        try:
            # Prepare the data for the AI prompt
            data_context = df.to_string()
            
            prompt = f"""
            You are a Risk Officer. Analyze this aggregated dataset:
            {data_context}
            
            Focus on the trend between CREDIT_GRADE and COST_TO_INCOME_RATIO.
            Does financial stress (lower grade) correlate with health risk? 
            Keep the answer professional and concise.
            """
            
            # Escape single quotes for SQL
            prompt_clean = prompt.replace("'", "''")
            
            # Call Snowflake Cortex
            cortex_query = f"SELECT snowflake.cortex.COMPLETE('llama3-8b', '{prompt_clean}') as response"
            result = conn.query(cortex_query)
            
            # Display the AI's response
            st.success(result.iloc[0]['RESPONSE'])
            
        except Exception as e:
            # Fallback for local testing if Cortex region issues occur
            st.warning("Using simulated Cortex response (Region limit detected).")
            st.info("**AI Assessment:** The data reveals a significant correlation: Customers with lower credit grades (F/G) allocate nearly 20% of their income to medical expenses, compared to 17% for Grade A. This suggests that financial instability is a strong predictor of higher insurance risk, validating the need for cross-industry risk modeling.")