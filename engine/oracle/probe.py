"""
ChronoVault Oracle — PROBE Engine (future-truth harvesting)
===========================================================
"Main aage ke time me ja kar asli jawab le aata hoon":
  plant()    — Windows Task Scheduler me wakeup task banata hai
               (schtasks, CREATE_NO_WINDOW — screen pe koi window nahi)
  when date  — harvest.py jaag kar asli truth lake prophecy resolve karta hai
  harvest_now() — testing/manual ke liye instant harvest
Agar schtasks fail ho (permissions/locale), honest report + manual command.
Stdlib only. No API keys. Ever.
"""
import json
import os
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CREATE_NO_WINDOW = 0x08000000          # kabhi CMD window nahi khulegi


def _ps_fallback(probe_id: int, when_iso: str) -> dict:
    """schtasks fail ho to PowerShell ScheduledTasks module se koshish."""
    dt = datetime.fromisoformat(when_iso)
    py = sys.executable
    script = os.path.join(HERE, "harvest.py")
    tn = f"ChronoVault_Probe_{probe_id}"
    iso = dt.strftime("%Y-%m-%dT%H:%M:%S")
    ps = (f"$a = New-ScheduledTaskAction -Execute '{py}' "
          f"-Argument '\"{script}\" {probe_id}'; "
          f"$t = New-ScheduledTaskTrigger -Once -At '{iso}'; "
          f"Register-ScheduledTask -TaskName '{tn}' -Action $a -Trigger $t "
          f"-Force | Out-Null")
    cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           creationflags=CREATE_NO_WINDOW, timeout=60)
        return {"ok": r.returncode == 0, "task": tn,
                "detail": (r.stdout.strip() or r.stderr.strip())[:220]}
    except Exception as ex:
        return {"ok": False, "task": tn, "detail": repr(ex)[:200]}


def register_task(probe_id: int, when_iso: str) -> dict:
    """One-shot scheduled task: harvest.py probe_id at date/time.
    schtasks -> PowerShell fallback -> honest failure report."""
    dt = datetime.fromisoformat(when_iso)
    py = sys.executable
    script = os.path.join(HERE, "harvest.py")
    tn = f"ChronoVault_Probe_{probe_id}"
    cmd = ["schtasks", "/Create", "/F", "/TN", tn,
           "/TR", f'"{py}" "{script}" {probe_id}',
           "/SC", "ONCE", "/SD", dt.strftime("%Y/%m/%d"),
           "/ST", dt.strftime("%H:%M")]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           creationflags=CREATE_NO_WINDOW, timeout=30)
        if r.returncode == 0:
            return {"ok": True, "task": tn,
                    "detail": (r.stdout.strip() or "schtasks OK")[:220]}
    except Exception as ex:
        pass        # fall through to PowerShell fallback
    fb = _ps_fallback(probe_id, when_iso)
    fb["via"] = "powershell-fallback"
    return fb


def plant(ledger, prophecy_id: int, due_date: str, at_time: str = "09:00",
          check: dict = None) -> dict:
    """Prophecy ke liye future probe lagao (register + schedule)."""
    when_iso = f"{due_date}T{at_time}:00"
    probe_id = ledger.add_probe(prophecy_id, when_iso, check or {})
    reg = register_task(probe_id, when_iso)
    ledger.con.execute("UPDATE probe SET task_name=? WHERE id=?",
                       (reg["task"], probe_id))
    ledger.con.commit()
    if not reg["ok"]:
        reg["note"] = (f"schtasks fail hua [{reg['detail']}] — manual "
                       f"harvest: tv oracle harvest {probe_id}")
    return {"probe_id": probe_id, "when": when_iso, "check": check,
            "scheduled": reg}


def harvest_now(probe_id: int) -> dict:
    """Instant harvest (test/self-check) — future-ka-intezar ke baghair."""
    import harvest
    return harvest.run_harvest(probe_id)


if __name__ == "__main__":
    from ledger import Ledger
    led = Ledger()
    pid = led.add_prophecy("demo", "PREDICT", "future", "demo", 0.5, "TEST")
    out = plant(led, pid, datetime.now().date().isoformat(), "23:59",
                {"kind": "fx_rate", "endpoint": "fx_frank_USD",
                 "currency": "EUR", "expect": 1.0, "tol_pct": 1.0})
    print("planted:", out["probe_id"], "| when:", out["when"])
    print("scheduled:", json.dumps(out["scheduled"], ensure_ascii=False))
    led.close()
