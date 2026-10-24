# -*- coding: utf-8 -*-
"""
Calculation engine for statutory deadline shifting (§ 193 BGB, § 903 ABGB, Art. 78 OR),
SEPA banking transfer deadlines, and cash discount (Skonto) financial optimization.
"""

from datetime import date, timedelta
from typing import List, Optional, Tuple
from .models import (
    Country,
    DeadlineDetail,
    SkontoDiscountTier,
    SkontoTierResult,
    CalculationResult,
)
from .holidays import is_statutory_holiday, is_bank_working_day


def calculate_effective_interest_rate(
    discount_pct: float,
    net_days: int,
    discount_days: int,
) -> float:
    """
    Calculates the annual effective interest rate (Effektiver Jahreszins) of taking a cash discount:
    Effektivzins = (Skontosatz / (100 - Skontosatz)) * (360 / (Nettoziel - Skontoziel)) * 100
    """
    days_gained = net_days - discount_days
    if days_gained <= 0 or discount_pct <= 0 or discount_pct >= 100:
        return 0.0

    rate = (discount_pct / (100.0 - discount_pct)) * (360.0 / float(days_gained)) * 100.0
    return round(rate, 2)


def calculate_deadline(
    start_date: date,
    days: int,
    country: Country = Country.DE,
    state_or_canton: str = "",
) -> DeadlineDetail:
    """
    Calculates the exact statutory payment deadline:
    1. Computes nominal deadline: start_date + days
    2. Checks if nominal deadline falls on a Saturday, Sunday, or statutory holiday.
    3. If so, shifts according to § 193 BGB / § 903 ABGB / Art. 78 OR to the NEXT working day.
    4. Computes latest bank transfer date to ensure timely receipt.
    """
    nominal_date = start_date + timedelta(days=days)
    curr = nominal_date

    is_initial_weekend = curr.weekday() >= 5
    initial_holiday = is_statutory_holiday(curr, country, state_or_canton)

    shifted = False
    shift_reasons = []

    if is_initial_weekend or initial_holiday:
        shifted = True

    while True:
        holiday_name = is_statutory_holiday(curr, country, state_or_canton)
        weekday = curr.weekday()

        if weekday == 5:
            shift_reasons.append(f"{curr.strftime('%d.%m.%Y')}: Samstag")
            curr += timedelta(days=1)
        elif weekday == 6:
            shift_reasons.append(f"{curr.strftime('%d.%m.%Y')}: Sonntag")
            curr += timedelta(days=1)
        elif holiday_name:
            shift_reasons.append(f"{curr.strftime('%d.%m.%Y')}: Feiertag ({holiday_name})")
            curr += timedelta(days=1)
        else:
            # Found next valid working day
            break

    final_date = curr
    shift_days = (final_date - nominal_date).days

    # Determine latest bank transfer date
    # BGH Rechtsprechung (u. a. BGH X ZR 113/97, VIII ZR 222/19):
    # Bei Überweisungsträgern/SEPA ist die rechtzeitige Erteilung des Überweisungsauftrags am Fälligkeitstag
    # bei hinreichender Kontodeckung maßgebend, wenn die Bank am selben Tag die Weiterleitung bewirkt.
    # Da ein Bankarbeitstag nötig sein kann, ist der sicherste Überweisungstag der letzte Bankarbeitstag auf oder vor final_date.
    t_date = final_date
    while not is_bank_working_day(t_date):
        t_date -= timedelta(days=1)

    latest_bank_transfer = t_date

    if shifted:
        reason_summary = f"Frist verlängert um {shift_days} Tag(e) gem. Gesetz (" + "; ".join(shift_reasons[:2]) + ")"
    else:
        reason_summary = "Fällt auf regulären Werktag (keine Verschiebung erforderlich)"

    transfer_notes = (
        f"SEPA-Überweisung spätestens am {latest_bank_transfer.strftime('%d.%m.%Y')} "
        f"vor Bank-Cut-off (ca. 14:00 Uhr) einreichen."
    )

    return DeadlineDetail(
        nominal_date=nominal_date,
        final_date=final_date,
        is_shifted=shifted,
        shift_days=shift_days,
        shift_reason=reason_summary,
        is_weekend=is_initial_weekend,
        holiday_name=initial_holiday,
        latest_bank_transfer_date=latest_bank_transfer,
        transfer_notes=transfer_notes,
    )


def calculate_skonto_plan(
    invoice_date: date,
    invoice_amount: float,
    net_days: int = 30,
    discount_tiers: Optional[List[SkontoDiscountTier]] = None,
    country: Country = Country.DE,
    state_or_canton: str = "",
) -> CalculationResult:
    """
    Computes a full payment term and cash discount plan with statutory deadline shifts.
    """
    if discount_tiers is None:
        discount_tiers = [
            SkontoDiscountTier(days=14, discount_pct=3.0),
            SkontoDiscountTier(days=7, discount_pct=2.0),
        ]

    # Calculate net deadline
    net_deadline = calculate_deadline(invoice_date, net_days, country, state_or_canton)

    tier_results: List[SkontoTierResult] = []
    max_savings = 0.0

    for tier in sorted(discount_tiers, key=lambda t: t.days, reverse=True):
        dl = calculate_deadline(invoice_date, tier.days, country, state_or_canton)
        discount_amount = round(invoice_amount * (tier.discount_pct / 100.0), 2)
        payable_amount = round(invoice_amount - discount_amount, 2)
        eff_interest = calculate_effective_interest_rate(tier.discount_pct, net_days, tier.days)

        if discount_amount > max_savings:
            max_savings = discount_amount

        tier_results.append(
            SkontoTierResult(
                tier=tier,
                deadline=dl,
                discount_amount=discount_amount,
                payable_amount=payable_amount,
                effective_annual_interest_pct=eff_interest,
            )
        )

    return CalculationResult(
        invoice_date=invoice_date,
        invoice_amount=round(invoice_amount, 2),
        country=country,
        state_or_canton=state_or_canton.upper() if state_or_canton else "STANDARD",
        net_deadline=net_deadline,
        skonto_tiers=tier_results,
        max_savings=round(max_savings, 2),
    )
