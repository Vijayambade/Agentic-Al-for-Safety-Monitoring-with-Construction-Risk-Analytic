"""
frontend/pages/document_analyzer.py
-----------------------------------
Standalone page for the Construction Document Analyzer Chatbot (Feature 4).
"""
import streamlit as st
from frontend.utils.api_client import APIClient


def show_document_analyzer_page():
    st.markdown(
        '# <span class="gradient-text">📂 Construction Document Analyzer Chatbot</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">Upload blueprints, drawings, cost sheets, BOQs, or contracts to summarize, locate risks, identify missing clauses, and answer contextual questions.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar list of analyzed documents
    st.sidebar.markdown("### 📂 Audited Documents")
    
    docs_list = []
    try:
        docs_list = APIClient.list_analyzed_documents()
    except Exception as e:
        st.sidebar.error(f"Error loading document list: {str(e)}")

    selected_doc_id = None
    if docs_list:
        doc_options = {f"{d['filename']} ({d['doc_type']})": d["id"] for d in docs_list}
        selected_option = st.sidebar.selectbox(
            "Load Historical Analysis",
            options=list(doc_options.keys())
        )
        selected_doc_id = doc_options[selected_option]
    else:
        st.sidebar.info("No documents uploaded yet.")

    # 2. Upload Document Form
    st.markdown("### 📥 Upload New Document")
    with st.form("doc_upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader(
            "Select construction contract, BOQ, or drawing specs (PDF, DOCX, XLSX)",
            type=["pdf", "docx", "xlsx", "xls", "doc"]
        )
        submit_upload = st.form_submit_button("Analyze Document", type="primary")

    if submit_upload:
        if not uploaded_file:
            st.error("Please select a file to upload.")
        else:
            with st.spinner("Extracting text, running audit checks, and compiling FAISS search index..."):
                try:
                    file_bytes = uploaded_file.read()
                    res = APIClient.upload_analyzed_document(file_bytes, uploaded_file.name)
                    st.success(f"Audit completed for '{uploaded_file.name}'!")
                    # Force reload so it selects the new document
                    st.session_state["active_doc_id"] = res["id"]
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # Retrieve current active document ID
    active_doc_id = st.session_state.get("active_doc_id", selected_doc_id)
    if active_doc_id is None and selected_doc_id is not None:
        active_doc_id = selected_doc_id

    if active_doc_id is not None:
        # Load details for active document
        doc_details = None
        try:
            doc_details = APIClient.get_analyzed_document_details(active_doc_id)
        except Exception as e:
            st.error(f"Could not load document details: {str(e)}")

        if doc_details:
            st.markdown(
                f"## 📄 Currently Viewing: **{doc_details['filename']}** ({doc_details['doc_type']})"
            )

            # Renders Tabs: Summary, Missing Clauses, Risks, Recommendations
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["📋 Summary Report", "🔍 Missing Clauses Audit", "⚠️ Highlighted Risks", "💡 Recommendations", "💬 Q&A Chatbot"]
            )

            with tab1:
                st.subheader("Document Summary")
                st.info(doc_details["summary"])

            with tab2:
                st.subheader("Audited Missing Clauses Checklist")
                # Split clauses into bullets if formatted as new lines
                clauses = doc_details["missing_clauses"].split("\n")
                for c in clauses:
                    if c.strip():
                        st.markdown(f"- {c.strip()}")

            with tab3:
                st.subheader("Critical Project Risks & Concerns")
                risks = doc_details["risks"].split("\n")
                for r in risks:
                    if r.strip():
                        # Display warning bubbles
                        st.warning(r.strip())

            with tab4:
                st.subheader("Actionable Suggestions")
                recs = doc_details["recommendations"].split("\n")
                for rec in recs:
                    if rec.strip():
                        st.success(rec.strip())

            with tab5:
                st.subheader("💬 Document Conversational QA (RAG)")
                st.write("Ask contextual questions directly from the clauses of this uploaded document:")

                # Chat history local state for active document
                history_key = f"doc_chat_history_{active_doc_id}"
                if history_key not in st.session_state:
                    st.session_state[history_key] = [
                        {"role": "assistant", "content": f"Hi! I've loaded and indexed '{doc_details['filename']}'. Ask me any question about its contents."}
                    ]

                # User query form
                with st.form("doc_qa_form", clear_on_submit=True):
                    question = st.text_input("Ask a question about this document:", placeholder="e.g., What are the payment milestones?")
                    submit_q = st.form_submit_button("Ask Chatbot", type="primary")

                if submit_q and question.strip():
                    # Save user message
                    st.session_state[history_key].append({"role": "user", "content": question.strip()})
                    
                    with st.spinner("Searching FAISS index and generating answer..."):
                        try:
                            reply = APIClient.query_analyzed_document(active_doc_id, question.strip())
                            st.session_state[history_key].append({
                                "role": "assistant",
                                "content": reply["answer"],
                                "context": reply.get("context_retrieved", [])
                            })
                        except Exception as e:
                            st.session_state[history_key].append({"role": "assistant", "content": f"Error: {str(e)}"})
                    st.rerun()

                # Display document chat history
                for chat in reversed(st.session_state[history_key]):
                    avatar = "👷 You" if chat["role"] == "user" else "🤖 Document Bot"
                    color = "#FF8C00" if chat["role"] == "assistant" else "grey"
                    
                    st.markdown(
                        f"""
                        <div style='border-left: 3px solid {color}; padding-left: 10px; margin-bottom: 12px;'>
                            <b>{avatar}</b><br/>
                            {chat['content']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Optional context citation expander
                    if chat["role"] == "assistant" and chat.get("context"):
                        with st.expander("Show Retrieved Text Passages (RAG Citations)"):
                            for idx, passage in enumerate(chat["context"]):
                                st.markdown(f"**[Citation #{idx+1}]** ... *{passage}* ...")
