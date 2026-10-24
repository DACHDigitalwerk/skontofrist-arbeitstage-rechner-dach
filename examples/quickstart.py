# -*- coding: utf-8 -*-
"""
Quickstart Example: DACH Skontofrist- & Arbeitstage-Rechner 2026.
"""

from datetime import date
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from skontofrist_dach import (
    Country,
    SkontoDiscountTier,
    calculate_skonto_plan,
)


def main():
    print("=== Quickstart: DACH Skontofrist- & Zahlungsziel-Planer 2026 ===")

    # Scenario: Invoice of 12,500.00 EUR received on Friday, May 15, 2026 in Bavaria (BY)
    # Terms: 14 days 3% Skonto, 30 days net
    inv_date = date(2026, 5, 15)
    amount = 12500.00
    tiers = [
        SkontoDiscountTier(days=14, discount_pct=3.0),
        SkontoDiscountTier(days=7, discount_pct=2.0),
    ]

    plan = calculate_skonto_plan(
        invoice_date=inv_date,
        invoice_amount=amount,
        net_days=30,
        discount_tiers=tiers,
        country=Country.DE,
        state_or_canton="BY",
    )

    print(f"\nRechnung: {plan.invoice_amount:.2f} € vom {plan.invoice_date.strftime('%d.%m.%Y')}")
    print(f"Rechtsregime: {plan.country.value} ({plan.state_or_canton}) -> § 193 BGB")

    nd = plan.net_deadline
    print(f"\n1. Netto-Fälligkeit:")
    print(f"   * Kalendarisch (+30 Tage): {nd.nominal_date.strftime('%d.%m.%Y')} ({nd.nominal_date.strftime('%A')})")
    print(f"   * Rechtswirksam gem. § 193 BGB: {nd.final_date.strftime('%d.%m.%Y')} ({nd.final_date.strftime('%A')})")
    if nd.is_shifted:
        print(f"     Hinweis: {nd.shift_reason}")
    print(f"   * Spätester Bank-Überweisungstermin: {nd.latest_bank_transfer_date.strftime('%d.%m.%Y')}")

    print(f"\n2. Skonto-Stufen:")
    for i, t in enumerate(plan.skonto_tiers, start=1):
        dl = t.deadline
        print(f"   * Stufe {i} ({t.tier.discount_pct}% / {t.tier.days} Tage):")
        print(f"     - Fälligkeit:  {dl.final_date.strftime('%d.%m.%Y')} ({dl.final_date.strftime('%A')})")
        print(f"     - Ersparnis:   {t.discount_amount:.2f} € (Zahlbetrag: {t.payable_amount:.2f} €)")
        print(f"     - Effektivzins: {t.effective_annual_interest_pct:.2f} % p.a.")


if __name__ == "__main__":
    main()
