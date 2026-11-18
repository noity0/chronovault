"""ChronoVault 2.0 — probe harvesting + Windows scheduled task.

Predictions are only honest if the future is checked.  Each forecast stores
a machine-checkable `check` spec; this module wakes up later, fetches the
real value, resolves the prophecy, and lets the Brier score update itself.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from . import sources
from .paths import ROOT


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _harvest_check(check: dict) -> tuple[bool, str, dict]:
    kind = check.get("kind")
    if kind == "fx_rate":
        b = sources.fx_rate(check["base"], check["currency"])
        if not b.get("ok"):
            return False, "provider offline", {"error": "no data"}
        truth = b["data"]["rate"]
        expect = float(check["expect"])
        tol = float(check.get("tol_pct", 3))
        err = abs(truth - expect) / expect * 100 if expect else 999
        ok = err <= tol
        return ok, (f"1 {check['base']} = {truth:,.4f} {check['currency']} "
                    f"(predicted {expect:,.4f}, error {err:.2f}%, tol {tol}%)"), {
            "value": truth, "predicted": expect, "error_pct": round(err, 3),
            "published": b["data"].get("date")}
    if kind == "crypto_usd":
        coin = check["coin"]
        b = sources.crypto_price(coin, check.get("symbol", coin.upper()))
        if not b.get("ok"):
            return False, "provider offline", {"error": "no data"}
        truth = b["data"]["usd"]
        expect = float(check["expect"])
        tol = float(check.get("tol_pct", 5))
        err = abs(truth - expect) / expect * 100 if expect else 999
        ok = err <= tol
        return ok, (f"1 {check.get('symbol', coin)} = ${truth:,.2f} "
                    f"(predicted ${expect:,.2f}, error {err:.2f}%, tol {tol}%)"), {
            "value": truth, "predicted": expect, "error_pct": round(err, 3)}
    return False, "no automated checker for this prediction", {"error": "manual"}


def harvest_due(oracle, limit: int = 20) -> list[dict]:
    now = _now()
    out = []
    for p in oracle.ledger.probes("scheduled"):
        if len(out) >= limit:
            break
        when = (p.get("when_iso") or "")[:19]
        if not when or when > now[:19]:
            continue
        check = p.get("check") or {}
        ok, truth, detail = _harvest_check(check)
        try:
            oracle.resolve(p["prophecy_id"], ok, truth)
        except Exception as e:
            detail["resolve_error"] = str(e)
        try:
            oracle.ledger.set_probe(p["id"], "harvested", {
                "ok": ok, "truth": truth, **detail, "at": now})
        except Exception:
            pass
        out.append({"probe_id": p["id"], "prophecy_id": p["prophecy_id"],
                    "ok": ok, "truth": truth, "check": check})
    return out


def schedule_daily(python: str | None = None) -> dict:
    """Create/refresh a daily catch-up task. Works without admin (PowerShell)."""
    py = python or sys.executable
    script = os.path.join(ROOT, "chrono.py")
    task = "ChronoVault_Daily"
    ps = f"""
$ErrorActionPreference = 'Stop'
$action = New-ScheduledTaskAction -Execute '{py}' -Argument '"{script}" probes run' -WorkingDirectory '{ROOT}'
$trigger = New-ScheduledTaskTrigger -Daily -At 23:59
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName '{task}' -Action $action -Trigger $trigger -Settings $settings -Description 'ChronoVault: harvest due future probes and update Brier accuracy' -Force | Out-Null
$t = Get-ScheduledTask -TaskName '{task}'
"OK " + $t.TaskName + " " + $t.State
"""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, text=True, timeout=60,
                           creationflags=0x08000000)
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        return {"ok": r.returncode == 0 and out.startswith("OK"),
                "task": task, "output": out, "error": err if r.returncode else ""}
    except Exception as e:
        return {"ok": False, "task": task, "error": f"{type(e).__name__}: {e}"}


def task_status() -> list[dict]:
    ps = ("Get-ScheduledTask -TaskName 'ChronoVault*' -ErrorAction SilentlyContinue | "
          "Select-Object TaskName,State | ConvertTo-Json -Compress")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, text=True, timeout=30,
                           creationflags=0x08000000)
        txt = (r.stdout or "").strip()
        if not txt:
            return []
        data = json.loads(txt)
        return data if isinstance(data, list) else [data]
    except Exception:
        return []


def run_cli() -> int:
    from .oracle import Oracle
    o = Oracle()
    res = harvest_due(o)
    if not res:
        print("Koi due probe nahi hai. (Sab future predictions abhi pending hain.)")
    for r in res:
        print(("FULFILLED " if r["ok"] else "VIOLATED  ") +
              f"probe #{r['probe_id']} → {r['truth']}")
    st = o.stats()
    print(f"\nProphecies: {st.get('prophecies')} | pending: {st.get('pending')}")
    return 0
