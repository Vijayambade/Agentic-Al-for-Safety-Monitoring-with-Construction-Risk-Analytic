import streamlit as st
import PyPDF2
import io
import re
from utils.ollama_client import check_ollama_running, list_models, generate
from utils.guardrails import check_construction_guardrail

MATERIAL_FACTORS = {
    "RCC Frame": {
        "Cement (bags)": 0.12,
        "Bricks (pieces)": 10,
        "Steel (kg)": 3.0,
        "Sand (m³)": 0.015,
        "Aggregate (m³)": 0.020,
        "Plaster Cement (bags)": 0.09,
        "Paint (liters)": 0.18,
    },
    "Steel Structure": {
        "Cement (bags)": 0.10,
        "Bricks (pieces)": 8,
        "Steel (kg)": 4.5,
        "Sand (m³)": 0.012,
        "Aggregate (m³)": 0.018,
        "Plaster Cement (bags)": 0.07,
        "Paint (liters)": 0.16,
    },
    "Load Bearing": {
        "Cement (bags)": 0.14,
        "Bricks (pieces)": 12,
        "Steel (kg)": 2.5,
        "Sand (m³)": 0.017,
        "Aggregate (m³)": 0.022,
        "Plaster Cement (bags)": 0.10,
        "Paint (liters)": 0.20,
    },
}


def calculate_materials(area_sqft: float, floors: int, structure_type: str) -> dict[str, float]:
    total_area = area_sqft * floors
    factors = MATERIAL_FACTORS.get(structure_type, MATERIAL_FACTORS["RCC Frame"])
    return {
        name: round(total_area * rate, 2)
        for name, rate in factors.items()
    }


def _extract_text(uploaded_file) -> str:
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return uploaded_file.read().decode("utf-8", errors="ignore")


def parse_ai_response(response: str) -> tuple[float | None, int | None, str | None, str]:
    area_sqft = None
    floors = None
    structure_type = None
    analysis_report = response

    lines = response.split("\n")
    report_start_idx = -1
    for i, line in enumerate(lines[:15]):  # Look at the first 15 lines for parameters
        line_upper = line.upper().strip()
        if line_upper.startswith("AREA_SQFT:"):
            val = line.split(":", 1)[1].strip()
            num_match = re.search(r"\d+(\.\d+)?", val)
            if num_match:
                area_sqft = float(num_match.group(0))
        elif line_upper.startswith("FLOORS:"):
            val = line.split(":", 1)[1].strip()
            num_match = re.search(r"\d+", val)
            if num_match:
                floors = int(num_match.group(0))
        elif line_upper.startswith("STRUCTURE_TYPE:"):
            val = line.split(":", 1)[1].strip()
            for st_type in ["RCC Frame", "Steel Structure", "Load Bearing"]:
                if st_type.lower() in val.lower():
                    structure_type = st_type
                    break
        elif line_upper.startswith("ANALYSIS_REPORT:"):
            report_start_idx = i + 1
            break
            
    if report_start_idx != -1:
        analysis_report = "\n".join(lines[report_start_idx:])
    
    return area_sqft, floors, structure_type, analysis_report


def render():
    st.header("🧱 Material Management")
    st.caption("Estimate construction materials from built-up area/structure type or by analyzing a document.")

    tab1, tab2 = st.tabs(["🧮 Area-Based Calculator", "📄 Document Analyzer"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            area_sqft = st.number_input("Built-up Area per Floor (sq.ft)", min_value=100, value=1000, step=50)
            floors = st.number_input("Number of Floors", min_value=1, max_value=40, value=1)
            structure_type = st.selectbox(
                "Structure Type",
                ["RCC Frame", "Steel Structure", "Load Bearing"],
            )
        with col2:
            st.markdown("#### Approximate material rates")
            st.write("These are preliminary estimates and should be validated by a structural engineer.")
            st.write("• Cement: bags per total built-up area")
            st.write("• Bricks: pieces per total built-up area")
            st.write("• Steel: kg per total built-up area")
            st.write("• Sand & Aggregate: cubic meters per total built-up area")

        if st.button("Calculate Material Estimate"):
            estimates = calculate_materials(area_sqft, floors, structure_type)
            total_area = area_sqft * floors

            st.subheader("Estimated Material Requirements")
            st.metric("Total Built-up Area", f"{total_area:,} sq.ft")

            table_data = [{"Material": name, "Quantity": qty} for name, qty in estimates.items()]
            st.table(table_data)

            st.markdown("---")
            st.subheader("Notes")
            st.markdown(
                "- These values are rough preliminary quantities. Final material bills of quantities (BOQ) should be prepared by an engineer or estimator."
            )
            st.markdown(
                "- Use the selected structure type to adjust the material mix: steel structures need more steel, load-bearing buildings need more bricks."
            )

        st.markdown("---")
        st.subheader("🤖 AI Helper")
        if not check_ollama_running():
            st.warning("The local AI server is not running. Start it with 'ollama serve' and pull a model first.")
        else:
            models = list_models() or ["llama3.1"]
            model = st.selectbox("Model", models, key="mat_model")
            prompt = st.text_area(
                "Ask for material guidance",
                "Suggest a plan to reduce material wastage and secure alternatives for delayed steel supply.",
                key="mat_prompt",
            )
            if st.button("Generate insight", key="mat_generate"):
                with st.spinner("Thinking..."):
                    response = generate(prompt, model=model, system="You are a construction materials advisor. Provide concise, practical recommendations.")
                st.markdown(response)

    with tab2:
        st.caption("Upload a spec sheet, RFP, or site drawing report (.txt or .pdf) to estimate materials using AI.")
        uploaded_file = st.file_uploader(
            "Upload project document", type=["txt", "pdf"], key="mat_doc_uploader"
        )
        if uploaded_file is not None:
            text = _extract_text(uploaded_file)
            st.text_area("Extracted text (preview)", text[:2000], height=150, key="mat_doc_preview", disabled=True)

            if not check_ollama_running():
                st.warning("The local AI server is not running. Start it with 'ollama serve' and pull a model first.")
            else:
                models = list_models() or ["llama3.1"]
                col_m, col_g = st.columns(2)
                with col_m:
                    selected_model = st.selectbox("Model", models, key="mat_doc_model")
                with col_g:
                    enable_guardrails = st.checkbox(
                        "Enable Construction Guardrails",
                        value=True,
                        help="Block off-topic queries and document processing using local AI guardrails.",
                        key="mat_doc_guardrails"
                    )

                if st.button("Analyze & Estimate Materials", key="mat_doc_analyze"):
                    is_allowed = True
                    refusal_msg = ""
                    if enable_guardrails:
                        with st.spinner("Checking document guardrails..."):
                            is_allowed, refusal_msg = check_construction_guardrail(text[:1000], model=selected_model)

                    if not is_allowed:
                        st.warning(refusal_msg)
                    else:
                        with st.spinner("Analyzing document and estimating materials..."):
                            prompt = (
                                "Analyze the following construction-related document (e.g. specification sheet, project proposal, or bill of quantities) and estimate the required materials.\n\n"
                                "First, attempt to extract or estimate these specific parameter values if they are mentioned or can be reasonably inferred. "
                                "Format these parameters at the very beginning of your response exactly like this (use 'Unknown' if not mentioned and cannot be reasonably estimated):\n"
                                "AREA_SQFT: <number or 'Unknown'>\n"
                                "FLOORS: <number or 'Unknown'>\n"
                                "STRUCTURE_TYPE: <'RCC Frame', 'Steel Structure', 'Load Bearing', or 'Unknown'>\n\n"
                                "After these three lines, write a detailed material estimation and specification report under the header 'ANALYSIS_REPORT:'.\n"
                                "In the report, provide:\n"
                                "1. An overview of the project type and structure.\n"
                                "2. A detailed estimation of key materials (cement, bricks, steel, aggregate, sand, paint, etc.) with estimated quantities and why.\n"
                                "3. Recommended material specifications (e.g. cement grade, steel type) based on the document.\n"
                                "4. Any risks, wastage concerns, or recommendations for material supply.\n\n"
                                f"Document Content:\n{text[:6000]}"
                            )
                            response = generate(prompt, model=selected_model, system="You are a construction material estimator. Extract parameters and provide a comprehensive materials analysis.")
                        
                        area_sqft, floors, structure_type, analysis_report = parse_ai_response(response)

                        # Display parsed parameters
                        st.subheader("Extracted Project Parameters")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Area per Floor", f"{area_sqft:,.2f} sq.ft" if area_sqft else "Unknown")
                        c2.metric("Floors", f"{floors}" if floors else "Unknown")
                        c3.metric("Structure Type", f"{structure_type}" if structure_type else "Unknown")

                        if area_sqft and floors:
                            st.subheader("Auto-Calculated Material Requirements")
                            struct = structure_type if structure_type in ["RCC Frame", "Steel Structure", "Load Bearing"] else "RCC Frame"
                            estimates = calculate_materials(area_sqft, floors, struct)
                            total_area = area_sqft * floors
                            st.write(f"Based on extracted area of **{total_area:,.2f} sq.ft** and **{struct}** structure type:")
                            table_data = [{"Material": name, "Quantity": qty} for name, qty in estimates.items()]
                            st.table(table_data)
                        else:
                            st.info("💡 Standard material estimation table could not be auto-calculated because Area/Floors were not found in the document. See the detailed AI Analysis Report below.")

                        st.markdown("---")
                        st.subheader("📋 AI Material Specification & Analysis Report")
                        st.markdown(analysis_report)

