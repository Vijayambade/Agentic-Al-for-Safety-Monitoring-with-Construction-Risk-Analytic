"""
backend/services/detection_service.py
-------------------------------------
Computer vision service for PPE object detection and safety compliance calculations.
"""
import base64
import io
import logging
import random
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def analyze_ppe_image(image_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Simulates onsite computer vision model analyzing an image.
    Uses PIL to draw bounding boxes representing detected and missing safety gear.
    Returns compliance score, lists of detected/missing items, and the base64-annotated image.
    """
    try:
        # Load image using PIL
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        
        # Ensure image is in RGB
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        draw = ImageDraw.Draw(image)
        
        # Simulated gear detection rules based on filename or randomness
        # We want to identify: Hard Hat, Safety Vest, Safety Boot, Harness, Safety Goggles
        fn_lower = filename.lower()
        
        # Fixed list of items to analyze
        ppe_items = ["Hard Hat", "Safety Vest", "Safety Boots", "Safety Harness", "Safety Goggles"]
        detected = []
        missing = []
        
        # Decide what is detected vs missing based on filename or randomized rules
        if "safe" in fn_lower or "compliant" in fn_lower:
            detected = ppe_items.copy()
        elif "violation" in fn_lower or "danger" in fn_lower:
            detected = ["Safety Boots", "Safety Goggles"]
            missing = ["Hard Hat", "Safety Vest", "Safety Harness"]
        else:
            # Random simulation to keep it dynamic and realistic
            for item in ppe_items:
                if random.random() > 0.3:  # 70% detection chance
                    detected.append(item)
                else:
                    missing.append(item)
                    
        # If everything is missing, add at least one detected to make the box look real
        if not detected:
            detected = ["Safety Boots"]
            missing = [i for i in ppe_items if i != "Safety Boots"]

        # Draw boxes on the image
        # Let's mock coordinate positions for bounding boxes
        box_coords = {
            "Hard Hat": [int(width * 0.4), int(height * 0.1), int(width * 0.6), int(height * 0.25)],
            "Safety Goggles": [int(width * 0.43), int(height * 0.22), int(width * 0.57), int(height * 0.30)],
            "Safety Vest": [int(width * 0.35), int(height * 0.32), int(width * 0.65), int(height * 0.65)],
            "Safety Harness": [int(width * 0.38), int(height * 0.30), int(width * 0.62), int(height * 0.70)],
            "Safety Boots": [int(width * 0.38), int(height * 0.80), int(width * 0.62), int(height * 0.95)]
        }

        # Select a font size relative to image size
        font_size = max(12, int(height * 0.025))
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        for item in ppe_items:
            coords = box_coords.get(item)
            if not coords:
                continue
                
            is_detected = item in detected
            color = (34, 197, 94) if is_detected else (239, 68, 68)  # Green vs Red
            label = f"{item}: Detected" if is_detected else f"MISSING: {item}"
            
            # Draw rectangle box
            draw.rectangle(coords, outline=color, width=4)
            
            # Draw label background
            text_pos = [coords[0], max(0, coords[1] - font_size - 4)]
            draw.rectangle(
                [text_pos[0], text_pos[1], text_pos[0] + len(label) * int(font_size * 0.6), text_pos[1] + font_size + 4],
                fill=color
            )
            # Draw text
            draw.text((text_pos[0] + 4, text_pos[1] + 2), label, fill=(255, 255, 255), font=font)

        # Calculate safety compliance score
        compliance_score = int((len(detected) / len(ppe_items)) * 100)
        
        # Save processed image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        base64_data = f"data:image/jpeg;base64,{img_str}"
        
        # Map safety violation warnings
        violations = []
        for item in missing:
            violations.append(f"Critical Violation: Worker identified without standard {item} in active zone.")
            
        return {
            "compliance_score": compliance_score,
            "detected_gear": detected,
            "missing_gear": missing,
            "violations": violations,
            "annotated_image": base64_data
        }
        
    except Exception as e:
        logger.error("Computer vision processing failed: %s", e)
        raise RuntimeError(f"CV Engine failed: {str(e)}")
