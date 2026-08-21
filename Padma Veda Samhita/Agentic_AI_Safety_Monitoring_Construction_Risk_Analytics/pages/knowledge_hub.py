"""
=========================================================
Knowledge Hub
=========================================================
"""

import streamlit as st


# --------------------------------------------------------
# PAGE
# --------------------------------------------------------

def render_knowledge_hub():

    st.title("Knowledge Hub")

    st.caption(
        "Construction standards, safety guidelines and best practices."
    )

    st.divider()

    # --------------------------------------------------------
    # Topic Selection
    # --------------------------------------------------------

    topic = st.selectbox(

        "Select Topic",

        [

            "Construction Materials",
            "Safety Guidelines",
            "Construction Standards",
            "Project Management Tips",

        ],

    )

    st.markdown("---")

    # --------------------------------------------------------
    # Construction Materials
    # --------------------------------------------------------

    if topic == "Construction Materials":

        st.subheader("Construction Materials")

        st.info("""
**Concrete**
- Common Grades: M20, M25, M30
- Used for foundations and structural members

**Steel**
- Fe500 reinforcement bars
- High tensile strength

**Bricks**
- Standard Size: 190 × 90 × 90 mm
- Used for wall construction

**Cement**
- OPC and PPC are the most commonly used types.
""")

    # --------------------------------------------------------
    # Safety
    # --------------------------------------------------------

    elif topic == "Safety Guidelines":

        st.subheader("Site Safety")

        st.success("""
✔ Wear PPE at all times

✔ Inspect scaffolding before use

✔ Follow electrical safety procedures

✔ Keep emergency exits accessible

✔ Conduct regular safety meetings
""")

    # --------------------------------------------------------
    # Standards
    # --------------------------------------------------------

    elif topic == "Construction Standards":

        st.subheader("Common Standards")

        st.table({

            "Standard":[
                "IS 456",
                "IS 875",
                "IS 10262",
                "IS 800"
            ],

            "Purpose":[
                "Plain & Reinforced Concrete",
                "Structural Loads",
                "Concrete Mix Design",
                "Steel Structures"
            ]

        })

    # --------------------------------------------------------
    # Project Tips
    # --------------------------------------------------------

    elif topic == "Project Management Tips":

        st.subheader("Best Practices")

        st.warning("""
• Plan before execution.

• Track project progress weekly.

• Monitor project costs.

• Maintain proper documentation.

• Perform regular quality inspections.

• Conduct periodic safety audits.
""")

    st.markdown("---")

    st.caption(
        "Construction Intelligence Hub • Knowledge Base"
    )