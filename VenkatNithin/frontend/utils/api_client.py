"""
frontend/utils/api_client.py
----------------------------
API Client to communicate with the FastAPI backend from Streamlit.
"""
import os
import requests
import streamlit as st
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class APIClient:
    """Client for making requests to the FastAPI backend."""

    @staticmethod
    def _get_headers() -> Dict[str, str]:
        """Generate common headers, injecting JWT token if present in session state."""
        headers = {"Content-Type": "application/json"}
        if "access_token" in st.session_state and st.session_state["access_token"]:
            token = st.session_state["access_token"]
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @staticmethod
    def _handle_response(response: requests.Response) -> Dict[str, Any]:
        """Parse response JSON or raise an informative exception on HTTP errors."""
        try:
            res_json = response.json()
        except ValueError:
            res_json = {"detail": response.text}

        if not response.ok:
            detail = res_json.get("detail", "An error occurred.")
            # If detail is list of validation errors, extract first error message
            if isinstance(detail, list):
                try:
                    detail = detail[0].get("msg", str(detail))
                except Exception:
                    pass
            raise Exception(detail)

        return res_json

    @classmethod
    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a POST request to the backend."""
        url = f"{BACKEND_URL}{endpoint}"
        headers = self._get_headers()
        try:
            response = requests.post(url, json=data, headers=headers, timeout=120)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection to backend failed: {str(e)}")

    @classmethod
    def get(self, endpoint: str) -> Dict[str, Any]:
        """Send a GET request to the backend."""
        url = f"{BACKEND_URL}{endpoint}"
        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers, timeout=120)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection to backend failed: {str(e)}")

    @classmethod
    def register(
        cls, email: str, password: str, first_name: str, last_name: str, role: str
    ) -> Dict[str, Any]:
        """Register a new user account."""
        payload = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
        }
        return cls.post("/api/v1/auth/register", data=payload)

    @classmethod
    def verify_otp(cls, email: str, otp_code: str) -> Dict[str, Any]:
        """Verify the user's OTP email verification code."""
        payload = {"email": email, "otp_code": otp_code}
        return cls.post("/api/v1/auth/verify-otp", data=payload)

    @classmethod
    def resend_otp(cls, email: str) -> Dict[str, Any]:
        """Resend OTP code to the user's email."""
        payload = {"email": email}
        return cls.post("/api/v1/auth/resend-otp", data=payload)

    @classmethod
    def login(
        cls, email: str, password: str, remember_me: bool = False
    ) -> Dict[str, Any]:
        """Log in with credentials and save the token to the session state."""
        payload = {"email": email, "password": password, "remember_me": remember_me}
        res = cls.post("/api/v1/auth/login", data=payload)

        # Store details in Streamlit session state
        st.session_state["access_token"] = res.get("access_token")
        st.session_state["user_role"] = res.get("role")
        st.session_state["user_email"] = res.get("email")
        st.session_state["authenticated"] = True

        return res

    @classmethod
    def logout(cls) -> Optional[Dict[str, Any]]:
        """Log out the current user, clearing session state."""
        res = None
        try:
            res = cls.post("/api/v1/auth/logout")
        except Exception:
            # Silence backend session clearing error if backend is down
            pass

        # Clear session credentials
        st.session_state["access_token"] = None
        st.session_state["user_role"] = None
        st.session_state["user_email"] = None
        st.session_state["authenticated"] = False
        st.session_state["user_profile"] = None

        return res

    @classmethod
    def forgot_password(cls, email: str) -> Dict[str, Any]:
        """Initiate password recovery."""
        payload = {"email": email}
        return cls.post("/api/v1/auth/forgot-password", data=payload)

    @classmethod
    def reset_password(
        cls, email: str, otp_code: str, new_password: str
    ) -> Dict[str, Any]:
        """Reset user password using token/OTP."""
        payload = {
            "email": email,
            "otp_code": otp_code,
            "new_password": new_password,
        }
        return cls.post("/api/v1/auth/reset-password", data=payload)

    @classmethod
    def get_me(cls) -> Dict[str, Any]:
        """Fetch current user profile data."""
        res = cls.get("/api/v1/auth/me")
        st.session_state["user_profile"] = res
        return res

    @classmethod
    def get_dashboard_stats(cls) -> Dict[str, Any]:
        """Fetch all stats, charts, tasks, and notifications for current user's role."""
        return cls.get("/api/v1/dashboard/stats")

    @classmethod
    def create_dashboard_task(
        cls, title: str, description: Optional[str] = None, due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new task on the user's dashboard."""
        payload = {"title": title, "description": description}
        if due_date:
            payload["due_date"] = due_date
        return cls.post("/api/v1/dashboard/tasks", data=payload)

    @classmethod
    def update_dashboard_task(cls, task_id: int, is_completed: bool) -> Dict[str, Any]:
        """Toggle task completion state."""
        payload = {"is_completed": is_completed}
        return cls.post(f"/api/v1/dashboard/tasks/{task_id}", data=payload)

    @classmethod
    def log_dashboard_activity(cls, action_type: str, description: str) -> Dict[str, Any]:
        """Log a custom dashboard action."""
        payload = {"action_type": action_type, "description": description}
        return cls.post("/api/v1/dashboard/activities", data=payload)

    @classmethod
    def send_dashboard_chat(cls, message: str) -> Dict[str, Any]:
        """Send a chat message to the contextual assistant."""
        payload = {"message": message}
        return cls.post("/api/v1/dashboard/chat", data=payload)

    @classmethod
    def send_general_chat(
        cls,
        session_id: str,
        prompt: Optional[str] = None,
        language: str = "en",
        audio: Optional[bytes] = None,
        image: Optional[bytes] = None,
        document: Optional[bytes] = None,
        doc_name: str = "document.pdf",
        img_name: str = "image.jpg",
    ) -> Dict[str, Any]:
        """Send general assistant chat with optional multimodal files and speech audio."""
        url = f"{BACKEND_URL}/api/v1/ai/general-chat"
        headers = {}
        if "access_token" in st.session_state and st.session_state["access_token"]:
            token = st.session_state["access_token"]
            headers["Authorization"] = f"Bearer {token}"
            
        data = {"session_id": session_id, "language": language}
        if prompt:
            data["prompt"] = prompt
            
        files = {}
        if audio:
            files["audio"] = ("speech.wav", audio, "audio/wav")
        if image:
            files["image"] = (img_name, image, "image/jpeg")
        if document:
            files["document"] = (doc_name, document, "application/octet-stream")
            
        try:
            response = requests.post(url, data=data, files=files, headers=headers, timeout=180)
            return cls._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection to backend failed: {str(e)}")

    @classmethod
    def get_general_chat_history(cls, session_id: str) -> Dict[str, Any]:
        """Get history for a general chat session."""
        return cls.get(f"/api/v1/ai/general-chat/history/{session_id}")

    @classmethod
    def clear_general_chat_history(cls, session_id: str) -> Dict[str, Any]:
        """Delete dialogue logs for a session."""
        url = f"{BACKEND_URL}/api/v1/ai/general-chat/history/{session_id}"
        headers = cls._get_headers()
        try:
            response = requests.delete(url, headers=headers, timeout=30)
            return cls._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection to backend failed: {str(e)}")

    @classmethod
    def upload_analyzed_document(cls, file_bytes: bytes, file_name: str) -> Dict[str, Any]:
        """Upload document to perform text extraction, audits, and FAISS indexing."""
        url = f"{BACKEND_URL}/api/v1/document-analyzer/upload"
        headers = {}
        if "access_token" in st.session_state and st.session_state["access_token"]:
            token = st.session_state["access_token"]
            headers["Authorization"] = f"Bearer {token}"
            
        files = {"file": (file_name, file_bytes, "application/octet-stream")}
        try:
            response = requests.post(url, files=files, headers=headers, timeout=180)
            return cls._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection to backend failed: {str(e)}")

    @classmethod
    def query_analyzed_document(cls, doc_id: int, question: str) -> Dict[str, Any]:
        """Send question to query uploaded document context via RAG."""
        payload = {"document_id": doc_id, "question": question}
        return cls.post("/api/v1/document-analyzer/query", data=payload)

    @classmethod
    def list_analyzed_documents(cls) -> List[Dict[str, Any]]:
        """List all analyzed documents available for current user context."""
        return cls.get("/api/v1/document-analyzer/list")

    @classmethod
    def get_analyzed_document_details(cls, doc_id: int) -> Dict[str, Any]:
        """Get full report analysis audits for a specific document."""
        return cls.get(f"/api/v1/document-analyzer/details/{doc_id}")

    @classmethod
    def send_safety_chat(cls, message: str, is_emergency: bool = False) -> Dict[str, Any]:
        """Query Safety Officer AI assistant chatbot."""
        payload = {"message": message, "is_emergency": is_emergency}
        return cls.post("/api/v1/safety/chat", data=payload)

    @classmethod
    def report_safety_hazard(cls, description: str, severity: str) -> Dict[str, Any]:
        """File a safety incident or hazard log."""
        payload = {"hazard_description": description, "severity": severity}
        return cls.post("/api/v1/safety/incidents", data=payload)

    @classmethod
    def get_safety_checklist(cls, activity: str) -> List[str]:
        """Get standard checklists for activities."""
        return cls.get(f"/api/v1/safety/checklist?activity={activity}")

    @classmethod
    def get_emergency_sop(cls, incident_type: str) -> Dict[str, str]:
        """Get step-by-step SOP instructions."""
        return cls.get(f"/api/v1/safety/emergency-sop?incident_type={incident_type}")

    @classmethod
    def detect_ppe_violations(cls, image_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Upload onsite webcam snap to perform computer vision safety detection."""
        url = f"{BACKEND_URL}/api/v1/safety-monitoring/detect"
        headers = {}
        if "access_token" in st.session_state and st.session_state["access_token"]:
            token = st.session_state["access_token"]
            headers["Authorization"] = f"Bearer {token}"
            
        files = {"file": (filename, image_bytes, "image/jpeg")}
        try:
            response = requests.post(url, files=files, headers=headers, timeout=30)
            return cls._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection to backend failed: {str(e)}")

    @classmethod
    def get_schedule_tasks(cls) -> List[Dict[str, Any]]:
        """Retrieve construction scheduling tasks and calculations."""
        return cls.get("/api/v1/schedule/tasks")

    @classmethod
    def predict_schedule_delays(cls, weather_risk: float, labor_risk: float) -> List[Dict[str, Any]]:
        """Trigger AI schedule delay simulator and rescheduling."""
        payload = {"weather_risk": weather_risk, "labor_risk": labor_risk}
        return cls.post("/api/v1/schedule/predict", data=payload)

    @classmethod
    def reset_schedule_tasks(cls) -> List[Dict[str, Any]]:
        """Reset database schedules to baseline project definitions."""
        return cls.post("/api/v1/schedule/reset", data={})

    @classmethod
    def get_telematics_equipment(cls) -> List[Dict[str, Any]]:
        """Retrieve equipment telematics fleet status and sensors."""
        return cls.get("/api/v1/telematics/equipment")

    @classmethod
    def simulate_telematics_sensors(cls, stress_intensity: float) -> List[Dict[str, Any]]:
        """Trigger operational stress loads on fleet machinery sensor variables."""
        payload = {"stress_intensity": stress_intensity}
        return cls.post("/api/v1/telematics/simulate", data=payload)

    @classmethod
    def schedule_equipment_maintenance(cls, equipment_id: int, scheduled_date: str) -> Dict[str, Any]:
        """Submit customized maintenance scheduling dates for fleet vehicles."""
        payload = {"equipment_id": equipment_id, "scheduled_date": scheduled_date}
        return cls.post("/api/v1/telematics/schedule-maintenance", data=payload)

    @classmethod
    def reset_telematics_equipment(cls) -> List[Dict[str, Any]]:
        """Revert fleet parameters to healthy baseline configurations."""
        return cls.post("/api/v1/telematics/reset", data={})

    @classmethod
    def get_inventory_stocks(cls) -> List[Dict[str, Any]]:
        """Retrieve material inventory stock details."""
        return cls.get("/api/v1/inventory/stocks")

    @classmethod
    def get_inventory_orders(cls) -> List[Dict[str, Any]]:
        """Retrieve historical material orders and delivery statuses."""
        return cls.get("/api/v1/inventory/orders")

    @classmethod
    def consume_inventory_material(cls, material_id: int, quantity: float, waste: float) -> Dict[str, Any]:
        """Log material consumption and waste metrics."""
        payload = {"material_id": material_id, "quantity": quantity, "waste": waste}
        return cls.post("/api/v1/inventory/consume", data=payload)

    @classmethod
    def reorder_inventory_material(cls, material_id: int, order_quantity: float) -> Dict[str, Any]:
        """Dispatch a purchase order to restock a material."""
        payload = {"material_id": material_id, "order_quantity": order_quantity}
        return cls.post("/api/v1/inventory/reorder", data=payload)

    @classmethod
    def update_order_delivery_status(cls, order_id: int, status: str) -> Dict[str, Any]:
        """Update purchase order status (Shipped or Delivered)."""
        payload = {"order_id": order_id, "status": status}
        return cls.post("/api/v1/inventory/update-delivery", data=payload)

    @classmethod
    def reset_inventory_data(cls) -> List[Dict[str, Any]]:
        """Revert material stock parameters to baseline settings."""
        return cls.post("/api/v1/inventory/reset", data={})

    @classmethod
    def get_waste_logs(cls) -> List[Dict[str, Any]]:
        """Retrieve logged waste events."""
        return cls.get("/api/v1/waste/logs")

    @classmethod
    def get_waste_goals(cls) -> List[Dict[str, Any]]:
        """Retrieve waste reduction goals."""
        return cls.get("/api/v1/waste/goals")

    @classmethod
    def get_waste_analytics(cls) -> Dict[str, Any]:
        """Retrieve dynamic waste diversion statistics and reduction suggestions."""
        return cls.get("/api/v1/waste/analytics")

    @classmethod
    def log_waste_disposal(cls, waste_type: str, quantity: float, unit: str, disposal_method: str, cost: float) -> Dict[str, Any]:
        """Log a site waste disposal event."""
        payload = {
            "waste_type": waste_type,
            "quantity": quantity,
            "unit": unit,
            "disposal_method": disposal_method,
            "cost": cost
        }
        return cls.post("/api/v1/waste/log", data=payload)

    @classmethod
    def update_waste_goal(cls, waste_type: str, goal_quantity: float, unit: str) -> Dict[str, Any]:
        """Set or update waste category target limit."""
        payload = {
            "waste_type": waste_type,
            "goal_quantity": goal_quantity,
            "unit": unit
        }
        return cls.post("/api/v1/waste/goal", data=payload)

    @classmethod
    def reset_waste_data(cls) -> List[Dict[str, Any]]:
        """Revert waste logs and targets back to baseline configurations."""
        return cls.post("/api/v1/waste/reset", data={})

    @classmethod
    def get_noise_logs(cls) -> List[Dict[str, Any]]:
        """Retrieve decibel sensor logs."""
        return cls.get("/api/v1/noise/logs")

    @classmethod
    def get_noise_configs(cls) -> List[Dict[str, Any]]:
        """Retrieve decibel sensor configs."""
        return cls.get("/api/v1/noise/configs")

    @classmethod
    def log_noise_decibel(cls, sensor_name: str, decibel_level: float) -> Dict[str, Any]:
        """Manually submit a decibel sensor reading."""
        payload = {"sensor_name": sensor_name, "decibel_level": decibel_level}
        return cls.post("/api/v1/noise/log", data=payload)

    @classmethod
    def simulate_noise_decibels(cls, stress_intensity: float) -> List[Dict[str, Any]]:
        """Trigger simulated decibel fluctuations across sensor zones."""
        payload = {"stress_intensity": stress_intensity}
        return cls.post("/api/v1/noise/simulate", data=payload)

    @classmethod
    def update_noise_config(cls, sensor_name: str, daytime_limit: float, nighttime_limit: float) -> Dict[str, Any]:
        """Calibrate daytime and nighttime decibel thresholds for a sensor."""
        payload = {
            "sensor_name": sensor_name,
            "daytime_limit": daytime_limit,
            "nighttime_limit": nighttime_limit
        }
        return cls.post("/api/v1/noise/config", data=payload)

    @classmethod
    def reset_noise_data(cls) -> List[Dict[str, Any]]:
        """Clear decibel log histories and revert configs back to baselines."""
        return cls.post("/api/v1/noise/reset", data={})

    @classmethod
    def get_air_quality_logs(cls) -> List[Dict[str, Any]]:
        """Retrieve environmental sensor air quality logs."""
        return cls.get("/api/v1/air-quality/logs")

    @classmethod
    def get_air_quality_configs(cls) -> List[Dict[str, Any]]:
        """Retrieve safety threshold configs for air monitoring."""
        return cls.get("/api/v1/air-quality/configs")

    @classmethod
    def log_air_quality(cls, sensor_name: str, aqi: float, pm25: float, pm10: float, co_level: float, no2_level: float, voc_level: float) -> Dict[str, Any]:
        """Manually log an air quality reading."""
        payload = {
            "sensor_name": sensor_name,
            "aqi": aqi,
            "pm25": pm25,
            "pm10": pm10,
            "co_level": co_level,
            "no2_level": no2_level,
            "voc_level": voc_level
        }
        return cls.post("/api/v1/air-quality/log", data=payload)

    @classmethod
    def simulate_air_quality(cls, stress_intensity: float) -> List[Dict[str, Any]]:
        """Trigger simulated gas leak / particulate spikes across sensor zones."""
        payload = {"stress_intensity": stress_intensity}
        return cls.post("/api/v1/air-quality/simulate", data=payload)

    @classmethod
    def update_air_quality_config(cls, sensor_name: str, pm25_limit: float, co_limit: float, voc_limit: float) -> Dict[str, Any]:
        """Calibrate PM2.5, CO, and VOC gas thresholds for a sensor."""
        payload = {
            "sensor_name": sensor_name,
            "pm25_limit": pm25_limit,
            "co_limit": co_limit,
            "voc_limit": voc_limit
        }
        return cls.post("/api/v1/air-quality/config", data=payload)

    @classmethod
    def reset_air_quality_data(cls) -> List[Dict[str, Any]]:
        """Clear air log histories and revert configs back to baselines."""
        return cls.post("/api/v1/air-quality/reset", data={})

    @classmethod
    def get_water_logs(cls) -> List[Dict[str, Any]]:
        """Retrieve water telemetry logs."""
        return cls.get("/api/v1/water/logs")

    @classmethod
    def get_water_configs(cls) -> List[Dict[str, Any]]:
        """Retrieve water sensor threshold configs."""
        return cls.get("/api/v1/water/configs")

    @classmethod
    def log_water_reading(cls, sensor_name: str, flow_rate: float, pressure: float, cumulative_liters: float) -> Dict[str, Any]:
        """Manually log a water sensor reading."""
        payload = {
            "sensor_name": sensor_name,
            "flow_rate": flow_rate,
            "pressure": pressure,
            "cumulative_liters": cumulative_liters
        }
        return cls.post("/api/v1/water/log", data=payload)

    @classmethod
    def simulate_water_flow(cls, stress_intensity: float) -> List[Dict[str, Any]]:
        """Trigger simulated water pressure / flow changes across zones."""
        payload = {"stress_intensity": stress_intensity}
        return cls.post("/api/v1/water/simulate", data=payload)

    @classmethod
    def update_water_config(cls, sensor_name: str, max_flow_limit: float, min_pressure_limit: float) -> Dict[str, Any]:
        """Calibrate max flow and min pressure limits for a water sensor."""
        payload = {
            "sensor_name": sensor_name,
            "max_flow_limit": max_flow_limit,
            "min_pressure_limit": min_pressure_limit
        }
        return cls.post("/api/v1/water/config", data=payload)

    @classmethod
    def reset_water_data(cls) -> List[Dict[str, Any]]:
        """Clear water log histories and revert configs back to baselines."""
        return cls.post("/api/v1/water/reset", data={})

    @classmethod
    def get_structural_logs(cls) -> List[Dict[str, Any]]:
        """Retrieve structural health telemetry logs."""
        return cls.get("/api/v1/structural/logs")

    @classmethod
    def get_structural_configs(cls) -> List[Dict[str, Any]]:
        """Retrieve structural sensor threshold configs."""
        return cls.get("/api/v1/structural/configs")

    @classmethod
    def log_structural_reading(cls, sensor_name: str, vibration_frequency: float, amplitude: float, tilt_angle: float, strain: float) -> Dict[str, Any]:
        """Manually log structural safety telemetry parameters."""
        payload = {
            "sensor_name": sensor_name,
            "vibration_frequency": vibration_frequency,
            "amplitude": amplitude,
            "tilt_angle": tilt_angle,
            "strain": strain
        }
        return cls.post("/api/v1/structural/log", data=payload)

    @classmethod
    def simulate_structural_health(cls, stress_intensity: float) -> List[Dict[str, Any]]:
        """Trigger simulated vibration, load stress, and tilt deviations across structures."""
        payload = {"stress_intensity": stress_intensity}
        return cls.post("/api/v1/structural/simulate", data=payload)

    @classmethod
    def update_structural_config(cls, sensor_name: str, max_vibration_frequency: float, max_tilt_angle: float, max_strain: float) -> Dict[str, Any]:
        """Calibrate max vibration, tilt, and strain safety boundaries for a structure."""
        payload = {
            "sensor_name": sensor_name,
            "max_vibration_frequency": max_vibration_frequency,
            "max_tilt_angle": max_tilt_angle,
            "max_strain": max_strain
        }
        return cls.post("/api/v1/structural/config", data=payload)

    @classmethod
    def reset_structural_data(cls) -> List[Dict[str, Any]]:
        """Clear structural logs and restore baseline safety configurations."""
        return cls.post("/api/v1/structural/reset", data={})

    @classmethod
    def get_energy_logs(cls) -> List[Dict[str, Any]]:
        """Retrieve energy smart meter logs."""
        return cls.get("/api/v1/energy/logs")

    @classmethod
    def get_energy_configs(cls) -> List[Dict[str, Any]]:
        """Retrieve energy sensor threshold configs."""
        return cls.get("/api/v1/energy/configs")

    @classmethod
    def log_energy_reading(cls, sensor_name: str, power_usage: float, voltage: float, current: float, power_factor: float, cumulative_kwh: float) -> Dict[str, Any]:
        """Manually log energy safety telemetry parameters."""
        payload = {
            "sensor_name": sensor_name,
            "power_usage": power_usage,
            "voltage": voltage,
            "current": current,
            "power_factor": power_factor,
            "cumulative_kwh": cumulative_kwh
        }
        return cls.post("/api/v1/energy/log", data=payload)

    @classmethod
    def simulate_energy_flow(cls, stress_intensity: float) -> List[Dict[str, Any]]:
        """Trigger simulated load fluctuations across smart meters."""
        payload = {"stress_intensity": stress_intensity}
        return cls.post("/api/v1/energy/simulate", data=payload)

    @classmethod
    def update_energy_config(cls, sensor_name: str, max_power_limit: float, min_voltage_limit: float, min_power_factor_limit: float) -> Dict[str, Any]:
        """Calibrate max power, min voltage, and power factor safety boundaries for a smart meter."""
        payload = {
            "sensor_name": sensor_name,
            "max_power_limit": max_power_limit,
            "min_voltage_limit": min_voltage_limit,
            "min_power_factor_limit": min_power_factor_limit
        }
        return cls.post("/api/v1/energy/config", data=payload)

    @classmethod
    def reset_energy_data(cls) -> List[Dict[str, Any]]:
        """Clear energy logs and restore baseline safety configurations."""
        return cls.post("/api/v1/energy/reset", data={})

    @classmethod
    def get_weather_logs(cls) -> List[Dict[str, Any]]:
        """Retrieve weather sensor telemetry logs."""
        return cls.get("/api/v1/weather/logs")

    @classmethod
    def get_weather_configs(cls) -> List[Dict[str, Any]]:
        """Retrieve weather sensor threshold configs."""
        return cls.get("/api/v1/weather/configs")

    @classmethod
    def log_weather_reading(cls, sensor_name: str, temperature: float, wind_speed: float, humidity: float, precipitation: float, barometric_pressure: float, uv_index: float) -> Dict[str, Any]:
        """Manually log weather safety telemetry parameters."""
        payload = {
            "sensor_name": sensor_name,
            "temperature": temperature,
            "wind_speed": wind_speed,
            "humidity": humidity,
            "precipitation": precipitation,
            "barometric_pressure": barometric_pressure,
            "uv_index": uv_index
        }
        return cls.post("/api/v1/weather/log", data=payload)

    @classmethod
    def simulate_weather_flow(cls, stress_intensity: float) -> List[Dict[str, Any]]:
        """Trigger simulated weather variations and storm events across sensors."""
        payload = {"stress_intensity": stress_intensity}
        return cls.post("/api/v1/weather/simulate", data=payload)

    @classmethod
    def update_weather_config(cls, sensor_name: str, max_wind_speed_limit: float, max_temp_limit: float, max_precipitation_limit: float) -> Dict[str, Any]:
        """Calibrate max wind, max temp, and max rain safety boundaries for weather monitoring."""
        payload = {
            "sensor_name": sensor_name,
            "max_wind_speed_limit": max_wind_speed_limit,
            "max_temp_limit": max_temp_limit,
            "max_precipitation_limit": max_precipitation_limit
        }
        return cls.post("/api/v1/weather/config", data=payload)

    @classmethod
    def reset_weather_data(cls) -> List[Dict[str, Any]]:
        """Clear weather logs and restore baseline safety configurations."""
        return cls.post("/api/v1/weather/reset", data={})

    @classmethod
    def get_developer_otp(cls, email: str) -> Dict[str, Any]:
        """Fetch simulated active OTP for local testing."""
        return cls.get(f"/api/v1/auth/developer/get-otp?email={email}")

    @classmethod
    def calculate_material_estimation(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quantity takeoff and total cost estimate."""
        return cls.post("/api/v1/material-estimation/estimate", data=payload)

    @classmethod
    def export_material_estimation_pdf(cls, payload: Dict[str, Any]) -> bytes:
        """Fetch PDF export byte stream from backend."""
        url = f"{BACKEND_URL}/api/v1/material-estimation/export-pdf"
        headers = cls._get_headers()
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if not response.ok:
            raise Exception("Failed to generate PDF export.")
        return response.content

    @classmethod
    def export_material_estimation_csv(cls, payload: Dict[str, Any]) -> str:
        """Fetch CSV export text string from backend."""
        url = f"{BACKEND_URL}/api/v1/material-estimation/export-csv"
        headers = cls._get_headers()
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if not response.ok:
            raise Exception("Failed to generate CSV export.")
        return response.text
