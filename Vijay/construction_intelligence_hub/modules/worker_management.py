import streamlit as st
from utils.ollama_client import check_ollama_running, list_models, generate


def render():
    st.header("👷 Worker Management")
    st.info("Worker roster, attendance, certifications, and skill tracking will be added here.")
    st.dataframe({"Worker": ["A. Khan", "R. Patel"], "Role": ["Foreman", "Electrician"], "Status": ["Active", "On leave"]})

    st.markdown("---")
    st.subheader("🤖 AI Helper")
    if not check_ollama_running():
        st.warning("The local AI server is not running. Start it with 'ollama serve' and pull a model first.")
        return

    models = list_models() or ["llama3.1"]
    model = st.selectbox("Model", models, key="wm_model")
    prompt = st.text_area(
        "Ask for workforce guidance",
        "Suggest ways to reduce labor shortages and improve site productivity.",
        key="wm_prompt",
    )
    if st.button("Generate insight", key="wm_generate"):
        with st.spinner("Thinking..."):
            response = generate(prompt, model=model, system="You are a construction workforce advisor. Provide concise, practical recommendations.")
        st.markdown(response)
