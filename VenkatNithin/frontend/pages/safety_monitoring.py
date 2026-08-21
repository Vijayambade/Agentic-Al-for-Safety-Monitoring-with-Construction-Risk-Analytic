"""
frontend/pages/safety_monitoring.py
-----------------------------------
Standalone page for Onsite Safety Monitoring & PPE Detection (Feature 6).
"""
import streamlit as st
from frontend.utils.api_client import APIClient


def show_safety_monitoring_page():
    st.markdown(
        '# <span class="gradient-text">📷 Onsite Live PPE Monitoring</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">Onsite live safety checking camera. Use browser webcam or upload site photos to locate Hard Hats, Safety Vests, Safety Boots, Harnesses, and Goggles.</p>',
        unsafe_allow_html=True,
    )

    # 1. Source toggle: Webcam vs Upload
    source_type = st.radio(
        "Select Camera Input Source:",
        ["📁 Upload Onsite Photo", "📷 Live Browser Webcam"],
        horizontal=True
    )

    image_bytes = None
    filename = "webcam_snap.jpg"

    if source_type == "📷 Live Browser Webcam":
        # Streamlit premium webcam capture input widget
        camera_photo = st.camera_input("Capture live site check snap:")
        if camera_photo:
            image_bytes = camera_photo.read()
            filename = camera_photo.name
    else:
        uploaded_file = st.file_uploader(
            "Upload onsite site worker photo (JPG, PNG):",
            type=["jpg", "png", "jpeg"]
        )
        if uploaded_file:
            image_bytes = uploaded_file.read()
            filename = uploaded_file.name

    # 2. Display Analysis Results
    if image_bytes:
        with st.spinner("Analyzing image features and validating safety gear..."):
            try:
                results = APIClient.detect_ppe_violations(image_bytes, filename)
                
                col_img, col_metrics = st.columns([1.2, 1])

                with col_img:
                    st.markdown("### 🔍 Annotated Safety Detections")
                    # Render the base64 annotated image returned by the server
                    st.image(
                        results["annotated_image"],
                        caption="Computer Vision Highlighted Detections (Green = Compliant, Red = Missing/Violation)",
                        use_container_width=True
                    )

                with col_metrics:
                    st.markdown("### 📊 Safety Compliance Metrics")
                    score = results["compliance_score"]
                    
                    # Score gauge delta
                    delta_str = f"{score - 100}% deviation" if score < 100 else "100% Compliant"
                    st.metric(
                        label="Safety Compliance Score",
                        value=f"{score}%",
                        delta=delta_str,
                        delta_color="normal" if score == 100 else "inverse"
                    )

                    # List Detections status
                    st.markdown("#### Safety Equipment Verification:")
                    
                    detected_gear = results["detected_gear"]
                    missing_gear = results["missing_gear"]
                    
                    all_gear = ["Hard Hat", "Safety Vest", "Safety Boots", "Safety Harness", "Safety Goggles"]
                    for gear in all_gear:
                        if gear in detected_gear:
                            st.write(f"🟢 **{gear}**: Detected & Compliant")
                        else:
                            st.write(f"🔴 **{gear}**: MISSING (Violation)")

                    # High priority violations list
                    violations = results["violations"]
                    if violations:
                        st.markdown("---")
                        st.markdown("### ⚠️ Active Safety Alarms")
                        for violation in violations:
                            st.error(violation)
                    else:
                        st.success("🎉 All workers in frame are fully compliant with mandatory site PPE.")

            except Exception as e:
                st.error(f"Detection failed: {str(e)}")
    else:
        st.info("Capture a webcam snap or upload an onsite worker photo to run safety compliance checking.")
