# -*- coding: utf-8 -*-
from datetime import date
import pytest

from skontofrist_dach.models import Country, SkontoDiscountTier
from skontofrist_dach.holidays import (
    compute_easter_sunday,
    get_holidays_for_year,
    is_statutory_holiday,
    is_bank_working_day,
)
from skontofrist_dach.calculator import (
    calculate_deadline,
    calculate_effective_interest_rate,
    calculate_skonto_plan,
)


def test_easter_sunday_calculation():
    # Known Easter dates:
    # 2025: April 20
    # 2026: April 5
    # 2027: March 28
    assert compute_easter_sunday(2025) == date(2025, 4, 20)
    assert compute_easter_sunday(2026) == date(2026, 4, 5)
    assert compute_easter_sunday(2027) == date(2027, 3, 28)


def test_holidays_2026_germany():
    # Easter 2026 is April 5
    # Karfreitag = April 3
    # Ostermontag = April 6
    # Christi Himmelfahrt = May 14
    # Pfingstmontag = May 25
    assert is_statutory_holiday(date(2026, 1, 1), Country.DE) == "Neujahr"
    assert is_statutory_holiday(date(2026, 4, 3), Country.DE) == "Karfreitag"
    assert is_statutory_holiday(date(2026, 4, 6), Country.DE) == "Ostermontag"
    assert is_statutory_holiday(date(2026, 5, 1), Country.DE) == "Tag der Arbeit"
    assert is_statutory_holiday(date(2026, 5, 14), Country.DE) == "Christi Himmelfahrt"
    assert is_statutory_holiday(date(2026, 5, 25), Country.DE) == "Pfingstmontag"
    assert is_statutory_holiday(date(2026, 10, 3), Country.DE) == "Tag der Deutschen Einheit"


def test_regional_holidays_germany():
    # Fronleichnam 2026: Easter (April 5) + 60 days = June 4, 2026 (Thursday)
    fronleichnam = date(2026, 6, 4)
    assert is_statutory_holiday(fronleichnam, Country.DE, "BY") == "Fronleichnam"
    assert is_statutory_holiday(fronleichnam, Country.DE, "NW") == "Fronleichnam"
    assert is_statutory_holiday(fronleichnam, Country.DE, "HH") is None  # Not a holiday in Hamburg

    # Reformationstag: Oct 31 in NI, HH, HB
    refo = date(2026, 10, 31)
    assert is_statutory_holiday(refo, Country.DE, "NI") == "Reformationstag"
    assert is_statutory_holiday(refo, Country.DE, "BY") is None  # Not a holiday in Bavaria

    # Allerheiligen: Nov 1 in BY, NW, BW
    aller = date(2026, 11, 1)
    assert is_statutory_holiday(aller, Country.DE, "BY") == "Allerheiligen"


def test_holidays_austria_and_switzerland():
    # Austria National Day: Oct 26
    assert is_statutory_holiday(date(2026, 10, 26), Country.AT) == "Nationalfeiertag"
    # Austria Mariä Empfängnis: Dec 8
    assert is_statutory_holiday(date(2026, 12, 8), Country.AT) == "Mariä Empfängnis"

    # Swiss National Day: Aug 1
    assert is_statutory_holiday(date(2026, 8, 1), Country.CH) == "Bundesfeiertag"
    # Tag der Arbeit in Zurich
    assert is_statutory_holiday(date(2026, 5, 1), Country.CH, "ZH") == "Tag der Arbeit"


def test_deadline_no_shift():
    # Wednesday to Friday (2 days)
    # 2026-06-10 (Wednesday) + 2 days = 2026-06-12 (Friday)
    res = calculate_deadline(date(2026, 6, 10), 2, Country.DE)
    assert res.nominal_date == date(2026, 6, 12)
    assert res.final_date == date(2026, 6, 12)
    assert not res.is_shifted
    assert res.shift_days == 0


def test_deadline_saturday_shift():
    # 2026-06-11 (Thursday) + 2 days = 2026-06-13 (Saturday)
    # Next working day: 2026-06-15 (Monday)
    res = calculate_deadline(date(2026, 6, 11), 2, Country.DE)
    assert res.nominal_date == date(2026, 6, 13)
    assert res.final_date == date(2026, 6, 15)
    assert res.is_shifted
    assert res.shift_days == 2


def test_deadline_sunday_shift():
    # 2026-06-10 (Wednesday) + 4 days = 2026-06-14 (Sunday)
    # Next working day: 2026-06-15 (Monday)
    res = calculate_deadline(date(2026, 6, 10), 4, Country.DE)
    assert res.nominal_date == date(2026, 6, 14)
    assert res.final_date == date(2026, 6, 15)
    assert res.is_shifted
    assert res.shift_days == 1


def test_deadline_easter_cluster_shift():
    # Nominal date falls on Karfreitag 2026-04-03
    # Friday 03.04 (Karfreitag) -> Sat 04.04 -> Sun 05.04 -> Mon 06.04 (Ostermontag) -> Tue 07.04!
    # Shift of 4 days!
    res = calculate_deadline(date(2026, 4, 1), 2, Country.DE)
    assert res.nominal_date == date(2026, 4, 3)
    assert res.final_date == date(2026, 4, 7)  # Tuesday after Easter
    assert res.is_shifted
    assert res.shift_days == 4


def test_bank_working_days():
    # Saturday 2026-04-04 is not a bank day
    assert not is_bank_working_day(date(2026, 4, 4))
    # Sunday 2026-04-05 is not a bank day
    assert not is_bank_working_day(date(2026, 4, 5))
    # Karfreitag 2026-04-03 is Target2 bank holiday
    assert not is_bank_working_day(date(2026, 4, 3))
    # Ostermontag 2026-04-06 is Target2 bank holiday
    assert not is_bank_working_day(date(2026, 4, 6))
    # Tuesday 2026-04-07 is regular bank working day
    assert is_bank_working_day(date(2026, 4, 7))


def test_effective_interest_rate_formula():
    # 3% cash discount, 14 days discount, 30 days net:
    # (3 / 97) * (360 / 16) * 100 = 0.0309278 * 22.5 * 100 = 69.59%
    rate = calculate_effective_interest_rate(3.0, 30, 14)
    assert rate == 69.59

    # 2% cash discount, 10 days discount, 30 days net:
    # (2 / 98) * (360 / 20) * 100 = 0.020408 * 18 * 100 = 36.73%
    rate2 = calculate_effective_interest_rate(2.0, 30, 10)
    assert rate2 == 36.73

    # Invalid range: net_days <= discount_days
    assert calculate_effective_interest_rate(3.0, 10, 10) == 0.0


def test_skonto_plan_comprehensive():
    inv_date = date(2026, 5, 15)
    amount = 10000.0
    tiers = [
        SkontoDiscountTier(days=14, discount_pct=3.0),
        SkontoDiscountTier(days=7, discount_pct=2.0),
    ]
    res = calculate_skonto_plan(
        invoice_date=inv_date,
        invoice_amount=amount,
        net_days=30,
        discount_tiers=tiers,
        country=Country.DE,
        state_or_canton="BY",
    )

    assert res.invoice_amount == 10000.0
    assert len(res.skonto_tiers) == 2
    # Tier 1 (14 days): 3% -> 300 € discount, 9700 € payable
    t1 = res.skonto_tiers[0]
    assert t1.tier.discount_pct == 3.0
    assert t1.discount_amount == 300.0
    assert t1.payable_amount == 9700.0
    assert t1.effective_annual_interest_pct == 69.59
    assert res.max_savings == 300.0
