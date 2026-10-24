# -*- coding: utf-8 -*-
"""
Data models for payment terms, holidays, bank working days, and cash discount (Skonto) calculation.
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional, Dict


class Country(str, Enum):
    DE = "DE"
    AT = "AT"
    CH = "CH"


@dataclass
class Holiday:
    date_val: date
    name: str
    country: Country
    is_nationwide: bool = True
    states_or_cantons: List[str] = field(default_factory=list)


@dataclass
class SkontoDiscountTier:
    days: int
    discount_pct: float  # e.g. 3.0 for 3%


@dataclass
class DeadlineDetail:
    nominal_date: date
    final_date: date
    is_shifted: bool
    shift_days: int
    shift_reason: str
    is_weekend: bool
    holiday_name: Optional[str]
    latest_bank_transfer_date: date
    transfer_notes: str


@dataclass
class SkontoTierResult:
    tier: SkontoDiscountTier
    deadline: DeadlineDetail
    discount_amount: float
    payable_amount: float
    effective_annual_interest_pct: float  # Effektivzins


@dataclass
class CalculationResult:
    invoice_date: date
    invoice_amount: float
    country: Country
    state_or_canton: str
    net_deadline: DeadlineDetail
    skonto_tiers: List[SkontoTierResult]
    max_savings: float
