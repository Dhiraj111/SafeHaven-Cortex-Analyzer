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

    def execute_query(self, query, params=None):
        try:
            # If params exist, pass them to the query engine
            if params:
                return self.conn.query(query, params=params, ttl=0)
            return self.conn.query(query, ttl=0)
        except Exception as e:
            st.error(f"Database Error: {e}")
            return pd.DataFrame()

    def run_command(self, sql, params=None):
        try:
            cursor = self.conn.raw_connection.cursor()
            cursor.execute(sql, params)
            self.conn.raw_connection.commit()
            return True
        except Exception as e:
            st.error(f"Command Error: {e}")
            return False
        
    # NEW: Dedicated secure method for inserting lists of data
    def bulk_insert(self, sql, data_list):
        try:
            cursor = self.conn.raw_connection.cursor()
            # executemany is highly optimized and secure for lists
            cursor.executemany(sql, data_list)
            self.conn.raw_connection.commit()
            return True
        except Exception as e:
            st.error(f"Bulk Insert Error: {e}")
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
    
    # SECURE: Now uses %s placeholders instead of f-strings
    def predict_risk(self, income, age, bmi, charges):
        try:
            sql = "SELECT CLEAN_ROOM_DB.ANALYSIS.PREDICT_RISK(%s, %s, %s, %s) as P"
            params = (income, age, bmi, charges)
            res = self.execute_query(sql, params)
            return res.iloc[0]['P']
        except:
            return 0.0

    def ask_cortex(self, context, question):
        # Note: Cortex UDFs might require string literal construction inside the function call logic,
        # but for standard queries, we bind where possible. 
        # For Cortex specifically, we sanitize quotes to be safe since it's a function string argument.
        clean_context = context.replace("'", "''")
        clean_question = question.replace("'", "''")        
        # We use strict formatting here because the arguments are part of a function string
        sql = f"SELECT snowflake.cortex.COMPLETE('mistral-7b', 'Context: {clean_context} Question: {clean_question}') as response"
        res = self.execute_query(sql)
        return res.iloc[0]['RESPONSE']