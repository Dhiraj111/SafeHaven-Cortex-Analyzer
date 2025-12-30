import streamlit as st
import pandas as pd

class SnowflakeManager:
    def __init__(self):
        self.conn = st.connection("snowflake")

    def get_system_status(self):
        try:
            cursor = self.conn.raw_connection.cursor()
            cursor.execute("LIST @CLEAN_ROOM_DB.ANALYSIS.MODEL_STAGE")
            result = cursor.fetchall()
            return result[0][3] if result else None
        except:
            return None

    def execute_query(self, query):
        try:
            return self.conn.query(query, ttl=0)
        except Exception as e:
            st.error(f"Database Error: {e}")
            return pd.DataFrame()

    def run_command(self, sql):
        try:
            cursor = self.conn.raw_connection.cursor()
            cursor.execute(sql)
            self.conn.raw_connection.commit()
            return True
        except Exception as e:
            st.error(f"Command Error: {e}")
            return False
            
    def get_dashboard_data(self):
        return self.execute_query("SELECT * FROM CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS ORDER BY CREDIT_GRADE")

    def get_geo_data(self):
        return self.execute_query("""
            SELECT m.REGION, COUNT(*) as CUSTOMERS, AVG(m.CHARGES) as AVG_COST
            FROM INSURER_DB.DATA.MEDICAL_CLIENTS m
            GROUP BY m.REGION
        """)

    def get_audit_queue(self):
        return self.execute_query("""
            SELECT l.EMAIL, l.ANNUAL_INC, l.GRADE, m.CHARGES, m.BMI, m.AGE
            FROM BANK_DB.DATA.LOAN_CUSTOMERS l
            JOIN INSURER_DB.DATA.MEDICAL_CLIENTS m ON l.EMAIL = m.EMAIL
            ORDER BY m.CHARGES DESC
            LIMIT 50
        """)

    def predict_risk(self, income, age, bmi, charges):
        try:
            sql = f"SELECT CLEAN_ROOM_DB.ANALYSIS.PREDICT_RISK({income}, {age}, {bmi}, {charges}) as P"
            res = self.execute_query(sql)
            return res.iloc[0]['P']
        except:
            return 0.0

    def ask_cortex(self, context, question):
        # Using Mistral-7b
        sql = f"SELECT snowflake.cortex.COMPLETE('mistral-7b', 'Context: {context} Question: {question}') as response"
        res = self.execute_query(sql)
        return res.iloc[0]['RESPONSE']