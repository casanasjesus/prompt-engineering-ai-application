import streamlit as st
import json

def render_data_generation():
    # Prompt
    prompt = st.text_area(
        label="Prompt",
        placeholder="Describe the data you want to generate...",
        height=120
    )

    # Upload schema
    uploaded_file = st.file_uploader(
        label="Upload DDL Schema",
        type=["sql", "json"]
    )

    schema = None

    if uploaded_file:
        if uploaded_file.name.endswith(".json"):
            schema = json.load(uploaded_file)
            st.success("JSON schema loaded successfully")

        elif uploaded_file.name.endswith(".sql"):
            sql_text = uploaded_file.read().decode("utf-8")
            schema = sql_text
            st.success("SQL schema loaded successfully")

    return prompt, schema
