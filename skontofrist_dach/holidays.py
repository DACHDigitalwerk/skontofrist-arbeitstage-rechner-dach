# -*- coding: utf-8 -*-
"""
Holiday calculation engine for Germany, Austria, and Switzerland (2026+),
including regional state/canton holidays and SEPA Target2 bank holidays.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Set
from .models import Country, Holiday


def compute_easter_sunday(year: int) -> date:
    """
    Computes Easter Sunday using the anonymous Gregorian algorithm (Meeus/Jones/Butcher).
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_target2_bank_holidays(year: int) -> Set[date]:
    """
    SEPA Target2 closed bank holidays (in addition to Saturdays and Sundays).
    """
    easter = compute_easter_sunday(year)
    return {
        date(year, 1, 1),            # Neujahr
        easter - timedelta(days=2),   # Karfreitag
        easter + timedelta(days=1),   # Ostermontag
        date(year, 5, 1),            # Tag der Arbeit
        date(year, 12, 25),          # 1. Weihnachtstag
        date(year, 12, 26),          # 2. Weihnachtstag
    }


def get_holidays_for_year(year: int, country: Country, state_or_canton: str = "") -> Dict[date, str]:
    """
    Returns a dict mapping date -> holiday name for a given country and state/canton.
    """
    st = state_or_canton.upper().strip()
    easter = compute_easter_sunday(year)
    holidays: Dict[date, str] = {}

    def add(d: date, name: str):
        if d not in holidays:
            holidays[d] = name

    # Common across all three: Neujahr, 1. & 2. Weihnachtstag
    add(date(year, 1, 1), "Neujahr")
    add(date(year, 12, 25), "1. Weihnachtstag")
    add(date(year, 12, 26), "2. Weihnachtstag / Stephanstag")

    if country == Country.DE:
        # Nationwide
        add(easter - timedelta(days=2), "Karfreitag")
        add(easter + timedelta(days=1), "Ostermontag")
        add(date(year, 5, 1), "Tag der Arbeit")
        add(easter + timedelta(days=39), "Christi Himmelfahrt")
        add(easter + timedelta(days=50), "Pfingstmontag")
        add(date(year, 10, 3), "Tag der Deutschen Einheit")

        # Regional
        # Heilige Drei Könige: BW, BY, ST
        if st in ("BW", "BY", "ST", "ALL"):
            add(date(year, 1, 6), "Heilige Drei Könige")
        # Internationaler Frauentag: BE, MV
        if st in ("BE", "MV", "ALL"):
            add(date(year, 3, 8), "Internationaler Frauentag")
        # Fronleichnam: BW, BY, HE, NW, RP, SL (and parts of SN, TH)
        if st in ("BW", "BY", "HE", "NW", "RP", "SL", "ALL"):
            add(easter + timedelta(days=60), "Fronleichnam")
        # Mariä Himmelfahrt: SL, BY (partially)
        if st in ("SL", "BY", "ALL"):
            add(date(year, 8, 15), "Mariä Himmelfahrt")
        # Weltkindertag: TH
        if st in ("TH", "ALL"):
            add(date(year, 9, 20), "Weltkindertag")
        # Reformationstag: BB, HB, HH, MV, NI, SN, ST, SH, TH
        if st in ("BB", "HB", "HH", "MV", "NI", "SN", "ST", "SH", "TH", "ALL"):
            add(date(year, 10, 31), "Reformationstag")
        # Allerheiligen: BW, BY, NW, RP, SL
        if st in ("BW", "BY", "NW", "RP", "SL", "ALL"):
            add(date(year, 11, 1), "Allerheiligen")
        # Buß- und Bettag: SN
        if st in ("SN", "ALL"):
            # Wednesday before Nov 23
            nov23 = date(year, 11, 23)
            # Find previous Wednesday (weekday() == 2)
            offset = (nov23.weekday() - 2) % 7
            if offset == 0:
                offset = 7
            busstag = nov23 - timedelta(days=offset)
            add(busstag, "Buß- und Bettag")

    elif country == Country.AT:
        # Nationwide
        add(date(year, 1, 6), "Heilige Drei Könige")
        add(easter + timedelta(days=1), "Ostermontag")
        add(date(year, 5, 1), "Staatsfeiertag")
        add(easter + timedelta(days=39), "Christi Himmelfahrt")
        add(easter + timedelta(days=50), "Pfingstmontag")
        add(easter + timedelta(days=60), "Fronleichnam")
        add(date(year, 8, 15), "Mariä Himmelfahrt")
        add(date(year, 10, 26), "Nationalfeiertag")
        add(date(year, 11, 1), "Allerheiligen")
        add(date(year, 12, 8), "Mariä Empfängnis")

    elif country == Country.CH:
        # Nationwide
        add(date(year, 8, 1), "Bundesfeiertag")
        add(easter + timedelta(days=39), "Auffahrt")

        # Karfreitag: almost all cantons except VS, TI partially
        if st not in ("VS",):
            add(easter - timedelta(days=2), "Karfreitag")
        # Ostermontag
        if st not in ("VS",):
            add(easter + timedelta(days=1), "Ostermontag")
        # Pfingstmontag
        if st not in ("VS",):
            add(easter + timedelta(days=50), "Pfingstmontag")
        # Tag der Arbeit (01.05): ZH, BS, BL, SH, TG, TI, JU, NE, SO
        if st in ("ZH", "BS", "BL", "SH", "TG", "TI", "JU", "NE", "SO", "ALL"):
            add(date(year, 5, 1), "Tag der Arbeit")
        # Fronleichnam: LU, UR, SZ, OW, NW, ZG, FR, SO, AI, TI, VS, JU
        if st in ("LU", "UR", "SZ", "OW", "NW", "ZG", "FR", "SO", "AI", "TI", "VS", "JU", "ALL"):
            add(easter + timedelta(days=60), "Fronleichnam")
        # Allerheiligen: LU, UR, SZ, OW, NW, GL, ZG, FR, SO, AI, SG, TI, VS, JU
        if st in ("LU", "UR", "SZ", "OW", "NW", "GL", "ZG", "FR", "SO", "AI", "SG", "TI", "VS", "JU", "ALL"):
            add(date(year, 11, 1), "Allerheiligen")

    return holidays


def is_statutory_holiday(d: date, country: Country, state_or_canton: str = "") -> Optional[str]:
    """
    Checks if a given date is a statutory holiday in the specified country/state.
    Returns the holiday name if true, None otherwise.
    """
    holidays = get_holidays_for_year(d.year, country, state_or_canton)
    return holidays.get(d)


def is_bank_working_day(d: date) -> bool:
    """
    Checks if a day is a SEPA Target2 banking working day.
    Saturdays, Sundays and Target2 bank holidays are not banking days.
    """
    if d.weekday() >= 5:  # Saturday or Sunday
        return False
    target2 = get_target2_bank_holidays(d.year)
    return d not in target2
