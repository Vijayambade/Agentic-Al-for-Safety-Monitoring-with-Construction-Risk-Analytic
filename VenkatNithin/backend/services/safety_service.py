"""
backend/services/safety_service.py
----------------------------------
Safety Officer AI helper service for OSHA standards and emergency procedures.
"""
import logging
from typing import List, Dict
import google.generativeai as genai

from backend.config import settings
from backend.services.ai_service import call_construction_llm

logger = logging.getLogger(__name__)


def get_default_checklist(activity: str) -> List[str]:
    """Retrieve default safety checklist for common construction activities."""
    checklists = {
        "Scaffolding": [
            "Verify scaffolding foundation is rigid and level.",
            "Ensure guardrails (toprails at 42 inches and midrails) are installed.",
            "Scaffolding must be built under competent supervisor supervision.",
            "All workers on scaffolding must wear safety harnesses tied off to an anchor point.",
            "Inspect scaffold boards for cracks, rot, or damage before use."
        ],
        "Excavation": [
            "Locate and mark all underground utility lines before digging.",
            "Any trench deeper than 5 feet (1.5m) must have shoring, shielding, or sloping.",
            "Ensure ladders or escape ramps are placed within 25 feet of lateral travel.",
            "Inspect trench daily for cave-in risks, water buildup, or tension cracks.",
            "Keep excavated soil and equipment at least 2 feet away from the trench edge."
        ],
        "Welding": [
            "Inspect welding cables and grounding connections for damage.",
            "Ensure a certified fire extinguisher is within immediate reach.",
            "Use welding screens to protect other site personnel from flash burns.",
            "Wear shade-matching welding helmet, leather gloves, and protective apron.",
            "Check area for flammable gases, liquids, or dust before striking an arc."
        ],
        "Electrical": [
            "Implement Lockout/Tagout (LOTO) procedures before working on active circuits.",
            "Use ground fault circuit interrupters (GFCIs) on all power outlets.",
            "Inspect power tool extension cords for cuts, tears, or exposed wiring.",
            "Keep a minimum distance of 10 feet from overhead power lines.",
            "Wear insulated rubber gloves and safety boots rated for electrical work."
        ],
        "Concrete": [
            "Ensure formwork is fully braced and capable of supporting concrete weight.",
            "Wear chemical-resistant goggles and waterproof gloves when handling wet mix.",
            "Verify rebar ends are capped with safety caps to prevent impalement hazards.",
            "Ensure concrete pump lines are securely anchored with whipchecks.",
            "Ensure all workers wear steel-toed rubber boots during placing operations."
        ]
    }
    
    return checklists.get(activity, ["Complete standard toolbox talk.", "Inspect general PPE: hard hat, vest, safety boots."])


def get_emergency_sop(incident_type: str) -> str:
    """Retrieve step-by-step emergency procedures manual (First-Response)."""
    sops = {
        "Fire Outbreak": (
            "1. ACTIVATE ALARM: Shout 'FIRE' and trigger the nearest manual alarm pull station.\n"
            "2. EVACUATE: Immediately evacuate the building/site through designated fire exits. Do NOT use elevators.\n"
            "3. CALL FOR HELP: Call 911 or local emergency services once in a safe location.\n"
            "4. ASSEMBLE: Report to the designated Assembly Point. Supervisors must conduct a headcount.\n"
            "5. FIGHT (IF SAFE): Only use extinguishers on small, localized fires if trained and exit path is clear."
        ),
        "Gas Leak / Spill": (
            "1. EVACUATE IMMEDIATE AREA: Move upwind from the source of the leak immediately.\n"
            "2. ELIMINATE IGNITION: Turn off heavy machinery, combustion equipment, and cellphones. Do not toggle electrical switches.\n"
            "3. VENTILATE: If indoors, open doors and windows to dilute vapor if safe to do so.\n"
            "4. REPORT: Notify the Site Supervisor and call the emergency hazmat team.\n"
            "5. ISOLATE: Restrict site entry until clear air quality is verified."
        ),
        "Medical / Injury": (
            "1. ASSESS SCENE: Ensure the area is safe to enter before approaching the victim.\n"
            "2. DO NOT MOVE VICTIM: Unless there is immediate danger (e.g. fire, collapse) to prevent spinal injury.\n"
            "3. FIRST AID: Administer bleeding control (pressure) or CPR if certified and necessary.\n"
            "4. CALL EMS: Dispatch site first-aiders and call emergency response services.\n"
            "5. COMPANIONSHIP: Keep the victim warm, calm, and reassured until medical teams arrive."
        ),
        "Structural Collapse": (
            "1. TAKE COVER: Instantly take shelter under structural concrete elements or strong tables.\n"
            "2. EVACUATE: Exit the affected zone immediately. Avoid stairs, glass façades, and unsupported walls.\n"
            "3. SHUT DOWN UTILITIES: Supervisors should turn off main electrical panels and gas valves.\n"
            "4. HEADCOUNT: Assemble at the main assembly yard and verify roster presence.\n"
            "5. RESCUE TEAMS: Do not re-enter the collapse zone; wait for specialized urban rescue teams."
        )
    }
    
    return sops.get(incident_type, "Proceed to the main assembly yard and await further instructions from the Site Supervisor.")


def get_local_safety_officer_response(prompt: str, is_emergency: bool = False) -> str:
    """Rules-based safety advisor responder when LLM is unavailable."""
    prompt_lower = prompt.lower()
    
    if is_emergency:
        if "fire" in prompt_lower:
            return f"[🚨 EMERGENCY PROTOCOL - FIRE OUTBREAK]\n{get_emergency_sop('Fire Outbreak')}"
        elif "leak" in prompt_lower or "spill" in prompt_lower:
            return f"[🚨 EMERGENCY PROTOCOL - HAZARDOUS SPILL]\n{get_emergency_sop('Gas Leak / Spill')}"
        elif "injury" in prompt_lower or "hurt" in prompt_lower or "bleed" in prompt_lower or "medical" in prompt_lower:
            return f"[🚨 EMERGENCY PROTOCOL - MEDICAL INJURY]\n{get_emergency_sop('Medical / Injury')}"
        elif "collapse" in prompt_lower or "fall" in prompt_lower:
            return f"[🚨 EMERGENCY PROTOCOL - STRUCTURAL FAILURE]\n{get_emergency_sop('Structural Collapse')}"
        else:
            return (
                "[🚨 EMERGENCY ACTION REQUIRED]\n"
                "1. STOP all active machinery and hot work.\n"
                "2. Clear exit lanes and proceed to the central Muster Station.\n"
                "3. Contact emergency dispatchers and report to the Site Safety Lead."
            )

    # General safety questions fallbacks
    if "scaffold" in prompt_lower:
        checklist = "\n".join([f"- {item}" for item in get_default_checklist("Scaffolding")])
        return (
            "[Safety Officer Advisor - Scaffolding Compliance]\n"
            "Scaffolding represents high fall risks (OSHA 1926.451). Required check items:\n"
            f"{checklist}\n\n"
            "Action: Do not load scaffold beyond its capacity. Inspect mudsills and bracing daily."
        )
    elif "trench" in prompt_lower or "dig" in prompt_lower or "excavat" in prompt_lower:
        checklist = "\n".join([f"- {item}" for item in get_default_checklist("Excavation")])
        return (
            "[Safety Officer Advisor - Excavation Safety]\n"
            "Trench cave-ins occur within seconds (OSHA 1926.651). Required check items:\n"
            f"{checklist}\n\n"
            "Action: Ensure access ladders are secured and shoring systems are locked in."
        )
    elif "ppe" in prompt_lower or "gear" in prompt_lower or "protect" in prompt_lower:
        return (
            "[Safety Officer Advisor - Personal Protective Equipment]\n"
            "Mandatory Site PPE (ANSI/OSHA rules):\n"
            "- Hard Hats (ANSI Z89.1): Class G/E required in overhead hazard zones.\n"
            "- Safety Vest (Class 2/3): Required for high visibility around machinery.\n"
            "- Safety Glasses (ANSI Z87.1): Wrap-around frames for flying debris protection.\n"
            "- Steel-toed boots: Rated for compression and impact."
        )
    else:
        return (
            "[Safety Officer Advisor]\n"
            "All site activities must comply with OSHA Construction Standard 29 CFR 1926.\n"
            "Always inspect tools, review safety checklists, and complete the morning toolbox talk.\n"
            "Safety first: If you see a hazard, report it immediately."
        )


def call_safety_llm(prompt: str, is_emergency: bool = False) -> str:
    """
    Call Safety Officer AI assistant. Employs a strict safety systems prompt.
    Falls back to local rules-based safety database if LLM keys are absent.
    """
    if not settings.gemini_api_key:
        logger.info("Gemini key not configured. Using local safety Officer rules database.")
        return get_local_safety_officer_response(prompt, is_emergency)

    try:
        system_instruction = (
            "You are a Senior Construction Safety Officer and OSHA compliance inspector. "
            "You give clear, authoritative, and strict safety guidelines matching OSHA 29 CFR 1926. "
            "If the situation is flagged as an EMERGENCY, prioritize life safety, rescue protocols, "
            "and immediate first-aid/evacuation advice."
        )

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
        )

        # Append urgent flag to prompt if emergency
        if is_emergency:
            prompt = f"🚨 URGENT EMERGENCY SITUATION REPORTED 🚨\n{prompt}"

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error("Safety LLM invocation failed: %s. Using local fallback.", e)
        return get_local_safety_officer_response(prompt, is_emergency)
