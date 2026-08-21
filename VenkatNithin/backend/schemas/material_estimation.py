"""
backend/schemas/material_estimation.py
---------------------------------------
Pydantic validation schemas for material estimation requests and responses.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class MaterialEstimationRequest(BaseModel):
    project_type: str = Field(..., description="Type of project: Residential, Commercial, Industrial")
    built_up_area: float = Field(..., description="Built-up area value (> 0)")
    area_unit: str = Field("sq_ft", description="Area unit: sq_ft or sq_m")
    floors: int = Field(1, description="Number of floors (>= 1)")
    material_quality: str = Field("Standard", description="Material quality: Standard, Premium, Luxury")
    construction_type: str = Field("RCC", description="Construction type: RCC, Steel Structure, Hybrid")
    location: Optional[str] = Field(None, description="Project location (Optional)")

    @field_validator("built_up_area")
    @classmethod
    def validate_built_up_area(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Built-up area must be a positive number greater than 0.")
        return v

    @field_validator("floors")
    @classmethod
    def validate_floors(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Number of floors must be at least 1.")
        return v

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, v: str) -> str:
        valid_types = ["Residential", "Commercial", "Industrial"]
        matched = [t for t in valid_types if t.lower() == v.lower()]
        if not matched:
            raise ValueError(f"Invalid project type '{v}'. Allowed types: {', '.join(valid_types)}")
        return matched[0]

    @field_validator("material_quality")
    @classmethod
    def validate_material_quality(cls, v: str) -> str:
        valid_qualities = ["Standard", "Premium", "Luxury"]
        matched = [q for q in valid_qualities if q.lower() == v.lower()]
        if not matched:
            raise ValueError(f"Invalid material quality '{v}'. Allowed options: {', '.join(valid_qualities)}")
        return matched[0]

    @field_validator("construction_type")
    @classmethod
    def validate_construction_type(cls, v: str) -> str:
        valid_const = ["RCC", "Steel Structure", "Hybrid"]
        matched = [c for c in valid_const if c.lower() == v.lower()]
        if not matched:
            raise ValueError(f"Invalid construction type '{v}'. Allowed options: {', '.join(valid_const)}")
        return matched[0]


class MaterialItem(BaseModel):
    material_name: str
    estimated_quantity: float
    unit: str
    estimated_cost: float


class MaterialEstimationResponse(BaseModel):
    materials: List[MaterialItem]
    total_estimated_cost: float
    material_distribution: Dict[str, float]
    cost_breakdown: Dict[str, float]
    project_summary: Dict[str, Any]
