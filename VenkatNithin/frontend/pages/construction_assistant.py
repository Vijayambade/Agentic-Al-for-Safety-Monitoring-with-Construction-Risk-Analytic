"""
frontend/pages/construction_assistant.py
----------------------------------------
Standalone page for the Construction AI Assistant (Feature 3).
"""
import uuid
import streamlit as st
from frontend.utils.api_client import APIClient


def show_construction_assistant_page():
    st.markdown(
        '# <span class="gradient-text">🏗️ AI Construction Expert Assistant</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">General chatbot for civil engineering questions, document analysis, safety checks, and multilingual translations.</p>',
        unsafe_allow_html=True,
    )

    # Make sure we have a session ID
    if "ai_session_id" not in st.session_state:
        st.session_state["ai_session_id"] = str(uuid.uuid4())

    session_id = st.session_state["ai_session_id"]

    # Sidebar controls specifically for the assistant
    st.sidebar.markdown("### Assistant Options")
    
    # Multilingual Selectbox
    language = st.sidebar.selectbox(
        "Chat Language / भाषा",
        ["English", "Spanish (Español)", "Hindi (हिंदी)", "French (Français)", "German (Deutsch)"],
        index=0
    )
    
    # Map to language code for gTTS and Gemini
    lang_map = {
        "English": "en",
        "Spanish (Español)": "es",
        "Hindi (हिंदी)": "hi",
        "French (Français)": "fr",
        "German (Deutsch)": "de"
    }
    lang_code = lang_map.get(language, "en")

    # Clear history option
    if st.sidebar.button("🧹 Clear Chat History", use_container_width=True):
        try:
            APIClient.clear_general_chat_history(session_id)
            st.sidebar.success("Chat history cleared.")
            st.rerun()
        except Exception as e:
            st.sidebar.error(str(e))

    # Fetch dialogue history on render
    history = []
    try:
        history = APIClient.get_general_chat_history(session_id)
    except Exception as e:
        st.error(f"Could not load conversation history: {str(e)}")

    # Layout: left column for uploading files & audio; right column for chat history
    col_chat, col_upload = st.columns([2, 1])

    with col_upload:
        st.markdown("### 📎 Attachments & Media")
        st.info("Ask visual questions, analyze contract specifications, or talk directly to the agent.")

        # Document uploader (RAG)
        uploaded_doc = st.file_uploader(
            "Upload BOQ, Contract, or Drawing specifications (PDF, DOCX, Excel)",
            type=["pdf", "docx", "doc", "xlsx", "xls"]
        )

        # Image uploader (Visual QA)
        uploaded_img = st.file_uploader(
            "Upload site photos or drawings (PNG, JPG, JPEG)",
            type=["png", "jpg", "jpeg"]
        )

        # Audio uploader (Speech input)
        uploaded_audio = st.file_uploader(
            "Upload voice command (WAV, FLAC, AIFF)",
            type=["wav", "flac", "aiff"]
        )

    with col_chat:
        st.markdown("### 💬 Conversational dialogue")

        # Render conversation history bubbles
        chat_container = st.container(height=420)
        with chat_container:
            if not history:
                st.write(
                    "<div style='text-align: center; color: grey; margin-top: 150px;'>"
                    "No conversation logs yet. Type a question or upload a file to get started!"
                    "</div>",
                    unsafe_allow_html=True
                )
            else:
                for msg in history:
                    is_user = msg["role"] == "user"
                    align = "right" if is_user else "left"
                    bg_color = "rgba(255, 140, 0, 0.08)" if is_user else "rgba(30, 39, 51, 0.65)"
                    border = "1px solid rgba(255, 140, 0, 0.2)" if is_user else "1px solid rgba(255, 140, 0, 0.1)"
                    avatar = "👷 You" if is_user else "🤖 AI Expert"
                    
                    st.markdown(
                        f"""
                        <div style='background: {bg_color}; border: {border}; border-radius: 12px; padding: 12px; margin-bottom: 12px; text-align: left;'>
                            <b>{avatar}</b><br/>
                            <p style='margin: 5px 0 0 0; line-height: 1.5;'>{msg['message']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # If assistant response has an audio file link, render the audio player
                    if not is_user and msg.get("audio_url"):
                        # Note: relative path is returned as /cache/..., concatenate with backend url endpoint
                        from frontend.utils.api_client import BACKEND_URL
                        full_audio_url = f"{BACKEND_URL}{msg['audio_url']}"
                        st.audio(full_audio_url, format="audio/mp3")

        # Chat inputs
        with st.form("chat_input_form", clear_on_submit=True):
            user_text = st.text_input("Message Construction Assistant:", placeholder="Ask about mix design, OSHA guidelines, etc...")
            submit_chat = st.form_submit_button("Send Query", type="primary")

        # Process message submission
        if submit_chat:
            prompt_str = user_text.strip()
            
            # Read files if uploaded
            doc_bytes = None
            doc_name = "document.pdf"
            if uploaded_doc:
                doc_bytes = uploaded_doc.read()
                doc_name = uploaded_doc.name
                
            img_bytes = None
            img_name = "image.jpg"
            if uploaded_img:
                img_bytes = uploaded_img.read()
                img_name = uploaded_img.name
                
            audio_bytes = None
            if uploaded_audio:
                audio_bytes = uploaded_audio.read()

            # Ensure we have at least text or a file
            if not prompt_str and not doc_bytes and not img_bytes and not audio_bytes:
                st.error("Please enter a question, upload a voice recording, or attach a document.")
            else:
                with st.spinner("Analyzing parameters and generating reply..."):
                    try:
                        APIClient.send_general_chat(
                            session_id=session_id,
                            prompt=prompt_str if prompt_str else None,
                            language=lang_code,
                            audio=audio_bytes,
                            image=img_bytes,
                            document=doc_bytes,
                            doc_name=doc_name,
                            img_name=img_name
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        # Download chats log
        if history:
            chat_text = ""
            for msg in history:
                speaker = "User" if msg["role"] == "user" else "Assistant"
                chat_text += f"{speaker} ({msg['timestamp']}): {msg['message']}\n\n"

            st.download_button(
                label="📥 Download Chat Logs (.txt)",
                data=chat_text,
                file_name=f"construction_chat_{session_id}.txt",
                mime="text/plain",
                use_container_width=True
            )
