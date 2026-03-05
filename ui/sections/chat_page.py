import streamlit as st

from src.llm.chat_with_data.sql_agent import SQLAgent
from src.llm.chat_with_data.sql_executor import SQLExecutor
from src.llm.chat_with_data.visualization import create_bar_plot
from src.llm.chat_with_data.guardrails import detect_prompt_injection
from src.llm.gemini_client import GeminiClient

def render_chat_page(schema):
    st.title("💬 Talk to your Data")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Ask a question about your data...")

    if not user_input:
        return

    # guardar mensaje usuario
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    st.chat_message("user").write(user_input)

    # guardrails
    if detect_prompt_injection(user_input):
        st.chat_message("assistant").write(
            "⚠️ Query blocked due to security policy."
        )
        return

    # LLM
    client = GeminiClient()

    agent = SQLAgent(client, schema)

    sql_query = agent.generate_sql(user_input)

    st.chat_message("assistant").code(sql_query, language="sql")

    # ejecutar SQL
    executor = SQLExecutor()

    try:

        df = executor.run_query(sql_query)

        st.dataframe(df)

        fig = create_bar_plot(df)

        if fig:
            st.pyplot(fig)

    except Exception as e:

        st.error(f"SQL execution failed: {e}")