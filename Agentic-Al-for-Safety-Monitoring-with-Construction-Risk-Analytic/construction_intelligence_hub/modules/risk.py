import streamlit as st
import plotly.graph_objects as go
from utils.ollama_client import generate, check_ollama_running

RISK_FACTORS = {
    "Site Accessibility": "Difficulty of getting materials/equipment to site",
    "Weather Exposure": "Likelihood of monsoon/extreme weather delays",
    "Labor Availability": "Skilled labor shortage risk in the area",
    "Regulatory Complexity": "Permit/approval complexity for this project type",
    "Design Maturity": "How finalized the drawings/specs are before starting",
    "Budget Contingency": "How much financial buffer exists (inverse risk)",
}


def render():
    st.header("⚠️ Risk Analysis")
    st.caption("Score each factor 1 (low risk) – 5 (high risk) to get a project risk profile.")

    scores = {}
    cols = st.columns(2)
    for i, (factor, desc) in enumerate(RISK_FACTORS.items()):
        with cols[i % 2]:
            scores[factor] = st.slider(factor, 1, 5, 3, help=desc)

    overall = sum(scores.values()) / (len(scores) * 5) * 100

    st.subheader("Risk Radar")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(scores.values()) + [list(scores.values())[0]],
        theta=list(scores.keys()) + [list(scores.keys())[0]],
        fill="toself",
        name="Risk Profile",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False, height=420, margin=dict(t=30, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    level = "🟢 Low" if overall < 40 else "🟡 Moderate" if overall < 65 else "🔴 High"
    st.metric("Overall Risk Score", f"{overall:.0f} / 100", level)

    if st.button("Generate AI Risk Mitigation Notes"):
        if not check_ollama_running():
            st.warning("The local AI server isn't reachable. Start it with `ollama serve` to enable this.")
        else:
            with st.spinner("Analyzing risk profile..."):
                factor_text = "\n".join(f"- {k}: {v}/5" for k, v in scores.items())
                prompt = (
                    "You are a construction project risk consultant. Given these risk factor "
                    f"ratings (1=low, 5=high):\n{factor_text}\n\n"
                    "List the top 3 risks and one concrete mitigation action for each, "
                    "as short bullet points."
                )
                notes = generate(prompt)
            st.markdown(notes)
