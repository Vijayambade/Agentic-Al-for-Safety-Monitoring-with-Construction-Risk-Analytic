import streamlit as st
from utils.ollama_client import check_ollama_running, list_models, generate


def render():
    st.header("🚜 Equipment")
    st.info("Equipment availability, maintenance, and utilization tracking will be added here.")
    st.dataframe({"Equipment": ["Excavator", "Crane", "Loader"], "Status": ["Available", "In use", "Maintenance"]})

    st.markdown("---")
    st.subheader("🤖 AI Helper")
    if not check_ollama_running():
        st.warning("The local AI server is not running. Start it with 'ollama serve' and pull a model first.")
        return

    models = list_models() or ["llama3.1"]
    model = st.selectbox("Model", models, key="eq_model")
    prompt = st.text_area(
        "Ask for equipment guidance",
        "Suggest how to optimize equipment utilization and reduce downtime on a busy site.",
        key="eq_prompt",
    )
    if st.button("Generate insight", key="eq_generate"):
        with st.spinner("Thinking..."):
            response = generate(prompt, model=model, system="You are a construction equipment advisor. Provide concise, practical recommendations.")
        st.markdown(response)
