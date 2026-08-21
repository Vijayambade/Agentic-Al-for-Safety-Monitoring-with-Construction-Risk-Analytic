"""
=========================================================
AI Assistant
=========================================================
"""

import streamlit as st
import time
from core.ai import ask_ai, get_project_context,is_construction_related


# ---------------------------------------------------------
# Page
# ---------------------------------------------------------

def render_ai_assistant():

    st.title("🤖 AI Construction Assistant")

    st.caption(
        "AI-powered assistant for construction planning, estimation and project management."
    )

    st.divider()

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    left, right = st.columns([3,1])

    with left:

        projects = [
            p["name"]
            for p in st.session_state.get("projects", [])
        ]

        if len(projects) == 0:
            projects = ["No Projects"]

        selected_project = st.selectbox(
            "Select Project",
            projects,
        )

    with right:

        st.success("🟢 AI Online")

    st.divider()

    # ---------------------------------------------------------
    # Quick Prompts
    # ---------------------------------------------------------

    st.subheader("Quick AI Actions")

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "📦 Material Estimation",
            use_container_width=True,
        ):

            with st.spinner("AI is analyzing project..."):
                time.sleep(1)
            project_context = get_project_context(selected_project)

            prompt = f"""You are an experienced construction engineer.
            Project Details:{project_context}
            Generate a professional material estimation report.
            Include:
            - Concrete
            - Steel
            - Cement Grade
            - Estimated Cost
            - Recommendations
            - Risk Level
            Keep the response under 200 words unless the user explicitly asks for a detailed explanation."""
            response = ask_ai(prompt)
            st.session_state.chat_history.append(
                (
                    "Material Estimation",
                    response,
                    )
            )

            st.rerun()

        if st.button(
            "⚠ Safety Analysis",
            use_container_width=True,
        ):

            with st.spinner("Checking safety records..."):
                time.sleep(1)
            project_context = get_project_context(selected_project)

            prompt = f""" You are a construction safety expert.
            Project Details:{project_context}
            Perform a detailed safety analysis.
            Include:
            - Safety compliance
            - Major risks
            - Recommendations
            - Overall Risk Level
            Keep the response under 200 words unless the user explicitly asks for a detailed explanation."""
            response = ask_ai(prompt)
            st.session_state.chat_history.append(
                (
                    "Safety Analysis",
                    response,
                    )
            )
            st.rerun()

    with c2:

        if st.button(
            "📅 Schedule Delay",
            use_container_width=True,
        ):

            with st.spinner("Analyzing project schedule..."):
                time.sleep(1)
            project_context = get_project_context(selected_project)

            
            prompt = f""" You are a project scheduling expert.
            Project Details:{project_context}
            Analyze the construction schedule.
            Include:
            - Delay risks
            - Possible causes
            - Completion prediction
            - Recommendations 
            Keep the response under 200 words unless the user explicitly asks for a detailed explanation."""
            response = ask_ai(prompt)
            st.session_state.chat_history.append(
                (
                    "Schedule Delay",response,
                    )
            )

            st.rerun()

        if st.button(
            "💰 Cost Prediction",
            use_container_width=True,
        ):

            with st.spinner("Calculating project cost..."):
                time.sleep(1)
            project_context = get_project_context(selected_project)

            prompt = f""" You are a construction cost consultant.
            Project Details:{project_context}
            Predict the project cost.
            Include:
            - Estimated Final Cost
            - Budget Usage
            - Remaining Budget
            - Recommendations
            Keep the response under 200 words unless the user explicitly asks for a detailed explanation.
            """
            response = ask_ai(prompt)
            st.session_state.chat_history.append(
                (
                    "Cost Prediction", response,
                    )
            )

            st.rerun()

    st.divider()

    # ---------------------------------------------------------
    # Ask AI
    # ---------------------------------------------------------

    st.subheader("Ask AI")

    question = st.text_area(
        "Ask your construction question",
        placeholder="Example: How much steel is required for Block A?",
        height=120,
    )
    if st.button("🚀 Ask AI",
                 type="primary",
                 use_container_width=True,
                 ):
        if question.strip() != "":
            # -----------------------------
            # Guardrail Check
            # -----------------------------
            if not is_construction_related(question):
                answer = """
                Sorry!
                I am the Construction Intelligence Hub AI Assistant.
                I can answer questions only related to:
                • Construction
                • Civil Engineering
                • Architecture
                • Structural Engineering
                • Building Materials
                • Quantity Estimation
                • Cost Estimation
                • Construction Drawings
                • Site Safety
                • Project Management
                Please ask a construction-related question."""
            else:
                with st.spinner("AI is thinking..."):
                     st.info("AI is thinking... Please wait while I analyze your question.")
                     project_context = get_project_context(selected_project)
                     prompt = f"""You are the AI assistant for a Construction Intelligence Hub.
                     Current Project Details:{project_context}
                     User Question:{question}
                     You are an experienced civil engineer and construction project consultant.
                     Provide:
                     - Accurate technical guidance
                     - Practical recommendations
                     - Safety considerations
                     - Cost implications (if relevant)
                     - Risk assessment (if relevant)
                     Use headings and bullet points where appropriate.
                     If information is insufficient, clearly state any assumptions.
                     Keep the response under 200 words unless the user explicitly asks for a detailed explanation."""
                     answer = ask_ai(prompt)
            st.session_state.chat_history.append((question, answer))
            st.rerun()

  

    # ---------------------------------------------------------
    # Conversation
    # ---------------------------------------------------------
    st.subheader("Conversation")

    if len(st.session_state.chat_history) == 0:

        st.info("Start a conversation with the AI Assistant.")

    else:

        for question, answer in reversed(st.session_state.chat_history):

            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                st.markdown(answer)
                st.caption("Generated by local Ollama (llama3.2)")
        
            st.divider()

    # ---------------------------------------------------------
    # Clear Conversation
    # ---------------------------------------------------------

    if st.button(
        "🗑 Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.chat_history = []

        st.rerun()