import streamlit as st
from utils.ollama_client import check_ollama_running, list_models, generate


def render():
    st.header("📁 Project Management")
    st.info("Project planning, schedule tracking, and milestone management will be added here.")
    st.text_area("Project notes", "Capture site milestones, deliverables, and progress updates.")

    st.markdown("---")
    st.subheader("🤖 AI Helper")
    if not check_ollama_running():
        st.warning("The local AI server is not running. Start it with 'ollama serve' and pull a model first.")
        return

    models = list_models() or ["llama3.1"]
    model = st.selectbox("Model", models, key="pm_model")
    prompt = st.text_area(
        "Ask for project guidance",
        "Suggest a practical weekly plan for a construction project with delayed procurement and rising labor costs.",
        key="pm_prompt",
    )
    if st.button("Generate insight", key="pm_generate"):
        with st.spinner("Thinking..."):
            response = generate(prompt, model=model, system="You are a construction project advisor. Provide concise, practical recommendations.")
        st.markdown(response)
