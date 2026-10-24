# -*- coding: utf-8 -*-
"""
Command-line interface for the DACH Skontofrist- & Arbeitstage-Rechner 2026 (dach-skontofrist).
"""

import argparse
from datetime import date, datetime
import json
import os
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from skontofrist_dach.models import Country, SkontoDiscountTier
from skontofrist_dach.calculator import calculate_skonto_plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dach-skontofrist",
        description="DACH Skontofrist-, Zahlungsziel- & Bankarbeitstage-Rechner 2026 (§ 193 BGB / § 903 ABGB / Art. 78 OR)",
    )
    parser.add_argument(
        "--date",
        "-d",
        type=str,
        default=date.today().strftime("%Y-%m-%d"),
        help="Rechnungsdatum (YYYY-MM-DD, Standard: heute)",
    )
    parser.add_argument(
        "--amount",
        "-a",
        type=float,
        default=10000.0,
        help="Rechnungsbetrag brutto in EUR / CHF (Standard: 10.000)",
    )
    parser.add_argument(
        "--net-days",
        "-n",
        type=int,
        default=30,
        help="Zahlungsziel netto in Tagen (Standard: 30)",
    )
    parser.add_argument(
        "--skonto-days",
        "-s",
        type=int,
        default=14,
        help="Skontofrist 1 in Tagen (Standard: 14)",
    )
    parser.add_argument(
        "--skonto-pct",
        "-p",
        type=float,
        default=3.0,
        help="Skontosatz 1 in Prozent (Standard: 3.0%%)",
    )
    parser.add_argument(
        "--skonto2-days",
        type=int,
        default=0,
        help="Optionale 2. Skontofrist in Tagen (z.B. 7)",
    )
    parser.add_argument(
        "--skonto2-pct",
        type=float,
        default=0.0,
        help="Optionale 2. Skontostufe in Prozent (z.B. 2.0%%)",
    )
    parser.add_argument(
        "--country",
        "-c",
        type=str,
        choices=["DE", "AT", "CH"],
        default="DE",
        help="Länderregime (DE: § 193 BGB, AT: § 903 ABGB, CH: Art. 78 OR)",
    )
    parser.add_argument(
        "--state",
        type=str,
        default="",
        help="Bundesland / Kanton (z.B. BY, NW, BW, W, ZH, BE)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ausgabe im strukturierten JSON-Format",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        inv_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        print(f"Fehler: Ungültiges Datumsformat '{args.date}'. Bitte YYYY-MM-DD verwenden.")
        return 1

    tiers = [SkontoDiscountTier(days=args.skonto_days, discount_pct=args.skonto_pct)]
    if args.skonto2_days > 0 and args.skonto2_pct > 0:
        tiers.append(SkontoDiscountTier(days=args.skonto2_days, discount_pct=args.skonto2_pct))

    country_enum = Country(args.country.upper())
    result = calculate_skonto_plan(
        invoice_date=inv_date,
        invoice_amount=args.amount,
        net_days=args.net_days,
        discount_tiers=tiers,
        country=country_enum,
        state_or_canton=args.state,
    )

    if args.json:
        out = {
            "invoice_date": result.invoice_date.strftime("%Y-%m-%d"),
            "invoice_amount": result.invoice_amount,
            "country": result.country.value,
            "state_or_canton": result.state_or_canton,
            "net_deadline": {
                "nominal_date": result.net_deadline.nominal_date.strftime("%Y-%m-%d"),
                "final_date": result.net_deadline.final_date.strftime("%Y-%m-%d"),
                "is_shifted": result.net_deadline.is_shifted,
                "shift_days": result.net_deadline.shift_days,
                "shift_reason": result.net_deadline.shift_reason,
                "latest_bank_transfer_date": result.net_deadline.latest_bank_transfer_date.strftime("%Y-%m-%d"),
            },
            "skonto_tiers": [
                {
                    "days": t.tier.days,
                    "discount_pct": t.tier.discount_pct,
                    "nominal_date": t.deadline.nominal_date.strftime("%Y-%m-%d"),
                    "final_date": t.deadline.final_date.strftime("%Y-%m-%d"),
                    "is_shifted": t.deadline.is_shifted,
                    "shift_days": t.deadline.shift_days,
                    "shift_reason": t.deadline.shift_reason,
                    "discount_amount": t.discount_amount,
                    "payable_amount": t.payable_amount,
                    "effective_annual_interest_pct": t.effective_annual_interest_pct,
                    "latest_bank_transfer_date": t.deadline.latest_bank_transfer_date.strftime("%Y-%m-%d"),
                }
                for t in result.skonto_tiers
            ],
            "max_savings": result.max_savings,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    law_name = {
        Country.DE: "§ 193 BGB (Fristverschiebung Samstag/Sonntag/Feiertag)",
        Country.AT: "§ 903 ABGB & Feiertagsgesetz",
        Country.CH: "Art. 78 OR (Erfüllung am nächsten Werktag)",
    }[result.country]

    print("=" * 75)
    print(f" DACH SKONTOFRIST- & ZAHLUNGSZIEL-ANALYSE 2026")
    print("=" * 75)
    print(f" Rechnungsdatum:    {result.invoice_date.strftime('%d.%m.%Y')}")
    print(f" Rechnungsbetrag:   {result.invoice_amount:>10.2f} € / CHF")
    print(f" Rechtsregime:      {result.country.value} ({result.state_or_canton}) -> {law_name}")
    print("-" * 75)

    print("\n1. NETTO-ZAHLUNGSZIEL:")
    nd = result.net_deadline
    print(f"  * Kalendarischer Stichtag (+{args.net_days} Tage): {nd.nominal_date.strftime('%d.%m.%Y')} ({nd.nominal_date.strftime('%A')})")
    print(f"  * Rechtswirksame Fälligkeit:        {nd.final_date.strftime('%d.%m.%Y')} ({nd.final_date.strftime('%A')})")
    if nd.is_shifted:
        print(f"    --> {nd.shift_reason}")
    print(f"  * Spätester Bank-Überweisungstermin: {nd.latest_bank_transfer_date.strftime('%d.%m.%Y')}")

    print("\n2. SKONTO-FRISTEN & ZINSVORTEIL:")
    for i, t in enumerate(result.skonto_tiers, start=1):
        dl = t.deadline
        print(f"  --- Skontostufe {i}: {t.tier.discount_pct:.1f} % innerhalb von {t.tier.days} Tagen ---")
        print(f"  * Kalendarischer Stichtag (+{t.tier.days} Tage): {dl.nominal_date.strftime('%d.%m.%Y')} ({dl.nominal_date.strftime('%A')})")
        print(f"  * Rechtswirksamer Skontostichtag:   {dl.final_date.strftime('%d.%m.%Y')} ({dl.final_date.strftime('%A')})")
        if dl.is_shifted:
            print(f"    --> {dl.shift_reason}")
        print(f"  * Spätester Überweisungstermin:     {dl.latest_bank_transfer_date.strftime('%d.%m.%Y')}")
        print(f"  * Skonto-Ersparnis:                 {t.discount_amount:>8.2f} € / CHF")
        print(f"  * Zu zahlender Überweisungsbetrag:  {t.payable_amount:>8.2f} € / CHF")
        print(f"  * Effektiver Jahreszins:            {t.effective_annual_interest_pct:>8.2f} % p.a.")

    print("=" * 75)
    print(f" MAXIMALER LIQUIDITÄTSVORTEIL: {result.max_savings:.2f} € / CHF")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    sys.exit(main())
