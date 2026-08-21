import pandas as pd
import numpy as np


def format_currency(value: float, symbol: str = "₹") -> str:
    return f"{symbol}{value:,.0f}"


def generate_sample_projects(n: int = 12) -> pd.DataFrame:
    """Creates a synthetic project dataset so Analytics works before any real data exists."""
    rng = np.random.default_rng(42)
    names = [f"Project {chr(65 + i)}" for i in range(n)]
    types = rng.choice(
        ["Residential", "Commercial", "Industrial", "Infrastructure"], size=n
    )
    budget = rng.integers(2_000_000, 50_000_000, size=n)
    variance_pct = rng.normal(0, 0.12, size=n)
    actual = (budget * (1 + variance_pct)).astype(int)
    planned_days = rng.integers(60, 540, size=n)
    delay_pct = np.clip(rng.normal(0.08, 0.15, size=n), -0.2, 0.6)
    actual_days = (planned_days * (1 + delay_pct)).astype(int)
    progress = rng.integers(10, 100, size=n)
    status = np.where(progress == 100, "Completed",
              np.where(progress > 60, "On Track", "At Risk"))

    return pd.DataFrame({
        "Project": names,
        "Type": types,
        "Budget": budget,
        "ActualCost": actual,
        "PlannedDays": planned_days,
        "ActualDays": actual_days,
        "Progress%": progress,
        "Status": status,
    })
