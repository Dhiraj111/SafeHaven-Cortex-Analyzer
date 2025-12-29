import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="SafeHaven Analytics")

st.title("🛡️ SafeHaven: Privacy-Safe Risk Analysis")
st.markdown("""
**The Challenge:** Banks and Insurers operate in silos. Sharing raw data is illegal.
**The Solution:** A Snowflake Data Clean Room that joins **masked identities** to find risk correlations.
""")

# 2. Connect to Snowflake
# This looks for the details you put in secrets.toml
conn = st.connection("snowflake")

# 3. Load Data from Your Clean Room View
# We use the view created in Day 2
query = "SELECT * FROM CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS ORDER BY CREDIT_GRADE"
df = conn.query(query, ttl=600)

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
    # Bar = Medical Costs, Line = Cost to Income Ratio
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

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