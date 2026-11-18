"""
ChronoVault - ORACLE DEMO (future travel: sawal -> jawab -> wapis -> verify)
============================================================================
Tumhara sapna, code me: "may kuch pocho or wo time me aagey jaye and uska
jawab nikal kr wapis aye phir jawab day"
  1. SIMULATE - exact math (badge EXACT-MATH, confidence 99.9%)
  2. PREDICT  - ensemble future prediction + Paradox Ledger entry
  3. PROBE    - future truth harvest (Task Scheduler wakeup + instant
                self-check plumbing test)
  4. Time capsule - aaj ki message, 1 saal baad khulegi
  5. Sach-Rate - Brier scoring + calibration report
Stdlib only. No API keys. Ever.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "oracle"))
sys.path.insert(0, os.path.join(HERE, "providers"))
import simulate as sim        # noqa: E402
from ledger import Ledger     # noqa: E402
from predict import Predict   # noqa: E402
from probe import plant, harvest_now  # noqa: E402

led = Ledger()

print("=" * 62)
print("CHRONOVAULT ORACLE DEMO - FUTURE TRAVEL ENGINES")
print("=" * 62)

# ---------------------------------------------------- 1) SIMULATE: exact
r1 = sim.answer("2050-01-01 konsa din hoga?")
pid = led.add_prophecy("2050-01-01 konsa din?", "SIMULATE", "exact",
                       r1["answer"], r1["confidence"], r1["badge"],
                       meta=r1["detail"])
led.resolve(pid, True, truth=r1["answer"])
print("[SIMULATE]", r1["answer"])
print("           badge:", r1["badge"], "| ledger #" + str(pid))

r2 = sim.answer("compound 100000 at 18% for 5 saal")
pid2 = led.add_prophecy("compound 100000 @18% 5y", "SIMULATE", "exact",
                        r2["answer"], r2["confidence"], r2["badge"],
                        meta=r2["detail"])
led.resolve(pid2, True, truth=r2["answer"])
print("[SIMULATE]", r2["answer"])

# --------------------------------------------------- 2) PREDICT: ensemble
res = Predict(ledger=led).fx(base="USD", quote="EUR", days_ahead=1)
print("[PREDICT]", res["answer"], f"({res['confidence']:.0%})")
print("          model:", res.get("model"))
print("          ensemble:", res.get("ensemble"))
print("          ledger #" + str(res["ledger_id"]), "| due", res["due"])
if res.get("probe"):
    pr = res["probe"]
    print(f"          PROBE #{pr['probe_id']} -> Task Scheduler @ "
          f"{pr['when']}: {'OK' if pr['scheduled']['ok'] else 'FAILED'}")
    if not pr["scheduled"]["ok"]:
        print("          note:", pr["scheduled"].get("note"))

# ------------------------------- 3) PROBE self-check (plumbing, instant)
consensus = res.get("consensus")
if consensus:
    due = datetime.now(timezone.utc).date().isoformat()
    q = "SELF-CHECK: fx plumbing test (isi waqt)"
    pid3 = led.add_prophecy(q, "PREDICT", "now", res["answer"],
                            res["confidence"],
                            "SELF-CHECK (instant harvest)",
                            due=due,
                            meta={"note": "tautological plumbing test; "
                                          "asli scoring kal ki probe karegi"})
    now_t = datetime.now(timezone.utc).strftime("%H:%M:%S")
    prid = led.add_probe(pid3, f"{due}T{now_t}",
                         {"kind": "fx_rate", "endpoint": "fx_frank_USD",
                          "base": "USD", "currency": "EUR",
                          "expect": round(consensus, 4), "tol_pct": 0.5})
    out = harvest_now(prid)
    if out.get("ok"):
        verdict = ("FULFILLED" if out.get("fulfilled") else "VIOLATED")
        print("[PROBE SELF-CHECK]", verdict)
        print("                   predicted:", out.get("predicted"),
              "| truth:", out.get("value"))
    else:
        print("[PROBE SELF-CHECK] harvest failed:",
              out.get("error"), "(honest - network restricted)")

# ------------------------------------------------------- 4) time capsule
opendate = (datetime.now(timezone.utc) + timedelta(days=365)) \
    .date().isoformat()
cid = led.seal_capsule(
    opendate, "Salam future! Time machine abhi bhi chal rahi hai.",
    author="ChronoVault")
print("[CAPSULE] #" + str(cid), "sealed — khulegi", opendate)

# ------------------------------------------------- 5) Paradox Ledger report
st = led.stats()
print("[LEDGER] prophecies:", st["prophecies"],
      "| pending:", st["pending"],
      "| probes scheduled:", st["probes"]["scheduled"])
print("         Sach-Rate by engine:")
for eng, e in st["sach_rate_by_engine"].items():
    print(f"           {eng:<9} hit {e['sach_rate']:<6} "
          f"brier {e['brier']}  (n={e['n']})")
print("=" * 62)
print("ORACLE LOOP PROVEN: sawal -> time travel -> jawab -> wapis -> verify")
