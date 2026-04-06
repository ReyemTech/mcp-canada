"""Pydantic v2 models for the Health Canada Drug Product Database API."""

from pydantic import BaseModel
from typing import Optional


class DrugProduct(BaseModel):
    """A drug product from the Drug Product Database search results."""

    drug_code: Optional[int] = None
    """Internal drug_code — used for all detail lookups (NOT the DIN)."""

    brand_name: Optional[str] = None
    din: Optional[str] = None
    """DIN (Drug Identification Number) — NOT the same as drug_code."""

    company_name: Optional[str] = None
    descriptor: Optional[str] = None
    class_name: Optional[str] = None
    number_of_ais: Optional[int] = None
    ai_group_no: Optional[str] = None


class ActiveIngredient(BaseModel):
    """An active ingredient associated with a drug product."""

    ingredient_name: Optional[str] = None
    strength: Optional[str] = None
    strength_unit: Optional[str] = None
    dosage_value: Optional[str] = None
    dosage_unit: Optional[str] = None


class DrugRoute(BaseModel):
    """A route of administration for a drug product."""

    route_of_administration: Optional[str] = None


class DrugSchedule(BaseModel):
    """The schedule classification of a drug product."""

    schedule_name: Optional[str] = None


class TherapeuticClass(BaseModel):
    """ATC (Anatomical Therapeutic Chemical) classification for a drug product."""

    tc_atc_number: Optional[str] = None
    tc_atc: Optional[str] = None
    tc_ahfs_number: Optional[str] = None
    tc_ahfs: Optional[str] = None


class DrugStatus(BaseModel):
    """The market status of a drug product."""

    status: Optional[str] = None
    history_date: Optional[str] = None
    lot_number: Optional[str] = None
    expiration_date: Optional[str] = None


class Company(BaseModel):
    """A company associated with drug products."""

    company_code: Optional[int] = None
    company_name: Optional[str] = None
    company_type: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
