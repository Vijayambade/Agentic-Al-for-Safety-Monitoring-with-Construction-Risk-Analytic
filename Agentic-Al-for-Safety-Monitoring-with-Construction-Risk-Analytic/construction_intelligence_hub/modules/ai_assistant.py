import streamlit as st
from utils.ollama_client import chat, generate, check_ollama_running, list_models
from utils.guardrails import check_construction_guardrail
import PyPDF2
import io

SYSTEM_PROMPT = (
    "You are a helpful assistant embedded in a Construction Intelligence Hub. "
    "You answer questions about construction cost estimation, scheduling, materials, "
    "regulations, and project management. Keep answers practical and concise."
)


def _extract_text(uploaded_file) -> str:
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return uploaded_file.read().decode("utf-8", errors="ignore")


def render():
    st.header("🤖 AI Assistant")

    if not check_ollama_running():
        st.error(
            "The local AI server is not reachable at `localhost:11434`. Start it with `ollama serve` "
            "and make sure you've pulled a model, e.g. `ollama pull llama3.1`."
        )
        return

    models = list_models()
    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox("Model", models if models else ["llama3.1"])
    with col2:
        enable_guardrails = st.checkbox(
            "Enable Construction Guardrails",
            value=True,
            help="Block off-topic queries and document processing using local AI guardrails.",
        )

    tab1, tab2 = st.tabs(["💬 Chat", "📄 Document Analyzer"])

    with tab1:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

        for msg in st.session_state.chat_history[1:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about estimates, materials, scheduling..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Guardrails check
            is_allowed = True
            refusal_msg = ""
            if enable_guardrails:
                with st.spinner("Checking guardrails..."):
                    is_allowed, refusal_msg = check_construction_guardrail(prompt, model=model)
            
            with st.chat_message("assistant"):
                if not is_allowed:
                    reply = refusal_msg
                    st.warning(reply)
                else:
                    with st.spinner("Thinking..."):
                        reply = chat(st.session_state.chat_history, model=model)
                    st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

        if st.button("Clear chat"):
            st.session_state.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
            st.rerun()

    with tab2:
        st.caption("Upload a spec sheet, RFP, or site report (.txt or .pdf) for an AI summary.")
        doc = st.file_uploader("Upload document", type=["txt", "pdf"], key="doc_upload")
        if doc is not None:
            text = _extract_text(doc)
            st.text_area("Extracted text (preview)", text[:2000], height=200)

            if st.button("Analyze Document"):
                # Guardrails check for document
                is_allowed = True
                refusal_msg = ""
                if enable_guardrails:
                    with st.spinner("Checking document guardrails..."):
                        is_allowed, refusal_msg = check_construction_guardrail(text[:1000], model=model)

                if not is_allowed:
                    st.warning(refusal_msg)
                else:
                    with st.spinner("Analyzing..."):
                        prompt = (
                            "Analyze this construction-related document. Provide:\n"
                            "1. A 3-sentence summary\n"
                            "2. Key requirements or specs mentioned\n"
                            "3. Any risks, ambiguities, or missing information\n\n"
                            f"Document:\n{text[:6000]}"
                        )
                        result = generate(prompt, model=model)
                    st.markdown(result)

