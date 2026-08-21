"""
backend/services/material_estimation_service.py
------------------------------------------------
Modular service for construction material estimation, formulas, PDF report generation,
and CSV exports.
"""
import io
import csv
import logging
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.schemas.material_estimation import MaterialEstimationRequest

logger = logging.getLogger(__name__)

# Base rates (in USD / currency units) per unit quantity for Standard quality
BASE_UNIT_RATES = {
    "Cement": 9.50,           # per bag
    "Sand": 2.20,             # per cu. ft.
    "Steel": 1.15,            # per kg
    "Bricks": 0.65,           # per piece
    "Concrete": 95.00,        # per cu. meter
    "Aggregate": 2.50,        # per cu. ft.
    "Paint": 18.00,           # per liter
    "Tiles": 3.50,            # per sq. ft.
    "Electrical Materials": 150.00, # per set package
    "Plumbing Materials": 180.00,   # per set package
}

# Material Units
MATERIAL_UNITS = {
    "Cement": "Bags",
    "Sand": "Cu. Ft.",
    "Steel": "Kg",
    "Bricks": "Pieces",
    "Concrete": "Cu. Meters",
    "Aggregate": "Cu. Ft.",
    "Paint": "Liters",
    "Tiles": "Sq. Ft.",
    "Electrical Materials": "Sets",
    "Plumbing Materials": "Sets",
}

# Quantity coefficients per 1 sq. ft. of built-up area for RCC structure
BASE_COEFFICIENTS_RCC = {
    "Cement": 0.40,
    "Sand": 1.80,
    "Steel": 4.00,
    "Bricks": 8.00,
    "Concrete": 0.05,
    "Aggregate": 1.35,
    "Paint": 0.15,
    "Tiles": 1.10,
    "Electrical Materials": 0.010,
    "Plumbing Materials": 0.007,
}

BASE_COEFFICIENTS_STEEL = {
    "Cement": 0.25,
    "Sand": 1.20,
    "Steel": 7.50,
    "Bricks": 5.00,
    "Concrete": 0.03,
    "Aggregate": 0.90,
    "Paint": 0.20,
    "Tiles": 1.10,
    "Electrical Materials": 0.012,
    "Plumbing Materials": 0.007,
}

BASE_COEFFICIENTS_HYBRID = {
    "Cement": 0.35,
    "Sand": 1.50,
    "Steel": 5.50,
    "Bricks": 6.50,
    "Concrete": 0.04,
    "Aggregate": 1.15,
    "Paint": 0.18,
    "Tiles": 1.10,
    "Electrical Materials": 0.011,
    "Plumbing Materials": 0.007,
}

PROJECT_TYPE_FACTORS = {
    "Residential": 1.00,
    "Commercial": 1.15,
    "Industrial": 1.25,
}

QUALITY_COST_MULTIPLIERS = {
    "Standard": 1.00,
    "Premium": 1.40,
    "Luxury": 2.00,
}

QUALITY_QUANTITY_MULTIPLIERS = {
    "Standard": 1.00,
    "Premium": 1.05,
    "Luxury": 1.10,
}


def calculate_material_estimation(req: MaterialEstimationRequest) -> Dict[str, Any]:
    """
    Calculate estimated material quantities and costs based on input parameters.
    Returns structured data for table, summary metrics, and chart rendering.
    """
    # 1. Standardize area to square feet
    area_sqft = req.built_up_area
    if req.area_unit.lower() in ["sq_m", "sq m", "sqm", "square meters", "square_meters"]:
        area_sqft = req.built_up_area * 10.7639

    total_effective_area = area_sqft * req.floors

    # 2. Select baseline coefficients based on Construction Type
    c_type = req.construction_type.lower()
    if "steel" in c_type:
        base_coeff = BASE_COEFFICIENTS_STEEL
    elif "hybrid" in c_type:
        base_coeff = BASE_COEFFICIENTS_HYBRID
    else:
        base_coeff = BASE_COEFFICIENTS_RCC

    # 3. Floor structural adjustment factor (for load bearing above 3 floors)
    floor_factor = 1.0
    if req.floors > 3:
        floor_factor += (req.floors - 3) * 0.015

    # 4. Multipliers
    proj_type_factor = PROJECT_TYPE_FACTORS.get(req.project_type, 1.00)
    qual_cost_factor = QUALITY_COST_MULTIPLIERS.get(req.material_quality, 1.00)
    qual_qty_factor = QUALITY_QUANTITY_MULTIPLIERS.get(req.material_quality, 1.00)

    materials_result: List[Dict[str, Any]] = []
    total_cost = 0.0
    cost_breakdown: Dict[str, float] = {}
    material_distribution: Dict[str, float] = {}

    for mat_name, base_rate in BASE_UNIT_RATES.items():
        coeff = base_coeff.get(mat_name, 1.0)
        
        # Apply structural floor factor to structural materials (Cement, Steel, Concrete)
        mat_floor_factor = floor_factor if mat_name in ["Cement", "Steel", "Concrete"] else 1.0
        
        # Quantity calculation
        qty = total_effective_area * coeff * proj_type_factor * qual_qty_factor * mat_floor_factor
        
        # Rate per unit calculation
        unit_rate = base_rate * qual_cost_factor
        item_cost = qty * unit_rate
        
        # Rounding for clean display
        qty_rounded = round(qty, 2)
        cost_rounded = round(item_cost, 2)
        
        materials_result.append({
            "material_name": mat_name,
            "estimated_quantity": qty_rounded,
            "unit": MATERIAL_UNITS.get(mat_name, "Units"),
            "estimated_cost": cost_rounded,
        })
        
        total_cost += cost_rounded
        cost_breakdown[mat_name] = cost_rounded

    total_cost_rounded = round(total_cost, 2)

    # Calculate percentage distribution for charts
    for mat in materials_result:
        pct = (mat["estimated_cost"] / total_cost_rounded * 100) if total_cost_rounded > 0 else 0
        material_distribution[mat["material_name"]] = round(pct, 2)

    project_summary = {
        "project_type": req.project_type,
        "built_up_area": req.built_up_area,
        "area_unit": req.area_unit,
        "built_up_area_sqft": round(area_sqft, 2),
        "total_effective_area_sqft": round(total_effective_area, 2),
        "floors": req.floors,
        "material_quality": req.material_quality,
        "construction_type": req.construction_type,
        "location": req.location or "Not Specified",
    }

    return {
        "materials": materials_result,
        "total_estimated_cost": total_cost_rounded,
        "material_distribution": material_distribution,
        "cost_breakdown": cost_breakdown,
        "project_summary": project_summary,
    }


def generate_estimation_pdf(data: Dict[str, Any]) -> bytes:
    """Generate a clean PDF report document for the Material Estimation."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#FF8C00"),
        alignment=0,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubTitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
    )
    section_style = ParagraphStyle(
        "ReportSection",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1F2937"),
        spaceBefore=12,
        spaceAfter=6,
    )
    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1F2937"),
    )

    story = []

    # Header Title
    story.append(Paragraph("🏗️ Construction Intelligent Hub", title_style))
    story.append(Paragraph("Material Estimation & Quantity Takeoff Report", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#FF8C00"), spaceBefore=5, spaceAfter=15))

    # Project Summary Table
    summary = data.get("project_summary", {})
    summary_table_data = [
        [
            Paragraph("<b>Project Type:</b> " + str(summary.get("project_type")), normal_style),
            Paragraph("<b>Built-up Area:</b> " + f"{summary.get('built_up_area')} ({summary.get('area_unit')})", normal_style),
        ],
        [
            Paragraph("<b>Number of Floors:</b> " + str(summary.get("floors")), normal_style),
            Paragraph("<b>Material Quality:</b> " + str(summary.get("material_quality")), normal_style),
        ],
        [
            Paragraph("<b>Construction Type:</b> " + str(summary.get("construction_type")), normal_style),
            Paragraph("<b>Location:</b> " + str(summary.get("location")), normal_style),
        ],
    ]
    t_summary = Table(summary_table_data, colWidths=[270, 270])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15))

    # Materials Table
    story.append(Paragraph("Itemized Material Quantity & Cost Estimates", section_style))
    materials = data.get("materials", [])
    
    mat_table_data = [["Material Name", "Estimated Quantity", "Unit", "Estimated Cost ($)"]]
    for m in materials:
        mat_table_data.append([
            m["material_name"],
            f"{m['estimated_quantity']:,}",
            m["unit"],
            f"${m['estimated_cost']:,.2f}",
        ])
    
    # Add Total row
    total_cost = data.get("total_estimated_cost", 0.0)
    mat_table_data.append(["TOTAL ESTIMATED COST", "", "", f"${total_cost:,.2f}"])

    t_mat = Table(mat_table_data, colWidths=[160, 130, 100, 150])
    t_mat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FF8C00")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#FFF7ED")),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor("#9A3412")),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_mat)
    story.append(Spacer(1, 20))

    # Footer note
    footer_text = Paragraph("<i>Generated automatically by Construction Intelligent Hub • Confidential Estimation Report</i>", subtitle_style)
    story.append(footer_text)

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


def generate_estimation_csv(data: Dict[str, Any]) -> str:
    """Generate a clean CSV string for the Material Estimation report."""
    output = io.StringIO()
    writer = csv.writer(output)

    summary = data.get("project_summary", {})
    writer.writerow(["CONSTRUCTION INTELLIGENT HUB - MATERIAL ESTIMATION REPORT"])
    writer.writerow([])
    writer.writerow(["PROJECT SUMMARY"])
    writer.writerow(["Project Type", summary.get("project_type")])
    writer.writerow(["Built-up Area", f"{summary.get('built_up_area')} {summary.get('area_unit')}"])
    writer.writerow(["Number of Floors", summary.get("floors")])
    writer.writerow(["Material Quality", summary.get("material_quality")])
    writer.writerow(["Construction Type", summary.get("construction_type")])
    writer.writerow(["Location", summary.get("location")])
    writer.writerow([])

    writer.writerow(["ITEMIZED MATERIAL ESTIMATION"])
    writer.writerow(["Material Name", "Estimated Quantity", "Unit", "Estimated Cost ($)"])

    materials = data.get("materials", [])
    for m in materials:
        writer.writerow([
            m["material_name"],
            m["estimated_quantity"],
            m["unit"],
            f"{m['estimated_cost']:.2f}",
        ])

    writer.writerow([])
    writer.writerow(["TOTAL ESTIMATED COST ($)", f"{data.get('total_estimated_cost', 0.0):.2f}"])

    return output.getvalue()
