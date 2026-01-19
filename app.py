import streamlit as st

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
    st.info("Data generation UI coming next...")

elif page == "Talk to your data":
    st.header("💬 Talk to your data")
    st.info("NL to SQL UI coming next...")
