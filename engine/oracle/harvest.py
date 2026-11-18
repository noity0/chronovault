"""
ChronoVault Oracle — PROBE: harvest entrypoint
==============================================
Task Scheduler wakeup script: `python harvest.py <probe_id>`
Jab future date aati hai, ye:
  1. probe row parhta hai (kaunsa endpoint, kya expect kiya tha)
  2. asli truth fetch karta hai (keyless providers)
  3. prediction se compare karke prophecy resolve karta hai
  4. Brier/Sach-Rate ledger me apne aap update ho jata hai
Yahan se `tv oracle harvest <id>` (instant harvest) bhi chalta hai.
Stdlib only. No API keys. Ever.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "providers"))
from ledger import Ledger                     # noqa: E402
from client import Providers                  # noqa: E402


def _fx_value(check: dict, p: Providers):
    r = p.get(check["endpoint"], base=check.get("base", "USD"))
    if not r.get("ok"):
        return None, r.get("error", "fetch failed")
    d = r["data"]
    rates = d.get("rates") if isinstance(d, dict) else None
    cur = check.get("currency", "EUR")
    if isinstance(rates, dict) and cur in rates:
        try:
            return float(rates[cur]), None
        except (TypeError, ValueError):
            return None, "rate not numeric"
    return None, "currency missing in response"


def run_check(check: dict, p: Providers = None) -> dict:
    """Future truth harvest — check spec ke mutabiq asli data lao."""
    p = p or Providers()
    kind = check.get("kind")
    if kind == "fx_rate":
        v, err = _fx_value(check, p)
        return {"ok": v is not None, "value": v, "error": err,
                "endpoint": check.get("endpoint")}
    return {"ok": False, "value": None,
            "error": f"unknown check kind: {kind}"}


def _compare(value, check: dict):
    exp = check.get("expect")
    tol = float(check.get("tol_pct", 0.5)) / 100.0
    if value is None or exp is None:
        return False
    try:
        return abs(float(value) - float(exp)) <= abs(float(exp)) * tol
    except (TypeError, ValueError):
        return str(value) == str(exp)


def run_harvest(probe_id: int, p: Providers = None) -> dict:
    led = Ledger()
    pr = led.probe(probe_id)
    if not pr:
        return {"ok": False, "error": f"probe {probe_id} not found"}
    res = run_check(pr["check"], p)
    led.set_probe(probe_id, "harvested" if res["ok"] else "failed", res)
    prop = led.prophecy(pr["prophecy_id"])
    if prop and res["ok"]:
        fulfilled = _compare(res["value"], pr["check"])
        led.resolve(pr["prophecy_id"], fulfilled, truth=str(res["value"]))
        res["prophecy_id"] = pr["prophecy_id"]
        res["fulfilled"] = fulfilled
        res["predicted"] = prop["answer"]
        res["confidence"] = prop["confidence"]
    return res


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python harvest.py <probe_id>")
        sys.exit(1)
    out = run_harvest(int(sys.argv[1]))
    print(json.dumps(out, ensure_ascii=False, indent=1))
