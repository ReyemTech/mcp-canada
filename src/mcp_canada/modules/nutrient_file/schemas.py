"""Pydantic v2 models for the Canadian Nutrient File module."""

from pydantic import BaseModel
from typing import Optional


class FoodItem(BaseModel):
    """A food item from the Canadian Nutrient File database."""

    food_id: Optional[int] = None
    food_description: Optional[str] = None
    food_group_id: Optional[int] = None
    food_group_name: Optional[str] = None


class NutrientAmount(BaseModel):
    """A nutrient amount for a specific food (per 100g)."""

    nutrient_name_id: Optional[int] = None
    nutrient_name: Optional[str] = None
    nutrient_value: Optional[float] = None
    nutrient_unit: Optional[str] = None
    nutrient_group: Optional[str] = None


class ServingSize(BaseModel):
    """A serving size measure for a food item."""

    measure_id: Optional[int] = None
    measure_name: Optional[str] = None
    conversion_factor_value: Optional[float] = None
    measure_description: Optional[str] = None


class NutrientName(BaseModel):
    """A nutrient name entry from the Canadian Nutrient File."""

    nutrient_name_id: Optional[int] = None
    nutrient_name: Optional[str] = None
    nutrient_unit: Optional[str] = None
    nutrient_group: Optional[str] = None


class FoodGroup(BaseModel):
    """A food group category from the Canadian Nutrient File."""

    food_group_id: Optional[int] = None
    food_group_name: Optional[str] = None
