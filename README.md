# 🛡️ SafeHaven: AI-Powered Privacy Clean Room

### 🏆 Built for AI for Good Hackathon 2025

**SafeHaven** is a privacy-first analytics platform that enables
financial institutions (Banks) and Insurance providers to securely
collaborate. It uses a **Snowflake Data Clean Room** to join sensitive
datasets without exposing PII, and applies **Snowpark ML** to predict
customer risk in real-time.

------------------------------------------------------------------------

## 🚨 The Problem

Banks and Insurers possess highly correlated data---financial stress
often leads to health decline, and vice-versa. However, strict privacy
regulations (GDPR, CCPA) and competitive secrecy prevent them from
sharing raw customer data. \* **Result:** Both industries operate with
"Risk Blind Spots." \* **Consequence:** Higher default rates and
inaccurate insurance premiums.

## 💡 The Solution

SafeHaven acts as a "Trusted Third Party" bridge. It ingests data from
both silos, hashes the identities (SHA-256), and allows for **Predictive
Risk Modeling** on the combined dataset without ever decrypting the
user's identity.

------------------------------------------------------------------------

## ⚙️ How It Works (Architecture)

``` mermaid
graph TD
    A[Bank Database] -->|Hashed Emails| C{Snowflake Clean Room}
    B[Insurance Database] -->|Hashed Emails| C
    
    C -->|Aggregated Data| D[Dynamic Tables]
    D -->|Live Updates| E[Streamlit Dashboard]
    
    C -->|Training Data| F[Snowpark ML Training]
    F -->|Model Artifact| G[Logistic Regression Model]
    
    G -->|UDF Inference| E
    
    subgraph "Generative AI Layer"
    D --> H[Snowflake Cortex]
    H -->|Natural Language Summary| E
    end

---

## 🚀 Key Features
1. 🔒 Privacy-First Clean Room
Joins datasets using SHA-256 hashed email keys.

Aggregates data to the CREDIT_GRADE level to prevent re-identification.

Implements Row Access Policies to ensure raw PII never leaves the secure schema.

2. 🧠 Predictive AI Engine (Snowpark ML)
Training: We trained a Logistic Regression model inside Snowflake to identify correlations between Medical Costs and Loan Defaults.

Inference: Deployed a Python UDF (PREDICT_RISK) that scores new customers instantly (0-100% Risk Probability) as they enter the system.

3. ⚡ Real-Time "Chaos" Simulation
Includes a "Simulation Engine" that injects synthetic high-risk data (e.g., a sudden market crash or pandemic event).

Powered by Snowflake Dynamic Tables (1-minute lag) to instantly reflect these changes in the dashboard.

4. 🤖 Generative AI Insights
Integrated Snowflake Cortex (Llama-3) to act as an automated Risk Officer.

Reads complex SQL aggregations and generates plain-English executive summaries for non-technical stakeholders.

---

## 🛠️ Technology Stack

| Component | Technology | Use Case |
| :--- | :--- | :--- |
| **Database** | **Snowflake Data Cloud** | Core storage and compute. |
| **Machine Learning** | **Snowpark Python** | Training Scikit-Learn models & deploying UDFs. |
| **Generative AI** | **Snowflake Cortex** | Llama-3-8b model for text summarization. |
| **Data Pipeline** | **Dynamic Tables** | Automated, declarative real-time ELT. |
| **Frontend** | **Streamlit** | Interactive dashboard & simulation UI. |
| **Visualization** | **Plotly** | Advanced interactive charting. |

---

## 💻 How to Run This Project

### Prerequisites
* Python 3.9+
* A Snowflake Account (Trial is fine)

### 1. Clone the Repo
```bash
git clone [https://github.com/YourUsername/SafeHaven.git](https://github.com/YourUsername/SafeHaven.git)
cd SafeHaven
```

### 2. Install Dependencies

``` bash
pip install -r requirements.txt
```

### 3. Setup Snowflake Environment

Run the contents of setup.sql in your Snowflake Worksheet. This script
will:

1.  Create the Databases (BANK_DB, INSURER_DB, CLEAN_ROOM_DB).

2.  Create the Dynamic Tables.

3.  Train the Machine Learning Model.

4.  Deploy the PREDICT_RISK UDF.

### 4. Configure Secrets

Create a .streamlit/secrets.toml file:

``` bash
[connections.snowflake]
user = "YOUR_USER"
password = "YOUR_PASSWORD"
account = "YOUR_ACCOUNT_LOCATOR"
warehouse = "COMPUTE_WH"
role = "ACCOUNTADMIN"
```

### 5. Run the App

``` bash
streamlit run app.py
```
