import streamlit as st
import json

def render_advanced_parameters():
    st.subheader("Advanced Parameters")

    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.5

    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 100

    st.slider(
        label="Temperature",
        min_value=0.0,
        max_value=1.0,
        step=0.05,
        key="temperature"
    )

    st.number_input(
        label="Max Tokens",
        min_value=10,
        max_value=2000,
        step=10,
        key="max_tokens"
    )

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

    render_advanced_parameters()

    # Init state
    if "generated_data" not in st.session_state:
        st.session_state.generated_data = None

    if "error" not in st.session_state:
        st.session_state.error = None

    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False

    # Generate button
    if st.button("🚀 Generate Data", type="primary"):
        st.session_state.error = None
        st.session_state.generated_data = None

        if not prompt.strip():
            st.session_state.error = "Prompt is required."
        else:
            with st.spinner("Generating data..."):
                st.session_state.is_generating = True

                try:
                    st.session_state.generated_data = generate_data(
                        prompt=prompt,
                        schema=schema,
                        temperature=st.session_state.temperature,
                        max_tokens=st.session_state.max_tokens,
                    )
                except Exception as e:
                    st.session_state.error = str(e)

                st.session_state.is_generating = False

    # Error message
    if st.session_state.error:
        st.error(st.session_state.error)

    # Result
    if st.session_state.generated_data:
        st.subheader("Generated Output")
        st.json(st.session_state.generated_data)

    return {
        "prompt": prompt,
        "schema": schema,
        "temperature": st.session_state.temperature,
        "max_tokens": st.session_state.max_tokens,
    }

def generate_data(prompt, schema, temperature, max_tokens):
    # Simulación temporal
    return {
        "status": "success",
        "data": [
            {"id": 1, "name": "Example A"},
            {"id": 2, "name": "Example B"},
        ],
        "meta": {
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    }

