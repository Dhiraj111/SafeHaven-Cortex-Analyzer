import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        .stMetric {
            background-color: #1e1e1e;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #333;
        }
        div[data-testid="stExpander"] {
            border: 1px solid #444;
            border-radius: 5px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

def setup_page():
    st.set_page_config(
        layout="wide", 
        page_title="SafeHaven Enterprise", 
        page_icon="🛡️",
        initial_sidebar_state="expanded"
    )
    apply_custom_css()