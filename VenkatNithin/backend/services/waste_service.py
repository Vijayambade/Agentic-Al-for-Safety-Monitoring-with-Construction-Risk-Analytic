"""
backend/services/waste_service.py
---------------------------------
Calculates waste diversion rates, recycling percentages, and generates reduction tips.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.waste import WasteLog, WasteGoal


def calculate_waste_analytics(db: Session) -> Dict[str, Any]:
    """
    Computes sustainability indicators:
    - Diversion Rate: % of waste kept out of landfills (Recycled + Reused).
    - Actual vs Goal quantities.
    - Rules-based dynamic sustainability suggestions.
    """
    logs = db.query(WasteLog).all()
    goals = db.query(WasteGoal).all()

    # 1. Group actual waste by type (convert all kg to Tons if mixed, but we assume consistent Tons/kg for simplicity)
    actuals: Dict[str, float] = {}
    total_waste = 0.0
    diverted_waste = 0.0

    for log in logs:
        qty = log.quantity
        actuals[log.waste_type] = actuals.get(log.waste_type, 0.0) + qty
        total_waste += qty
        if log.disposal_method in ("Recycled", "Reused"):
            diverted_waste += qty

    # 2. Audit and update goals
    goals_met = 0
    goals_list = []
    
    for goal in goals:
        actual_qty = actuals.get(goal.waste_type, 0.0)
        # Check if goal is achieved (actual is less than or equal to goal threshold)
        goal.achieved = (actual_qty <= goal.goal_quantity)
        if goal.achieved:
            goals_met += 1
            
        goals_list.append({
            "waste_type": goal.waste_type,
            "goal_quantity": goal.goal_quantity,
            "actual_quantity": round(actual_qty, 2),
            "unit": goal.unit,
            "achieved": goal.achieved
        })

    db.commit()

    # 3. Overall diversion rate
    diversion_rate = (diverted_waste / total_waste * 100) if total_waste > 0.0 else 100.0

    # 4. Generate dynamic sustainability tips
    tips = []
    for w_type, qty in actuals.items():
        # Match goal limit
        g_limit = next((g.goal_quantity for g in goals if g.waste_type == w_type), 999999.0)
        
        if qty > g_limit * 0.7:  # Alert if waste reaches 70% of goal limit
            if w_type == "Concrete":
                tips.append("🏗️ Concrete waste is high: Consider setting up an onsite mobile crusher to reuse rubble for roadbed gravel or subbase fill.")
            elif w_type == "Steel":
                tips.append("🔩 Steel offcuts are high: Set up dedicated metal recycle bins. Contact scrap dealers for sorting partnerships.")
            elif w_type == "Wood":
                tips.append("🪵 Wood scrap is high: Separate dimensional lumber offcuts for reuse in framing spacers, or chip wood on site for landscaping mulch.")
            elif w_type == "Packaging":
                tips.append("📦 Packaging waste is high: Demand supplier take-back programs for pallets, protective wraps, and drums to minimize landfill bins.")

    if not tips:
        tips.append("🟢 Sustainability performance is within normal bounds. Maintain active debris segregation at waste stations.")

    return {
        "total_waste": round(total_waste, 2),
        "diverted_waste": round(diverted_waste, 2),
        "diversion_rate": round(diversion_rate, 1),
        "goals_met": goals_met,
        "total_goals": len(goals),
        "goals": goals_list,
        "sustainability_tips": tips
    }
