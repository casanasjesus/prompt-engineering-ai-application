import sys
import os
import streamlit as st

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.llm.gemini_client import GeminiClient
from ui.sections.data_generation.data_generation import render_data_generation
from ui.sections.chat_with_data.chat_with_data import render_chat
from streamlit_option_menu import option_menu
from dotenv import load_dotenv

load_dotenv()

# Initialize session state
if "llm" not in st.session_state:
    st.session_state.llm = GeminiClient()

if "schema" not in st.session_state:
    st.session_state.schema = {}

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

dataGeneration = "Data Generation"
talkToYourData = "Talk to your data"

with st.sidebar:
    selected = option_menu(
        "Navigation",
        [dataGeneration, talkToYourData],
        icons=["database", "chat"],
        menu_icon="cast",
        default_index=0
    )

page = selected

# Page routing

if page == dataGeneration:
    st.header("🧪 Data Generation")
    render_data_generation()

elif page == talkToYourData:
    st.header("💬 Talk to your data")
    render_chat()



