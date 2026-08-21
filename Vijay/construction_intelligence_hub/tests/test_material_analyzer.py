from modules.material_management import parse_ai_response, calculate_materials

def test_parse_ai_response_success():
    response = (
        "AREA_SQFT: 1500\n"
        "FLOORS: 3\n"
        "STRUCTURE_TYPE: Steel Structure\n"
        "ANALYSIS_REPORT:\n"
        "This is a detailed analysis report.\n"
        "It contains cement, steel details."
    )
    area, floors, struct_type, report = parse_ai_response(response)
    
    assert area == 1500.0
    assert floors == 3
    assert struct_type == "Steel Structure"
    assert "This is a detailed analysis report." in report
    assert "It contains cement, steel details." in report

def test_parse_ai_response_partial():
    response = (
        "AREA_SQFT: Unknown\n"
        "FLOORS: 2\n"
        "STRUCTURE_TYPE: RCC Frame\n"
        "ANALYSIS_REPORT:\n"
        "Report body here."
    )
    area, floors, struct_type, report = parse_ai_response(response)
    
    assert area is None
    assert floors == 2
    assert struct_type == "RCC Frame"
    assert "Report body here." in report

def test_parse_ai_response_missing_report_header():
    response = (
        "AREA_SQFT: 2000.5\n"
        "FLOORS: Unknown\n"
        "STRUCTURE_TYPE: Unknown\n"
        "No explicit report header, just standard text."
    )
    area, floors, struct_type, report = parse_ai_response(response)
    
    assert area == 2000.5
    assert floors is None
    assert struct_type is None
    assert "No explicit report header" in report

def test_calculate_materials_values():
    # RCC Frame factors: Cement=0.12, Bricks=10, Steel=3.0, etc.
    # Total area: 1000 * 2 = 2000
    estimates = calculate_materials(1000, 2, "RCC Frame")
    
    assert estimates["Cement (bags)"] == 240.0
    assert estimates["Bricks (pieces)"] == 20000.0
    assert estimates["Steel (kg)"] == 6000.0
