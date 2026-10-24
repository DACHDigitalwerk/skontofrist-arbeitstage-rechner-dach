# -*- coding: utf-8 -*-
import json
import subprocess
import sys


def test_cli_help():
    cmd = [sys.executable, "automation/github_staging/repo24/skontofrist_dach/cli.py", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "dach-skontofrist" in res.stdout
    assert "--net-days" in res.stdout


def test_cli_standard_execution():
    cmd = [
        sys.executable,
        "automation/github_staging/repo24/skontofrist_dach/cli.py",
        "--date", "2026-06-01",
        "--amount", "5000",
        "--net-days", "30",
        "--skonto-days", "14",
        "--skonto-pct", "3.0",
        "--country", "DE",
        "--state", "BY",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "DACH SKONTOFRIST-" in res.stdout
    assert "NETTO-ZAHLUNGSZIEL" in res.stdout
    assert "MAXIMALER LIQUIDITÄTSVORTEIL" in res.stdout


def test_cli_json_output():
    cmd = [
        sys.executable,
        "automation/github_staging/repo24/skontofrist_dach/cli.py",
        "--date", "2026-05-15",
        "--amount", "8000",
        "--net-days", "30",
        "--skonto-days", "10",
        "--skonto-pct", "2.5",
        "--country", "CH",
        "--state", "ZH",
        "--json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["country"] == "CH"
    assert data["state_or_canton"] == "ZH"
    assert data["invoice_amount"] == 8000.0
    assert len(data["skonto_tiers"]) == 1
    assert data["skonto_tiers"][0]["discount_amount"] == 200.0  # 2.5% of 8000
