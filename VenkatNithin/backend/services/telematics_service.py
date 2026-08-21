"""
backend/services/telematics_service.py
-------------------------------------
IoT sensor simulation and predictive maintenance calculation helper.
"""
import random
from typing import List, Any


def calculate_equipment_health(eq: Any) -> Any:
    """
    Evaluates temperature, vibration levels, and running hours to determine health.
    Computes health scores, failure probability, and toggles failure warning flags.
    """
    temp_deduction = 0.0
    vibration_deduction = 0.0
    hour_deduction = 0.0

    # 1. Temperature thresholds
    if eq.engine_temp > 95.0:
        overheat = eq.engine_temp - 95.0
        temp_deduction = min(40.0, overheat * 1.5)  # Max 40 points off
        if eq.engine_temp > 115.0:
            temp_deduction = 45.0

    # 2. Vibration thresholds
    if eq.vibration_level > 5.0:
        excess = eq.vibration_level - 5.0
        vibration_deduction = min(40.0, excess * 4.0)  # Max 40 points off
        if eq.vibration_level > 9.0:
            vibration_deduction = 45.0

    # 3. Operating hours thresholds (since last service)
    # Deduct small fraction for aging components
    hour_deduction = min(10.0, (eq.operating_hours % 1000) * 0.01)

    # 4. Calculate Final Health Score (0-100)
    health = 100.0 - temp_deduction - vibration_deduction - hour_deduction
    eq.health_score = max(0.0, min(100.0, round(health, 1)))

    # 5. Failure probability
    eq.failure_probability = round(100.0 - eq.health_score, 1)

    # 6. Flag Predicted Failure if health is critical
    eq.predicted_failure = (eq.health_score < 50.0)

    # Automatically swap status to Maintenance if health hits absolute 0 or if scheduled
    if eq.health_score <= 15.0 and eq.status != "Maintenance":
        eq.status = "Maintenance"

    return eq


def simulate_sensor_fluctuations(equipment: List[Any], stress_intensity: float) -> List[Any]:
    """
    Simulates operational runtime fluctuations (fuel drops, temp crawls).
    Applying higher stress_intensity triggers equipment failures.
    """
    for eq in equipment:
        if eq.status == "Maintenance":
            # Maintenance restores engine to cool baseline parameters
            eq.engine_temp = max(60.0, eq.engine_temp - 15.0)
            eq.vibration_level = max(1.5, eq.vibration_level - 1.0)
            continue

        # Normal operational fuel burn
        fuel_burn = random.uniform(1.0, 3.5)
        eq.fuel_level = max(0.0, round(eq.fuel_level - fuel_burn, 1))

        # Operational running hours count upward
        eq.operating_hours = round(eq.operating_hours + random.uniform(0.5, 1.5), 1)

        # Apply stress factor to temperature and vibrations
        if stress_intensity > 0.0:
            temp_increase = random.uniform(10.0, 30.0) * stress_intensity
            vib_increase = random.uniform(2.5, 6.0) * stress_intensity
            
            eq.engine_temp = round(eq.engine_temp + temp_increase, 1)
            eq.vibration_level = round(eq.vibration_level + vib_increase, 1)
        else:
            # Gentle normal fluctuation
            eq.engine_temp = max(70.0, min(95.0, round(eq.engine_temp + random.uniform(-2.0, 2.0), 1)))
            eq.vibration_level = max(1.0, min(5.0, round(eq.vibration_level + random.uniform(-0.5, 0.5), 1)))

        # Update health scores
        calculate_equipment_health(eq)

    return equipment
