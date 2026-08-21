"""
backend/services/schedule_service.py
------------------------------------
Critical Path Method (CPM) and automatic delay prediction rescheduling services.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Set, Any


def run_cpm_algorithm(tasks: List[Any]) -> List[Any]:
    """
    Computes Early Start (ES), Early Finish (EF), Late Start (LS), Late Finish (LF),
    and Slack Float for all tasks using Critical Path Method (CPM).
    Marks tasks with float == 0 as critical path tasks.
    """
    if not tasks:
        return []

    # Map tasks by ID for quick lookup
    task_map = {t.id: t for t in tasks}
    
    # 1. Parse dependencies
    adj_list: Dict[int, List[int]] = {t.id: [] for t in tasks}
    in_degree: Dict[int, int] = {t.id: 0 for t in tasks}
    
    for t in tasks:
        dep_str = t.dependencies.strip()
        if dep_str:
            dep_ids = [int(x.strip()) for x in dep_str.split(",") if x.strip().isdigit()]
            for dep_id in dep_ids:
                if dep_id in adj_list:
                    adj_list[dep_id].append(t.id)
                    in_degree[t.id] += 1

    # 2. Topological Sort (Kahn's Algorithm)
    queue = [t_id for t_id in in_degree if in_degree[t_id] == 0]
    topo_order = []
    
    # Copy degrees for sorting
    deg_copy = in_degree.copy()
    while queue:
        curr = queue.pop(0)
        topo_order.append(curr)
        for succ in adj_list[curr]:
            deg_copy[succ] -= 1
            if deg_copy[succ] == 0:
                queue.append(succ)

    # In case of cycles, fallback to simple ID ordering to avoid infinite hangs
    if len(topo_order) < len(tasks):
        topo_order = [t.id for t in tasks]

    # Project base start date (use the earliest start date among root tasks)
    proj_start = min(t.start_date for t in tasks) if tasks else datetime.utcnow()

    # Early calculations (Forward Pass)
    early_start: Dict[int, datetime] = {}
    early_finish: Dict[int, datetime] = {}

    for t_id in topo_order:
        t = task_map[t_id]
        total_duration = t.duration + t.predicted_delay
        
        dep_str = t.dependencies.strip()
        dep_ids = [int(x.strip()) for x in dep_str.split(",") if x.strip().isdigit() and int(x.strip()) in task_map]
        
        if not dep_ids:
            es = t.start_date  # baseline or root start
        else:
            # ES is the latest EF of all dependencies
            es = max(early_finish[dep_id] for dep_id in dep_ids)
            
        ef = es + timedelta(days=total_duration)
        early_start[t_id] = es
        early_finish[t_id] = ef

    # Project finish date is the maximum EF among all tasks
    proj_finish = max(early_finish.values()) if early_finish else proj_start

    # Late calculations (Backward Pass)
    late_start: Dict[int, datetime] = {}
    late_finish: Dict[int, datetime] = {}

    for t_id in reversed(topo_order):
        t = task_map[t_id]
        total_duration = t.duration + t.predicted_delay
        
        successors = adj_list[t_id]
        valid_succs = [s for s in successors if s in late_start]
        
        if not valid_succs:
            lf = proj_finish
        else:
            # LF is the earliest LS of all successors
            lf = min(late_start[succ] for succ in valid_succs)
            
        ls = lf - timedelta(days=total_duration)
        late_finish[t_id] = lf
        late_start[t_id] = ls

    # Apply computed dates, calculate float, and mark critical path
    for t in tasks:
        t_id = t.id
        es = early_start.get(t_id, t.start_date)
        ef = early_finish.get(t_id, t.start_date + timedelta(days=t.duration))
        ls = late_start.get(t_id, es)
        lf = late_finish.get(t_id, ef)
        
        # Total Float in days
        slack = (lf - ef).days
        
        # Update database fields
        t.start_date = es
        t.end_date = ef
        t.is_critical = (slack <= 0)
        
        # Save temporary float details if needed (or keep it simple for database fields)
        t.risk_factors = f"Slack Float: {slack} days. " + (t.risk_factors.split("Slack Float:")[0].strip() if "Slack Float:" in t.risk_factors else t.risk_factors)

    return tasks


def predict_schedule_delays(tasks: List[Any], weather_risk: float, labor_risk: float) -> List[Any]:
    """
    Predicts delay days for each task based on risk sliders,
    shifts successor dates down the dependency path, and re-computes CPM critical paths.
    """
    # 1. Calculate delay factors for each task
    for t in tasks:
        name = t.name.lower()
        
        weather_weight = 0.0
        labor_weight = 0.0
        max_delay = 0
        
        if "excavat" in name or "site prep" in name:
            weather_weight = 0.8  # Excavation highly affected by mud/rain
            labor_weight = 0.2
            max_delay = 10
        elif "foundation" in name or "concrete" in name:
            weather_weight = 0.6  # Concrete curing fails in cold/rain
            labor_weight = 0.4
            max_delay = 12
        elif "framing" in name or "structural" in name:
            weather_weight = 0.4
            labor_weight = 0.6  # Steel/Framing needs heavy onsite crew
            max_delay = 15
        elif "roofing" in name:
            weather_weight = 0.9  # Cannot install roof in high wind/rain
            labor_weight = 0.1
            max_delay = 8
        elif "finish" in name or "interior" in name:
            weather_weight = 0.1
            labor_weight = 0.9  # Plastering/Wiring highly dependent on labor
            max_delay = 14
        else:
            weather_weight = 0.3
            labor_weight = 0.7
            max_delay = 8

        # Delay prediction calculation
        factor = (weather_risk * weather_weight) + (labor_risk * labor_weight)
        delay_days = int(max_delay * factor)
        t.predicted_delay = delay_days
        
        # Set status warnings
        factors = []
        if weather_risk > 0.3 and weather_weight > 0.3:
            factors.append("Weather delays")
        if labor_risk > 0.3 and labor_weight > 0.3:
            factors.append("Labor shortages")
            
        t.risk_factors = " | ".join(factors) if factors else "None"

    # 2. Run Critical Path Method to recalculate dates and propagate delay shifts
    return run_cpm_algorithm(tasks)
