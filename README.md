# 🛡 SafeHaven Risk Intelligence Dashboard

## Overview

**SafeHaven** is an internal **risk intelligence dashboard** designed to help organizations detect **early signs of financial and healthcare stress** across customer populations — **without exposing personal identities**.

The dashboard combines aggregated financial and medical indicators to highlight **where risk is rising**, enabling teams to take **proactive, human-led actions** instead of reacting after defaults, claim failures, or crises occur.

This project is built as an **enterprise internal tool**, not a consumer application.

---

## Why This Dashboard Is Needed

In most real-world organizations:

- Financial data and healthcare data exist in silos  
- Risk is detected only after damage is done  
- Decisions are reactive rather than preventive  
- Privacy constraints limit meaningful analysis  

As a result:
- Customers fall into distress unexpectedly  
- Institutions face higher losses and compliance pressure  
- Trust between customers and institutions erodes  

**SafeHaven addresses this gap by providing early, privacy-safe risk signals at a population and group level — not personal surveillance.**

---

## Who This Is For

### Primary Users (Direct Users)
- Risk analysts  
- Credit risk teams  
- Insurance risk analysts  
- Compliance and strategy teams  

### Secondary Users (Action Takers)
- Customer support teams  
- Relationship managers  
- Claims or outreach teams (via CRM integration)

### Indirect Beneficiaries
- Loan customers  
- Insurance policy holders  
- Employees and families  

> End customers never log into this system — they benefit from better, earlier decisions made upstream.

---

## Key Features

### 📊 Executive Risk View
- Population-level risk metrics
- Adjustable high-risk threshold
- Geographic concentration of medical exposure
- Risk vs volume correlation across credit groups

**Purpose:**  
Help leaders decide *where attention and resources are needed first*.

---

### 🕵 Customer Investigator View (Privacy-Safe)
- Masked user identifiers (no PII exposed)
- Financial and medical stress indicators
- AI-generated risk probability
- Stress testing (“What if medical costs increase?”)

**Purpose:**  
Support fair, explainable, human decisions for high-risk cases.

---

### 🤖 AI Analyst Agent
- Natural-language questions over aggregated data
- Executive summaries and trend explanations
- Fail-safe responses if AI services are unavailable

**Purpose:**  
Reduce analysis time and cognitive load for decision-makers.

---

### ⚡ Simulation (Chaos Engine)
- Injects synthetic scenarios (economic recession, health crisis, market boom)
- Tests system behavior under stress
- Uses only synthetic data — no real customer impact

**Purpose:**  
Allow teams to practice decision-making safely before real-world events.

---

## Privacy by Design

SafeHaven is built with **privacy-first and compliance-friendly principles**:

- No names, phone numbers, or emails displayed
- Masked reference IDs only
- Group-level analysis instead of individual surveillance
- Human-in-the-loop decision making
- No automated approvals or rejections

Identity resolution and customer contact are handled **outside this application**, typically within CRM systems such as Salesforce.

---

## How This Fits Into an Enterprise System

Data Warehouse (Snowflake)
↓
SafeHaven Dashboard (Risk Detection)
↓
CRM / Case System (e.g. Salesforce)
↓
Human Support Teams
↓
Customer Outreach & Support

---


SafeHaven **does not replace CRM systems** — it functions as a **risk signal generator** that feeds existing workflows.

---

## Technology Stack

- **Application Framework:** Streamlit  
- **Data Processing:** Pandas  
- **Visualizations:** Plotly  
- **Data Platform:** Snowflake (Aggregated / Clean Room Views)  
- **AI & ML:** Snowflake Cortex (Risk prediction & LLMs)

---

## Current Status

This project is a **working internal prototype (PoC)** that demonstrates:

- End-to-end data flow
- Risk interpretation logic
- Privacy-safe investigation workflows
- Enterprise integration patterns

The application intentionally **does not include public signup or authentication**, as it is designed for controlled, internal enterprise usage.

---

## Future Enhancements

- Salesforce CRM integration (Case / Task creation)
- Role-based access (Executive, Analyst)
- Decision audit logs
- Enterprise SSO (Okta / Azure AD / Salesforce Identity)
- Configurable alert routing and escalation

---

## Project Intent

This project was built to:

- Demonstrate enterprise system and product thinking
- Explore ethical and privacy-safe use of AI in risk domains
- Showcase integration between data platforms and CRM systems
- Serve as a portfolio-grade example of **decision-support software**

---

## One-Line Summary

> **SafeHaven helps organizations act early and fairly when financial and healthcare stress begins to rise — without compromising individual privacy.**

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
