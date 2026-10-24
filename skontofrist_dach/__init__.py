# -*- coding: utf-8 -*-
"""
skontofrist_dach: DACH Skontofrist-, Zahlungsziel- & Bankarbeitstage-Rechner 2026.
§ 193 BGB, § 903 ABGB, Art. 78 OR Samstags- und Feiertagsverschiebungen.
"""

from .models import (
    Country,
    Holiday,
    SkontoDiscountTier,
    DeadlineDetail,
    SkontoTierResult,
    CalculationResult,
)
from .holidays import (
    compute_easter_sunday,
    get_holidays_for_year,
    is_statutory_holiday,
    is_bank_working_day,
    get_target2_bank_holidays,
)
from .calculator import (
    calculate_deadline,
    calculate_effective_interest_rate,
    calculate_skonto_plan,
)

__version__ = "1.0.0"
__all__ = [
    "Country",
    "Holiday",
    "SkontoDiscountTier",
    "DeadlineDetail",
    "SkontoTierResult",
    "CalculationResult",
    "compute_easter_sunday",
    "get_holidays_for_year",
    "is_statutory_holiday",
    "is_bank_working_day",
    "get_target2_bank_holidays",
    "calculate_deadline",
    "calculate_effective_interest_rate",
    "calculate_skonto_plan",
    "__version__",
]
