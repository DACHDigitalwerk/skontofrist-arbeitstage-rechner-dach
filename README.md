# DACH Skontofrist-, Zahlungsziel- & Bankarbeitstage-Rechner 2026 ⏱️📅

[![CI](https://github.com/DACHDigitalwerk/skontofrist-arbeitstage-rechner-dach/actions/workflows/ci.yml/badge.svg)](https://github.com/DACHDigitalwerk/skontofrist-arbeitstage-rechner-dach/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Legal Compliance](https://img.shields.io/badge/BGB%20§%20193-OR%20Art.%2078-success.svg)](https://dachdigitalwerk.github.io/skontofrist-arbeitstage-rechner/)

> **Produktionsreife Berechnungs-Engine & CLI zur rechtswirksamen Fristenberechnung nach § 193 BGB (DE), § 903 ABGB (AT) und Art. 78 OR (CH). Berücksichtigt Wochenenden, regionale Feiertage aller Bundesländer & Kantone sowie SEPA Target2-Bankarbeitstage.**

Sparen Sie Liquidität und sichern Sie Skontoabzüge rechtssicher: Berechnen Sie den exakten juristischen Fälligkeitstag, die Verschiebung bei Sonn-, Samstags- und Feiertagen und den spätesten Einreichungstermin für SEPA-Überweisungen.

🌐 **Interaktives Web-Tool:** [https://dachdigitalwerk.github.io/skontofrist-arbeitstage-rechner/](https://dachdigitalwerk.github.io/skontofrist-arbeitstage-rechner/)

---

## 🎯 Kernfunktionen

- **Gesetzliche Fristverschiebung (§ 193 BGB, § 903 ABGB, Art. 78 OR):**
  Fällt das rechnerische Fristende auf einen Samstag, Sonntag oder staatlich anerkannten allgemeinen Feiertag, verlängert sich die Zahlungs- bzw. Skontofrist automatisch auf den **nächsten Werktag**.
- **Vollständiger Feiertagskalender 2026+:**
  Astronomische Osterformel (Meeus/Jones/Butcher) für bewegliche Feiertage (Karfreitag, Ostermontag, Himmelfahrt, Pfingsten, Fronleichnam) plus regionale Feiertage aller 16 deutschen Bundesländer, 9 österreichischen Bundesländer und 26 Schweizer Kantone.
- **SEPA Target2 Bankarbeitstage & Überweisungstermin:**
  Ermittlung des spätesten Bank-Überweisungstermins unter Berücksichtigung von Bankfeiertagen (Neujahr, Karfreitag, Ostermontag, 1. Mai, 25./26. Dezember) und SEPA-Laufzeiten gem. § 675t BGB.
- **Effektiver Jahreszins & Skontovorteil:**
  Berechnung des Liquiditätsgewinns und des effektiven Jahreszinses (häufig über 30–70 % p.a.) bei Skontoinanspruchnahme gegenüber dem vollen Nettoziel.
- **CLI & JSON-Export:**
  Konsolenbefehl `dach-skontofrist` mit flexiblen Argumenten und JSON-Ausgabe für ERP- und FiBu-Integration.

---

## 📦 Installation

```bash
git clone https://github.com/DACHDigitalwerk/skontofrist-arbeitstage-rechner-dach.git
cd skontofrist-arbeitstage-rechner-dach
pip install -e .
```

---

## 🚀 CLI-Nutzung

Nach der Installation steht der Konsolenbefehl `dach-skontofrist` zur Verfügung:

### 1. Standard-Rechnungsprüfung (5.000 € mit 3 % Skonto in Bayern)
```bash
dach-skontofrist --date 2026-05-15 --amount 5000 --net-days 30 --skonto-days 14 --skonto-pct 3.0 --country DE --state BY
```

**Ausgabe:**
```text
===========================================================================
 DACH SKONTOFRIST- & ZAHLUNGSZIEL-ANALYSE 2026
===========================================================================
 Rechnungsdatum:    15.05.2026
 Rechnungsbetrag:      5000.00 € / CHF
 Rechtsregime:      DE (BY) -> § 193 BGB (Fristverschiebung Samstag/Sonntag/Feiertag)
---------------------------------------------------------------------------

1. NETTO-ZAHLUNGSZIEL:
  * Kalendarischer Stichtag (+30 Tage): 14.06.2026 (Sunday)
  * Rechtswirksame Fälligkeit:        15.06.2026 (Monday)
    --> Frist verlängert um 1 Tag(e) gem. Gesetz (14.06.2026: Sonntag)
  * Spätester Bank-Überweisungstermin: 15.06.2026

2. SKONTO-FRISTEN & ZINSVORTEIL:
  --- Skontostufe 1: 3.0 % innerhalb von 14 Tagen ---
  * Kalendarischer Stichtag (+14 Tage): 29.05.2026 (Friday)
  * Rechtswirksamer Skontostichtag:   29.05.2026 (Friday)
  * Spätester Überweisungstermin:     29.05.2026
  * Skonto-Ersparnis:                   150.00 € / CHF
  * Zu zahlender Überweisungsbetrag:   4850.00 € / CHF
  * Effektiver Jahreszins:               69.59 % p.a.
===========================================================================
 MAXIMALER LIQUIDITÄTSVORTEIL: 150.00 € / CHF
===========================================================================
```

### 2. JSON-Export für ERP-Systeme (SAP, DATEV, Lexoffice)
```bash
dach-skontofrist --date 2026-06-01 --amount 12500 --json
```

---

## 💻 Python API Quickstart

```python
from datetime import date
from skontofrist_dach import (
    Country,
    SkontoDiscountTier,
    calculate_skonto_plan,
)

plan = calculate_skonto_plan(
    invoice_date=date(2026, 5, 15),
    invoice_amount=10000.0,
    net_days=30,
    discount_tiers=[
        SkontoDiscountTier(days=14, discount_pct=3.0),
    ],
    country=Country.DE,
    state_or_canton="BY",
)

# Netto-Fälligkeit
print(f"Rechtswirksam fällig am: {plan.net_deadline.final_date}")
print(f"Verschoben? {plan.net_deadline.is_shifted} ({plan.net_deadline.shift_reason})")

# Skonto-Ersparnis
t1 = plan.skonto_tiers[0]
print(f"Skonto-Stichtag: {t1.deadline.final_date}")
print(f"Ersparnis: {t1.discount_amount} € (Effektivzins: {t1.effective_annual_interest_pct}% p.a.)")
```

---

## ⚖️ Rechtlicher Hinweis & Disclaimer

> **Wichtiger Hinweis gem. BGH-Rechtsprechung (Az. I ZR 113/20 & I ZR 226/20):**  
> Diese Software und die Berechnungsalgorithmen dienen der mathematischen Simulation und Orientierung zur Fristenberechnung (§ 193 BGB, § 903 ABGB, Art. 78 OR). Sie stellen ausdrücklich **keine** Rechts- oder Steuerberatung im Sinne des Rechtsdienstleistungsgesetzes (RDG) oder Steuerberatungsgesetzes (StBerG) dar. Für verbindliche juristische Fristenwahrungen oder vertragliche Sondervereinbarungen konsultieren Sie bitte einen Rechtsanwalt oder Steuerberater.

---

## 📄 Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Details finden Sie in der [LICENSE](LICENSE)-Datei.
