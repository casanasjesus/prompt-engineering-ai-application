import streamlit as st
import pandas as pd

from src.llm.chat_with_data.sql_agent import SQLAgent
from src.llm.chat_with_data.sql_executor import SQLExecutor
from src.llm.chat_with_data.visualization import create_bar_plot
from src.llm.chat_with_data.guardrails import detect_prompt_injection

def render_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if "sql" in msg:
                st.code(msg["sql"], language="sql")

            if "df" in msg:
                st.dataframe(msg["df"])

    # Chat input
    question = st.chat_input("Ask a question about your data...")

    if question:

        # Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        # Guardrail check
        if detect_prompt_injection(question):

            with st.chat_message("assistant"):
                st.error("⚠️ Prompt injection detected.")

            return

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                agent = SQLAgent(
                    llm_client=st.session_state.llm,
                    schema=st.session_state.schema
                )

                sql_placeholder = st.empty()

                sql_text = ""

                for chunk in agent.generate_sql_stream(question):

                    sql_text += chunk

                    sql_placeholder.code(sql_text, language="sql")

                sql = sql_text

                executor = SQLExecutor()

                df = None

                try:

                    df = executor.run_query(sql)

                    st.dataframe(df)

                    fig = create_bar_plot(df)

                    if fig:
                        st.pyplot(fig)

                except Exception as e:

                    st.error(f"Query failed: {str(e)}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": "Here are the results",
            "sql": sql,
            "df": df if df is not None else pd.DataFrame()
        })