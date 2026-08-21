import streamlit as st
from utils.ollama_client import check_ollama_running, list_models, generate


def render():
    st.header("🗺️ Site Monitoring")
    st.info("Site activity monitoring, weather updates, and geotagged progress will be added here.")
    st.map()

    st.markdown("---")
    st.subheader("🤖 AI Helper")
    if not check_ollama_running():
        st.warning("The local AI server is not running. Start it with 'ollama serve' and pull a model first.")
        return

    models = list_models() or ["llama3.1"]
    model = st.selectbox("Model", models, key="site_model")
    prompt = st.text_area(
        "Ask for site guidance",
        "Suggest the best response plan for bad weather and reduced site productivity.",
        key="site_prompt",
    )
    if st.button("Generate insight", key="site_generate"):
        with st.spinner("Thinking..."):
            response = generate(prompt, model=model, system="You are a construction site operations advisor. Provide concise, practical recommendations.")
        st.markdown(response)
