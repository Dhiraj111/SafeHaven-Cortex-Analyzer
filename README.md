# 🛡 SafeHaven – AI for Early Financial & Healthcare Stress Detection

**[Live Demo 🚀](https://safehaven-cortex-analyzer-jpb9mt7nbvs2usmhatykgg.streamlit.app/)**

## AI Bharat Hackathon Submission

---

## Problem Statement 🇮🇳

In India, **millions of families silently fall into financial distress due to sudden healthcare expenses**.  
This stress often leads to:
- Missed loan payments  
- Loan defaults  
- Insurance claim rejections  
- Long-term financial exclusion  

### The Core Problem
Today, **financial data and healthcare data exist in silos**.  
Institutions usually detect distress **only after damage is done** — when a customer defaults or a claim fails.

By that time:
- Families are already in crisis  
- Institutions incur losses  
- Trust breaks down  

---

## Our Solution 💡

**SafeHaven** is a **privacy-safe AI-powered dashboard** that detects **early signs of combined financial and healthcare stress** at a **population and group level**, without exposing personal identities.

It enables institutions to:
- Identify rising stress **early**
- Understand *where* and *why* risk is increasing
- Take **proactive, human-led support actions** instead of reactive penalties

This is **AI for prevention**, not punishment.

---

## Why This Matters for India 🇮🇳

- Healthcare costs are one of the **top reasons for household debt** in India  
- Many families live paycheck-to-paycheck  
- A single medical emergency can push households into long-term financial instability  

SafeHaven helps institutions **act before families fall into irreversible distress**.

---

## How AI Is Used 🤖 (Clearly & Responsibly)

AI in SafeHaven is used to **support humans**, not replace them.

### AI Capabilities
- Estimates **stress probability** based on aggregated financial and medical indicators  
- Performs **“what-if” simulations** (e.g., what if medical costs increase by 20–60%)  
- Generates **plain-language insights** for decision-makers  

### What AI Does NOT Do
- ❌ No automatic loan rejection  
- ❌ No automatic claim denial  
- ❌ No individual-level surveillance  

AI provides **signals**, humans make decisions.

---

## Key Features 🚀

### 📊 Executive Risk View
- Shows how many people are affected by rising stress
- Adjustable “high-risk threshold” for policy flexibility
- Geographic view of medical cost concentration
- Risk vs population size comparison across groups

**Helps answer:**  
> “Where should we focus help first?”

---

### 🕵 Privacy-Safe Investigator View
- Masked user identifiers (no names, no phone numbers)
- Combined financial + healthcare stress indicators
- AI-assisted risk probability
- Stress testing for future scenarios

**Helps answer:**  
> “Is this case stable, fragile, or at risk?”

---

### 🤖 AI Analyst Assistant
- Ask questions in natural language
- Get summaries of trends and anomalies
- Fallback logic ensures system reliability

**Helps answer:**  
> “What should decision-makers care about right now?”

---

### ⚡ Scenario Simulation (Chaos Engine)
- Simulates recession, health crisis, or economic boom
- Uses **synthetic data only**
- No impact on real users

**Helps answer:**  
> “Are we prepared if things get worse?”

---

## Privacy & Ethics by Design 🔐

SafeHaven is built with **strong ethical and privacy principles**:

- No personally identifiable information (PII) shown
- Only masked reference IDs
- Group-level analysis instead of individual profiling
- Human-in-the-loop decision making
- Clear separation between analysis and customer contact

This makes the system **regulation-friendly and socially responsible**.

---

## How It Fits Into Real Systems 🏗

Data Sources (Aggregated)
↓
SafeHaven AI Dashboard
↓
CRM / Support Systems (e.g., Salesforce)
↓
Human Support Teams
↓
Customer Outreach & Assistance

---


SafeHaven **does not replace existing systems** — it enhances them with early intelligence.

---

## Impact Potential 🌱

If deployed at scale, SafeHaven can:
- Reduce loan defaults caused by medical emergencies
- Improve fairness in credit and insurance decisions
- Enable proactive customer support
- Strengthen financial inclusion
- Build trust between institutions and citizens

This aligns strongly with **AI for Social Good**.

---

## Technology Stack 🧠

- **App Framework:** Streamlit  
- **Data Processing:** Pandas  
- **Visualizations:** Plotly  
- **AI & ML:** Predictive models + LLM-based analysis  
- **Data:** Public datasets (Kaggle) for prototype demonstration  

---

## Current Status 🚧

This project is a **working prototype (PoC)** built for the **AI Bharat Hackathon**.

It focuses on:
- Problem clarity  
- AI logic  
- Ethical design  
- Real-world feasibility  

It intentionally avoids complex authentication or production deployment details to prioritize **impact and clarity**.

---

## Why This Is an AI Bharat–Ready Solution 🇮🇳

✔ Addresses a real Indian social problem  
✔ Uses AI responsibly  
✔ Protects privacy  
✔ Human-centered design  
✔ Scalable and feasible  
✔ Clear social impact  

---

## 📊 Data & Architecture
The simulation engine is powered by real-world datasets to ensure statistical validity:
* **Financial Data:** Modeled on the [Lending Club Loan Dataset](https://www.kaggle.com/datasets/wordsforthewise/lending-club) (Kaggle).
* **Healthcare Data:** Modeled on the [Medical Cost Personal Datasets](https://www.kaggle.com/datasets/mirichoi0218/insurance) (Kaggle).

## One-Line Summary

> **SafeHaven uses AI to detect early financial and healthcare stress in India — so institutions can help families before crisis strikes.**

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
streamlit run main.py
```
