import streamlit as st
from utils.ollama_client import check_ollama_running, list_models, generate


def render():
    st.header("📷 Safety Monitoring")
    st.info("Safety observations, incident logs, and inspection checklists will be added here.")
    st.checkbox("Daily safety briefing completed")
    st.checkbox("PPE inspection completed")

    st.markdown("---")
    st.subheader("🤖 AI Helper")
    if not check_ollama_running():
        st.warning("The local AI server is not running. Start it with 'ollama serve' and pull a model first.")
        return

    models = list_models() or ["llama3.1"]
    model = st.selectbox("Model", models, key="sm_model")
    prompt = st.text_area(
        "Ask for safety guidance",
        "Suggest practical safety actions for a site with repeated near-miss incidents.",
        key="sm_prompt",
    )
    if st.button("Generate insight", key="sm_generate"):
        with st.spinner("Thinking..."):
            response = generate(prompt, model=model, system="You are a construction safety advisor. Provide concise, practical recommendations.")
        st.markdown(response)
