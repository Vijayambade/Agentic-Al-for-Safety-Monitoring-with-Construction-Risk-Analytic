import streamlit as st
from utils.ollama_client import check_ollama_running, list_models, generate


def render():
    st.header("📄 Reports")
    st.info("Daily, weekly, and executive reports will be generated here.")
    st.button("Generate summary report")

    st.markdown("---")
    st.subheader("🤖 AI Helper")
    if not check_ollama_running():
        st.warning("The local AI server is not running. Start it with 'ollama serve' and pull a model first.")
        return

    models = list_models() or ["llama3.1"]
    model = st.selectbox("Model", models, key="rep_model")
    prompt = st.text_area(
        "Ask for report guidance",
        "Draft a concise executive summary for a construction project with cost overruns and schedule delays.",
        key="rep_prompt",
    )
    if st.button("Generate insight", key="rep_generate"):
        with st.spinner("Thinking..."):
            response = generate(prompt, model=model, system="You are a construction reporting advisor. Provide concise, professional report language.")
        st.markdown(response)
