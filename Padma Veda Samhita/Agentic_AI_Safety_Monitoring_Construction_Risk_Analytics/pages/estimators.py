"""
=========================================================
Estimators
=========================================================
"""
from core.ai import ask_ai, get_project_context

import streamlit as st


# --------------------------------------------------------
# PAGE
# --------------------------------------------------------

def render_estimators():

    st.title("Construction Estimators")

    st.caption(
        "Calculate quantities and estimated costs for construction materials."
    )
    st.markdown("### Select Project")
    projects = st.session_state.get("projects", [])
    if len(projects) == 0:
        st.warning("No projects available.")
        return
    project_names = [p["name"] for p in projects]
    selected_project = st.selectbox(
        "Project",
        project_names,
    )

    st.subheader("Choose an Estimator")

    estimator = st.selectbox(
        "Estimator",
        [
            "Concrete Estimator",
            "Brick Estimator",
            "Steel Estimator",
            "Paint Estimator",
            "Material Cost Estimator",
        ],
    )

    st.markdown("---")

    # --------------------------------------------------------
    # CONCRETE ESTIMATOR
    # --------------------------------------------------------

    if estimator == "Concrete Estimator":

        st.subheader("Concrete Estimator")

        col1, col2 = st.columns(2)

        with col1:

            length = st.number_input(
                "Length (m)",
                min_value=0.0,
                value=10.0,
            )

            width = st.number_input(
                "Width (m)",
                min_value=0.0,
                value=8.0,
            )

        with col2:

            depth = st.number_input(
                "Depth (m)",
                min_value=0.0,
                value=0.15,
            )

            wastage = st.slider(
                "Wastage (%)",
                0,
                20,
                5,
            )

        if st.button(
            "Calculate Concrete",
            use_container_width=True,
            type="primary",
        ):

            volume = length * width * depth
            volume += volume * wastage / 100

            cement = volume * 8
            sand = volume * 0.44
            aggregate = volume * 0.88

            st.success("Estimation Completed")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "Concrete",
                    f"{volume:.2f} m³",
                )

            with c2:
                st.metric(
                    "Cement",
                    f"{cement:.0f} Bags",
                )

            with c3:
                st.metric(
                    "Sand",
                    f"{sand:.2f} m³",
                )

            with c4:
                st.metric(
                    "Aggregate",
                    f"{aggregate:.2f} m³",
                )

            st.markdown("---")

            st.info(
                """
Recommended Cement Grade : M30

Recommended Curing Period : 28 Days

Estimated Quality : Excellent
"""
            )

            with st.spinner("Generating AI Material Analysis..."):

                prompt = f"""
You are an experienced construction engineer.

Project Information:
{get_project_context(selected_project)}

Concrete Quantity : {volume:.2f} m³
Cement : {cement:.0f} Bags
Sand : {sand:.2f} m³
Aggregate : {aggregate:.2f} m³

Analyze these values.

Provide:

• Material validation

• Material quality recommendation

• Storage recommendations

• Curing advice

• Possible risks

• Cost optimization

Keep the response below 180 words.
"""

                response = ask_ai(prompt)

            st.markdown("### 🤖 AI Material Analysis")

            with st.container(border=True):
                st.write(response)

    # --------------------------------------------------------
    # BRICK ESTIMATOR
    # --------------------------------------------------------

    elif estimator == "Brick Estimator":

        st.subheader("Brick Estimator")

        col1, col2 = st.columns(2)

        with col1:

            wall_length = st.number_input(
                "Wall Length (m)",
                min_value=0.0,
                value=10.0,
            )

            wall_height = st.number_input(
                "Wall Height (m)",
                min_value=0.0,
                value=3.0,
            )

        with col2:

            wall_thickness = st.selectbox(
                "Wall Thickness",
                ["0.10 m", "0.20 m", "0.30 m"],
            )

            wastage = st.slider(
                "Brick Wastage (%)",
                0,
                20,
                5,
            )

        if st.button(
            "Calculate Bricks",
            use_container_width=True,
            type="primary",
        ):

            area = wall_length * wall_height

            bricks = int(area * 60)

            bricks += int(bricks * wastage / 100)

            st.success("Calculation Complete")

            st.metric(
                "Estimated Bricks",
                f"{bricks:,}",
            )

            st.info(
                """
Recommended Brick Size : 190 × 90 × 90 mm

Recommended Mortar : 1 : 6

Estimated Wastage : Included
"""
            )

            with st.spinner("Generating AI Material Analysis..."):

                prompt = f"""
You are an experienced construction engineer.

Project Information:
{get_project_context(selected_project)}

Estimated Bricks : {bricks}

Analyze the estimate.

Provide:

• Material validation

• Suitable brick type

• Recommended mortar ratio

• Storage recommendations

• Wastage reduction methods

• Construction recommendations

Keep the response below 180 words.
"""

                response = ask_ai(prompt)

            st.markdown("### 🤖 AI Material Analysis")

            with st.container(border=True):
                st.write(response)

    # --------------------------------------------------------
    # STEEL ESTIMATOR
    # --------------------------------------------------------

    elif estimator == "Steel Estimator":

        st.subheader("Steel Estimator")

        bars = st.number_input(
            "Number of Bars",
            min_value=1,
            max_value=1000,
            value=20,
        )

        length = st.number_input(
            "Length per Bar (m)",
            min_value=1.0,
            max_value=30.0,
            value=12.0,
        )

        diameter = st.selectbox(
            "Bar Diameter (mm)",
            [8, 10, 12, 16, 20, 25],
        )

        if st.button(
            "Calculate Steel",
            use_container_width=True,
            type="primary",
        ):

            weight = (diameter ** 2 / 162) * length * bars

            st.success("Calculation Complete")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Steel Required",
                    f"{weight:.2f} kg",
                )

            with col2:
                st.metric(
                    "Bars",
                    bars,
                )

            st.info(
                f"""
Recommended Steel Grade : Fe500

Bar Diameter : {diameter} mm

Estimated Steel Weight : {weight:.2f} kg
"""
            )

            with st.spinner("Generating AI Material Analysis..."):

                prompt = f"""
You are an experienced construction structural engineer.

Project Information:
{get_project_context(selected_project)}

Calculated Steel Details

Steel Required : {weight:.2f} kg

Number of Bars : {bars}

Bar Diameter : {diameter} mm

Analyze ONLY the above information.

Provide:

• Material validation

• Suitable steel grade

• Reinforcement recommendations

• Corrosion protection

• Storage recommendations

• Safety precautions

• Cost optimization suggestions

Keep the response below 180 words.
"""

                response = ask_ai(prompt)

            st.markdown("### 🤖 AI Material Analysis")

            with st.container(border=True):
                st.write(response)

    # --------------------------------------------------------
    # PAINT ESTIMATOR
    # --------------------------------------------------------

    elif estimator == "Paint Estimator":

        st.subheader("Paint Estimator")

        area = st.number_input(
            "Wall Area (m²)",
            min_value=1.0,
            value=100.0,
        )

        coats = st.slider(
            "Number of Coats",
            1,
            4,
            2,
        )

        if st.button(
            "Calculate Paint",
            use_container_width=True,
            type="primary",
        ):

            paint = area * coats / 10

            st.success("Calculation Complete")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Paint Required",
                    f"{paint:.1f} Litres",
                )

            with col2:
                st.metric(
                    "Coverage",
                    "10 m²/L",
                )

            st.info(
                f"""
Recommended Paint : Exterior Acrylic Emulsion

Wall Area : {area:.2f} m²

Number of Coats : {coats}

Estimated Paint : {paint:.2f} Litres
"""
            )

            with st.spinner("Generating AI Material Analysis..."):

                prompt = f"""
You are an experienced construction finishing engineer.

Project Information:
{get_project_context(selected_project)}

Calculated Paint Details

Wall Area : {area:.2f} m²

Number of Coats : {coats}

Estimated Paint Required : {paint:.2f} Litres

Analyze ONLY the above information.

Provide:

• Paint quantity validation

• Recommended paint type

• Primer recommendation

• Drying and curing time

• Weather precautions

• Storage recommendations

• Cost optimization suggestions

Keep the response below 180 words.
"""

                response = ask_ai(prompt)

            st.markdown("### 🤖 AI Material Analysis")

            with st.container(border=True):
                st.write(response)

    # --------------------------------------------------------
    # MATERIAL COST ESTIMATOR
    # --------------------------------------------------------

    elif estimator == "Material Cost Estimator":

        st.subheader("Material Cost Estimator")

        cement = st.number_input(
            "Cement Cost (₹)",
            min_value=0,
            value=50000,
        )

        steel = st.number_input(
            "Steel Cost (₹)",
            min_value=0,
            value=120000,
        )

        bricks = st.number_input(
            "Brick Cost (₹)",
            min_value=0,
            value=35000,
        )

        paint = st.number_input(
            "Paint Cost (₹)",
            min_value=0,
            value=18000,
        )

        if st.button(
            "Calculate Total Cost",
            use_container_width=True,
            type="primary",
        ):

            total = cement + steel + bricks + paint

            st.success("Cost Estimation Completed")

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "Estimated Cost",
                    f"₹ {total:,.0f}",
                )

            with c2:
                st.metric(
                    "Materials",
                    "4",
                )

            st.info(
                f"""
Estimated Project Material Cost

• Cement : ₹{cement:,}

• Steel : ₹{steel:,}

• Bricks : ₹{bricks:,}

• Paint : ₹{paint:,}

------------------------------------

Total Estimated Cost : ₹{total:,}
"""
            )

            with st.spinner("Generating AI Material Analysis..."):

                prompt = f"""
You are an experienced construction cost consultant.

Project Information:
{get_project_context(selected_project)}

Estimated Material Costs

Cement : ₹{cement}

Steel : ₹{steel}

Bricks : ₹{bricks}

Paint : ₹{paint}

Total Estimated Cost : ₹{total}

Analyze ONLY the above information.

Provide:

• Budget validation

• Procurement strategy

• Cost optimization ideas

• Material purchasing recommendations

• Financial risks

• Suggestions to reduce unnecessary expenses

Keep the response below 180 words.
"""

                response = ask_ai(prompt)

            st.markdown("### 🤖 AI Material Analysis")

            with st.container(border=True):
                st.write(response)

    # --------------------------------------------------------
    # ESTIMATION SUMMARY
    # --------------------------------------------------------

 

    st.markdown("---")

    st.subheader("Material Reference")

    reference = {
        "Material": [
            "Concrete",
            "Steel",
            "Bricks",
            "Paint",
        ],
        "Standard": [
            "M20 - M40",
            "Fe500",
            "190×90×90 mm",
            "10 m²/L",
        ],
        "Typical Usage": [
            "Structural Work",
            "Reinforcement",
            "Wall Construction",
            "Wall Finishing",
        ],
    }

    st.table(reference)

    st.markdown("---")

    st.caption(
        "All calculations are approximate estimates intended for planning purposes."
    )