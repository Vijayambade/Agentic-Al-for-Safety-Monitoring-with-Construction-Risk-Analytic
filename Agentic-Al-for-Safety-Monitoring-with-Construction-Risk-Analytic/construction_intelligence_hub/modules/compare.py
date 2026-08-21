import streamlit as st
import pandas as pd
import plotly.express as px
from modules.estimation import calculate_estimate, BASE_RATE, CITY_MULTIPLIER
from utils.ollama_client import generate, check_ollama_running
from utils.helpers import format_currency

STRUCTURE_TYPES = ["RCC Frame", "Steel Structure", "Load Bearing"]


def _default_option(idx: int) -> dict:
    letter = chr(64 + idx)  # 1 -> A, 2 -> B, ...
    return {"Name": f"Option {letter}", "Area": 1800, "Floors": 2,
            "Structure": "RCC Frame", "Quality": "Standard", "City": "Tier 2 City"}


def render():
    st.header("🆚 Compare Construction Options")
    st.caption("Configure 2-4 options side by side to see which fits your budget and goals best.")

    if "compare_options" not in st.session_state:
        st.session_state.compare_options = [_default_option(1), _default_option(2)]

    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Add Option", disabled=len(st.session_state.compare_options) >= 4):
            st.session_state.compare_options.append(
                _default_option(len(st.session_state.compare_options) + 1)
            )
            st.rerun()
    with c2:
        if st.button("➖ Remove Last Option", disabled=len(st.session_state.compare_options) <= 1):
            st.session_state.compare_options.pop()
            st.rerun()

    for i, opt in enumerate(st.session_state.compare_options):
        with st.expander(f"⚙️ {opt['Name']}", expanded=True):
            c1, c2, c3 = st.columns(3)
            opt["Name"] = c1.text_input("Option Name", value=opt["Name"], key=f"name_{i}")
            opt["Area"] = c2.number_input("Area per floor (sq.ft)", min_value=100,
                                           value=opt["Area"], step=50, key=f"area_{i}")
            opt["Floors"] = c3.number_input("Floors", min_value=1, max_value=40,
                                             value=opt["Floors"], key=f"floors_{i}")
            c4, c5, c6 = st.columns(3)
            opt["Structure"] = c4.selectbox(
                "Structure Type", STRUCTURE_TYPES,
                index=STRUCTURE_TYPES.index(opt["Structure"]), key=f"struct_{i}",
            )
            opt["Quality"] = c5.selectbox(
                "Finish Quality", list(BASE_RATE.keys()),
                index=list(BASE_RATE.keys()).index(opt["Quality"]), key=f"qual_{i}",
            )
            opt["City"] = c6.selectbox(
                "Location Tier", list(CITY_MULTIPLIER.keys()),
                index=list(CITY_MULTIPLIER.keys()).index(opt["City"]), key=f"city_{i}",
            )

    if st.button("Compare Options", type="primary"):
        results = []
        for opt in st.session_state.compare_options:
            total_cost, breakdown, rate = calculate_estimate(
                opt["Area"], opt["Quality"], opt["City"], opt["Floors"], opt["Structure"]
            )
            row = {
                "Option": opt["Name"], "Structure": opt["Structure"], "Quality": opt["Quality"],
                "City Tier": opt["City"], "Area/floor": opt["Area"], "Floors": opt["Floors"],
                "Total Cost": total_cost, "Rate/sq.ft": rate,
            }
            row.update(breakdown)
            results.append(row)
        df = pd.DataFrame(results)
        st.session_state.compare_results = df

    if "compare_results" in st.session_state:
        df = st.session_state.compare_results

        st.subheader("Comparison Table")
        display_cols = ["Option", "Structure", "Quality", "City Tier", "Area/floor", "Floors",
                         "Total Cost", "Rate/sq.ft"]
        display_df = df[display_cols].copy()
        display_df["Total Cost"] = display_df["Total Cost"].apply(format_currency)
        display_df["Rate/sq.ft"] = display_df["Rate/sq.ft"].apply(format_currency)
        st.dataframe(display_df, use_container_width=True)

        st.subheader("Total Cost Comparison")
        fig = px.bar(df, x="Option", y="Total Cost", color="Option", text_auto=".2s")
        fig.update_layout(height=380, margin=dict(t=20, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        cheapest = df.loc[df["Total Cost"].idxmin()]
        st.success(
            f"💰 Most cost-effective: **{cheapest['Option']}** "
            f"at {format_currency(cheapest['Total Cost'])}"
        )

        if st.checkbox("Get AI recommendation"):
            if not check_ollama_running():
                st.warning("The local AI server isn't reachable. Start it with `ollama serve` to enable this.")
            else:
                with st.spinner("Comparing options..."):
                    opts_text = "\n".join(
                        f"- {r['Option']}: {r['Structure']}, {r['Quality']} finish, "
                        f"{r['City Tier']}, {r['Floors']} floors, {r['Area/floor']} sq.ft/floor, "
                        f"cost ~{format_currency(r['Total Cost'])}"
                        for r in df.to_dict("records")
                    )
                    prompt = (
                        "A client is comparing these construction options:\n"
                        f"{opts_text}\n\n"
                        "In 4-5 sentences, recommend which option makes the most sense and why, "
                        "considering cost, durability, and construction speed trade-offs."
                    )
                    rec = generate(prompt)
                st.info(rec)
