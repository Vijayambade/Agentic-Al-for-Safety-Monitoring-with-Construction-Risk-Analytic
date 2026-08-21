from modules.estimation import build_estimate_summary_prompt


def test_build_estimate_summary_prompt_includes_project_context():
    prompt = build_estimate_summary_prompt(
        area_sqft=1800,
        floors=2,
        structure_type="RCC Frame",
        quality="Standard",
        city_tier="Tier 1 Metro",
        total_cost=12000000,
        breakdown={"Materials": 5400000, "Labor": 3000000},
        rate_used=2500,
    )

    assert "RCC Frame" in prompt
    assert "Standard" in prompt
    assert "Tier 1 Metro" in prompt
    assert "12,000,000" in prompt
    assert "cost-saving" in prompt.lower()
