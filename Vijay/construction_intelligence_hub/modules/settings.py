import streamlit as st
from utils.ollama_client import check_ollama_running, list_models, generate


def render():
    st.header("⚙️ Settings")
    st.info("Application preferences and integration settings will be configured here.")
    st.checkbox("Enable AI suggestions")
    st.text_input("Default project name", "North Tower")

    st.markdown("---")
    st.subheader("🤖 AI Helper")
    if not check_ollama_running():
        st.warning("The local AI server is not running. Start it with 'ollama serve' and pull a model first.")
        return

    models = list_models() or ["llama3.1"]
    model = st.selectbox("Model", models, key="set_model")
    prompt = st.text_area(
        "Ask for configuration guidance",
        "Suggest the best default setup for a construction management dashboard with AI support.",
        key="set_prompt",
    )
    if st.button("Generate insight", key="set_generate"):
        with st.spinner("Thinking..."):
            response = generate(prompt, model=model, system="You are a construction software configuration advisor. Provide concise, practical recommendations.")
        st.markdown(response)
