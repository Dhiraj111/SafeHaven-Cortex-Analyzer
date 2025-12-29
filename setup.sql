-- ----------------------------------------------------------------------------
-- 🛡️ SafeHaven: Database & ML Setup Script
-- ----------------------------------------------------------------------------
-- This script reconstructs the entire backend environment:
-- 1. Data Clean Room (Banks & Insurers)
-- 2. Real-Time Pipelines (Dynamic Tables)
-- 3. Machine Learning Environment (Training & Inference)
-- ----------------------------------------------------------------------------

-- 1. SETUP DATABASE & SCHEMA
CREATE DATABASE IF NOT EXISTS CLEAN_ROOM_DB;
CREATE SCHEMA IF NOT EXISTS CLEAN_ROOM_DB.ANALYSIS;

-- 2. CREATE REAL-TIME PIPELINE (Dynamic Table)
-- Aggregates risk data and updates every 1 minute
CREATE OR REPLACE DYNAMIC TABLE CLEAN_ROOM_DB.ANALYSIS.REAL_WORLD_INSIGHTS
    TARGET_LAG = '1 minute'
    WAREHOUSE = COMPUTE_WH
AS
SELECT 
    b.GRADE AS CREDIT_GRADE,
    COUNT(*) AS TOTAL_CUSTOMERS,
    ROUND(AVG(i.CHARGES), 2) AS AVG_MEDICAL_COSTS,
    ROUND(AVG(
        CASE WHEN b.ANNUAL_INC > 0 THEN (i.CHARGES / b.ANNUAL_INC) * 100 
        ELSE 0 END
    ), 2) AS COST_TO_INCOME_RATIO,
    MAX(CURRENT_TIMESTAMP()) as LAST_UPDATED
FROM BANK_DB.DATA.LOAN_CUSTOMERS b
JOIN INSURER_DB.DATA.MEDICAL_CLIENTS i 
    ON b.EMAIL = i.EMAIL
GROUP BY b.GRADE;

-- 3. MACHINE LEARNING SETUP
-- Create View for Training Data
CREATE OR REPLACE VIEW CLEAN_ROOM_DB.ANALYSIS.ML_TRAINING_DATASET AS
SELECT 
    b.ANNUAL_INC, i.AGE, i.BMI, i.CHARGES AS MEDICAL_COSTS,
    CASE WHEN b.LOAN_STATUS = 'Default' THEN 1 ELSE 0 END AS IS_DEFAULT
FROM BANK_DB.DATA.LOAN_CUSTOMERS b
JOIN INSURER_DB.DATA.MEDICAL_CLIENTS i ON b.EMAIL = i.EMAIL;

-- Create Stage for Model Artifacts
CREATE STAGE IF NOT EXISTS CLEAN_ROOM_DB.ANALYSIS.MODEL_STAGE;

-- 4. TRAIN MODEL PROCEDURE (Snowpark Python)
CREATE OR REPLACE PROCEDURE CLEAN_ROOM_DB.ANALYSIS.TRAIN_RISK_MODEL()
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
PACKAGES = ('snowflake-snowpark-python', 'pandas', 'scikit-learn', 'joblib')
HANDLER = 'train_model'
AS
$$
import snowflake.snowpark as snowpark
import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib
import os

def train_model(session):
    df = session.table("CLEAN_ROOM_DB.ANALYSIS.ML_TRAINING_DATASET").to_pandas()
    X = df[['ANNUAL_INC', 'AGE', 'BMI', 'MEDICAL_COSTS']]
    y = df['IS_DEFAULT']
    model = LogisticRegression()
    model.fit(X, y)
    
    model_dir = '/tmp'
    model_file = os.path.join(model_dir, 'risk_model.joblib')
    joblib.dump(model, model_file)
    session.file.put(model_file, "@CLEAN_ROOM_DB.ANALYSIS.MODEL_STAGE", auto_compress=False, overwrite=True)
    return "Model Trained and Saved."
$$;

-- 5. DEPLOY PREDICTION FUNCTION (UDF)
-- Real-time inference engine used by the Streamlit App
CREATE OR REPLACE FUNCTION CLEAN_ROOM_DB.ANALYSIS.PREDICT_RISK(income FLOAT, age FLOAT, bmi FLOAT, charges FLOAT)
RETURNS FLOAT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
PACKAGES = ('pandas', 'scikit-learn', 'joblib')
IMPORTS = ('@CLEAN_ROOM_DB.ANALYSIS.MODEL_STAGE/risk_model.joblib')
HANDLER = 'predict_risk_handler'
AS
$$
import sys
import pandas as pd
import joblib
import os

model = None
def predict_risk_handler(income, age, bmi, charges):
    global model
    if model is None:
        import_dir = sys._xoptions["snowflake_import_directory"]
        model_path = os.path.join(import_dir, "risk_model.joblib")
        model = joblib.load(model_path)
    
    features = pd.DataFrame([[income, age, bmi, charges]], columns=['ANNUAL_INC', 'AGE', 'BMI', 'MEDICAL_COSTS'])
    return model.predict_proba(features)[0][1]
$$;