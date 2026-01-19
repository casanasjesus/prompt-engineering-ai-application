import sys
import os
import streamlit as st

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from sections.data_generation import render_data_generation
from dotenv import load_dotenv

load_dotenv()

# Page configuration

st.set_page_config(
    page_title="Data Assistant",
    page_icon="📊",
    layout="wide",
)

# App title

st.title("📊 Data Assistant")

st.markdown(
    """
    Welcome to **Data Assistant**  
    Generate data or talk to your database using natural language.
    """
)

# Session state initialization

if "schema" not in st.session_state:
    st.session_state.schema = None

if "data" not in st.session_state:
    st.session_state.data = None

if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

# Sidebar navigation

st.sidebar.title("Data Assistant")

page = st.sidebar.radio(
    "Navigation",
    options=["Data Generation", "Talk to your data"],
)

# Page routing

if page == "Data Generation":
    st.header("🧪 Data Generation")
    render_data_generation()

elif page == "Talk to your data":
    st.header("💬 Talk to your data")



