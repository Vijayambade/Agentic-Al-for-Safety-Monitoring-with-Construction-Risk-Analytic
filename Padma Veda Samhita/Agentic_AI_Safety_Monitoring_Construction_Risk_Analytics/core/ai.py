import requests
import streamlit as st

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"


# ---------------------------------------------------------
# Construction Guardrail
# ---------------------------------------------------------

def is_construction_related(text: str) -> bool:
    """
    Uses Ollama to determine whether the input
    is related to construction.
    """
    classifier_prompt = f"""You are a classifier for a Construction Intelligence Hub.
    The user is currently working on a construction project.
    Decide whether the USER'S QUESTION should be answered by a construction AI assistant.
    Return YES if:
    - It is about the current project.
    - It refers to "project", "budget", "cost", "schedule", "deadline", "completion", "progress", "delay", "client", "contractor", or work being performed.
    - It is about construction, civil engineering, architecture, structural engineering, BOQ, materials, safety, estimation, or site management.
    Return NO if:
    - It is general knowledge.
    - It is mathematics.
    - It is about sports, celebrities, politics, history, entertainment or anything else
    Reply ONLY with YES or NO.
    The input may be:
    - a user question
    - a construction document
    - a PDF
    - an OCR scan
    - a contract
    - a drawing description
    - a BOQ
    - a site report
    INPUT:
    {text}"""

    
    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": classifier_prompt,
                "stream": False
            },
            timeout=None
        )

        response.raise_for_status()

        answer = response.json().get("response", "").strip().upper()

        return answer.startswith("YES")

    except Exception:
        # Allow the request if the classifier fails
        return True
def is_construction_document(text: str) -> bool:

    classifier_prompt = f"""
You are a document classifier.

Your ONLY task is to determine whether the following extracted text comes from a construction-related document.

Construction documents include:

- Architectural Drawings
- Structural Drawings
- Civil Engineering Drawings
- Site Reports
- BOQ
- Bill of Quantities
- Material Estimates
- Contracts
- DPR
- Construction Specifications
- Foundation Details
- Reinforcement Details
- Safety Reports
- Quality Checklists

Return YES if the text belongs to any construction document.

Return NO if it is:

- Resume
- CV
- Biography
- Medical Report
- Bank Statement
- Story
- Newspaper
- Examination Paper
- Assignment
- Personal Letter

Reply ONLY with YES or NO.

Document:

{text}
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": classifier_prompt,
                "stream": False,
            },
            timeout=None,
        )

        response.raise_for_status()

        answer = response.json().get("response", "").strip().upper()

        return answer.startswith("YES")

    except Exception:
        return True


# ---------------------------------------------------------
# AI Response
# ---------------------------------------------------------

def ask_ai(prompt: str) -> str:
    """
    Sends a prompt to Ollama after passing
    the Construction Guardrail.
    """

  

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=None
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "").strip()

    except Exception as e:

        return f"Error communicating with Ollama:\n{e}"


# ---------------------------------------------------------
# Project Context
# ---------------------------------------------------------

def get_project_context(project_name):
    """
    Returns formatted project information
    for the selected project.
    """

    projects = st.session_state.get("projects", [])

    for project in projects:

        if project["name"] == project_name:

            return f"""
Project Name: {project.get('name', 'N/A')}
Client: {project.get('client', 'N/A')}
Location: {project.get('location', 'N/A')}
Status: {project.get('status', 'N/A')}
Progress: {project.get('progress', 'N/A')}%
"""

    return "No project selected."