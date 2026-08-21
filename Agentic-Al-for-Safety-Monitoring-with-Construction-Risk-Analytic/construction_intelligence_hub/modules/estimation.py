import streamlit as st
from utils.helpers import format_currency
from utils.ollama_client import generate, check_ollama_running, list_models

# Base construction rate per sq.ft (INR), by quality tier
BASE_RATE = {"Economy": 1400, "Standard": 1900, "Premium": 2600, "Luxury": 3800}

# City-tier cost multiplier
CITY_MULTIPLIER = {"Tier 1 Metro": 1.25, "Tier 2 City": 1.05, "Tier 3 / Town": 0.9}

# Rough cost split used to build the breakdown chart / narrative
COST_SPLIT = {
    "Materials": 0.45,
    "Labor": 0.25,
    "Equipment": 0.08,
    "Design & Permits": 0.07,
    "Contingency": 0.10,
    "Overheads": 0.05,
}


def calculate_estimate(area_sqft, quality, city_tier, floors, structure_type):
    base = BASE_RATE[quality] * CITY_MULTIPLIER[city_tier]

    # simple structural adjustments
    if structure_type == "RCC Frame":
        base *= 1.0
    elif structure_type == "Steel Structure":
        base *= 1.18
    elif structure_type == "Load Bearing":
        base *= 0.9

    # multi-floor efficiency (shared foundation/roof cost)
    floor_factor = 1 + (floors - 1) * 0.92
    total_cost = base * area_sqft * floor_factor

    breakdown = {k: total_cost * v for k, v in COST_SPLIT.items()}
    return total_cost, breakdown, base


def build_estimate_summary_prompt(area_sqft, floors, structure_type, quality, city_tier, total_cost, breakdown, rate_used):
    breakdown_text = ", ".join(
        f"{name}: {format_currency(amount)}" for name, amount in breakdown.items()
    )
    return (
        "You are a construction cost consultant. Write a concise 4-5 sentence client-facing "
        "summary for a building estimate. Mention the primary cost drivers, the overall "
        "budget impression, and one practical cost-saving idea. Keep the tone professional "
        "and easy to understand. "
        f"Project context: {floors}-floor {structure_type} building, {area_sqft} sq.ft per floor, "
        f"{quality} finish quality, in a {city_tier} location. Estimated total cost is "
        f"{format_currency(total_cost)} with an effective rate of {format_currency(rate_used)}/sq.ft. "
        f"Breakdown: {breakdown_text}. Suggest one cost-saving approach that is realistic and specific."
    )


def generate_estimate_summary(area_sqft, floors, structure_type, quality, city_tier, total_cost, breakdown, rate_used, model=None):
    prompt = build_estimate_summary_prompt(
        area_sqft,
        floors,
        structure_type,
        quality,
        city_tier,
        total_cost,
        breakdown,
        rate_used,
    )
    system_prompt = (
        "You are a practical construction cost consultant. Explain estimates clearly, "
        "focus on the main cost drivers, and propose one realistic cost-saving action."
    )
    return generate(prompt, model=model or "llama3.1", system=system_prompt)


def render():
    st.header("🏗️ Cost Estimation")
    st.caption("Rule-based construction cost estimator with optional AI-written summary.")

    col1, col2 = st.columns(2)
    with col1:
        area_sqft = st.number_input("Built-up Area (sq.ft)", min_value=100, value=1800, step=50)
        floors = st.number_input("Number of Floors", min_value=1, max_value=40, value=2)
        structure_type = st.selectbox("Structure Type", ["RCC Frame", "Steel Structure", "Load Bearing"])
    with col2:
        quality = st.selectbox("Finish Quality", list(BASE_RATE.keys()), index=1)
        city_tier = st.selectbox("Location Tier", list(CITY_MULTIPLIER.keys()))
        use_ai = st.checkbox("Generate AI narrative summary", value=False)

    if st.button("Calculate Estimate", type="primary"):
        total_cost, breakdown, rate_used = calculate_estimate(
            area_sqft, quality, city_tier, floors, structure_type
        )

        st.subheader("Estimated Cost")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Project Cost", format_currency(total_cost))
        m2.metric("Effective Rate", f"{format_currency(rate_used)}/sq.ft")
        m3.metric("Total Built-up Area", f"{area_sqft * floors:,} sq.ft")

        st.subheader("Cost Breakdown")
        bc1, bc2 = st.columns([1, 1])
        with bc1:
            for item, amount in breakdown.items():
                st.write(f"**{item}**")
                st.progress(min(amount / total_cost, 1.0))
                st.caption(format_currency(amount))
        with bc2:
            import plotly.express as px
            fig = px.pie(
                names=list(breakdown.keys()),
                values=list(breakdown.values()),
                hole=0.45,
            )
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)
            st.plotly_chart(fig, use_container_width=True)

        if use_ai:
            st.subheader("🤖 AI Summary")
            if not check_ollama_running():
                st.warning("The local AI server isn't reachable. Start it with `ollama serve` to enable this.")
            else:
                available_models = list_models()
                selected_model = st.selectbox(
                    "Model",
                    available_models if available_models else ["llama3.1"],
                    key="estimation_model",
                )
                with st.spinner("Asking the local model..."):
                    summary = generate_estimate_summary(
                        area_sqft=area_sqft,
                        floors=floors,
                        structure_type=structure_type,
                        quality=quality,
                        city_tier=city_tier,
                        total_cost=total_cost,
                        breakdown=breakdown,
                        rate_used=rate_used,
                        model=selected_model,
                    )
                st.info(summary)
