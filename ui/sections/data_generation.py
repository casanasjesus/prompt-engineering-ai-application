import streamlit as st
import json
import pandas as pd
import io
import zipfile

from src.llm.gemini_client import GeminiClient
from src.llm.prompt_builder import build_generation_prompt
from src.llm.response_parser import parse_llm_response
from src.utils.table_detector import detect_table_name
from src.db.sqlite_manager import create_table_if_not_exists, insert_rows

def render_advanced_parameters():
    st.subheader("Advanced Parameters")

    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.5

    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 2500

    col1, col2 = st.columns(2)

    with col1:
        st.slider(
            label="Temperature",
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            key="temperature"
        )

    with col2:
        st.number_input(
            label="Max Tokens",
            min_value=10,
            max_value=5000,
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
        label="Upload Schema",
        type=["DDL", "json", "sql"]
    )

    schema = None

    if uploaded_file:
        if uploaded_file.name.endswith(".json"):

            try:
                schema = json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Invalid JSON file")

            st.session_state.schema = schema
            st.success("JSON schema loaded successfully")

        elif uploaded_file.name.endswith(".sql"):
            sql_text = uploaded_file.read().decode("utf-8")
            schema = sql_text
            st.session_state.schema = schema
            st.success("SQL schema loaded successfully")

    render_advanced_parameters()

    # Init state
    if "generated_data" not in st.session_state:
        st.session_state.generated_data = None

    if "error" not in st.session_state:
        st.session_state.error = None

    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False

    # Validate inputs
    prompt_valid = bool(prompt and prompt.strip())
    file_valid = uploaded_file is not None
    can_generate = prompt_valid and file_valid

    # Generate button
    if st.button(
        "🚀 Generate Data",
        type="primary",
        disabled=not can_generate
    ):
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

        tab_table, tab_preview, tab_raw = st.tabs(
            ["📋 Table", "👀 Preview", "🧾 Raw JSON"]
        )

        data = st.session_state.generated_data

        # ---------- TABLE ----------
        with tab_table:
            rows = data.get("data")

            if isinstance(rows, list) and len(rows) > 0:
                df = pd.DataFrame(rows)
                st.dataframe(df, width='stretch')
            else:
                st.info("No tabular data available.")

        # ---------- PREVIEW ----------
        with tab_preview:
            st.json(data)

        # ---------- RAW ----------
        with tab_raw:
            st.code(
                json.dumps(data, indent=2),
                language="json"
            )

        col1, col2, col3 = st.columns(3)
        rows = st.session_state.generated_data.get("data")

        # ---------- DOWNLOAD ----------
        with col1:
            st.download_button(
            label="⬇ Download JSON",
            data=json.dumps(data, indent=2),
            file_name="generated_data.json",
            mime="application/json",
            width='stretch'
        )
            
        # ------------------ EXPORT ------------------
        with col2:
            if isinstance(rows, list) and len(rows) > 0:
                csv_content = export_csv(rows)

            st.download_button(
                label="⬇ Download CSV",
                data=csv_content,
                file_name="generated_data.csv",
                mime="text/csv",
                width='stretch',
            )
        
        # ZIP export (prepared for multi-table)
        with col3:
            zip_data = {
            "generated_data": rows
        }

            zip_bytes = export_zip(zip_data)

            st.download_button(
                label="⬇ Download ZIP",
                data=zip_bytes,
                file_name="generated_data.zip",
                mime="application/zip",
                width='stretch',
            )

    return {
        "prompt": prompt,
        "schema": schema,
        "temperature": st.session_state.temperature,
        "max_tokens": st.session_state.max_tokens,
    }

def generate_data(prompt, schema, temperature, max_tokens):
    client = GeminiClient(
        temperature=temperature,
        max_tokens=max_tokens,
    )

    llm_prompt = build_generation_prompt(
        schema=schema,
        user_prompt=prompt,
        rows_per_table=10,
    )

    try:
        raw_response = client.generate_json(llm_prompt)
        data = parse_llm_response(raw_response)

        if "data" not in data:
            raise ValueError("JSON does not contain 'data' key")
        
        rows = data["data"]

        table_name = detect_table_name(prompt, schema)

        create_table_if_not_exists(table_name, rows)
        insert_rows(table_name, rows)

        return {
            "status": "success",
            "data": rows
        }

    except Exception as e:
        msg = str(e)

        print("\n" + "=" * 80)
        print("MESSAGE EXCEPTION")
        print(msg)
        print("=" * 80)

        if "quota" in msg.lower() or "resource_exhausted" in msg.lower():
            raise RuntimeError(
                "Gemini quota exceeded. Please wait or upgrade your plan."
            )

        raise RuntimeError(
            "The AI returned an invalid response.\n"
            "Try simplifying your prompt or reducing max tokens."
        )

def export_csv(data: list) -> str:
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def export_zip(data_dict: dict) -> bytes:
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for table_name, rows in data_dict.items():
            df = pd.DataFrame(rows)
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            zipf.writestr(f"{table_name}.csv", csv_bytes)

    buffer.seek(0)
    return buffer.read()

