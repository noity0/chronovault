"""
ChronoVault — Live smoke test: proves the keyless endpoints are REAL.
Pings one endpoint per category + one ensemble cross-check.
No keys. Run: python smoke_test.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import Providers  # noqa: E402

TESTS = [
    ("time", "time_wt_UTC"),
    ("time-mirror", "time_tio_UTC"),
    ("knowledge", "wiki_en_summary", {"title": "Time_travel"}),
    ("knowledge-hi", "wiki_hi_summary", {"title": "समय"}),
    ("finance", "fx_frank_USD"),
    ("calendar", "holiday_nager_IN", {"year": "2026"}),
    ("weather", "weather_om_best_match", {"lat": "28.61", "lon": "77.23"}),
    ("ai", "ai_pollinations_text", {"prompt": "Say only: CHRONOVAULT ONLINE"}),
    ("world", "fact_earthquakes_usgs"),
    ("net", "ip_ipwhois"),
]

p = Providers()
print("=" * 60)
print(f"REGISTRY: {p.meta['total_endpoints']} keyless endpoints loaded")
print("=" * 60)

hits = 0
net_blocks = 0
for t in TESTS:
    name, eid = t[0], t[1]
    params = t[2] if len(t) > 2 else {}
    try:
        r = p.get(eid, timeout=12, **params)
    except Exception as ex:  # never crash the whole smoke run
        r = {"ok": False, "error": repr(ex)[:150]}
    status = "OK " if r.get("ok") else "FAIL"
    hits += int(bool(r.get("ok")))
    net_blocks += int(r.get("kind") == "network_restricted")
    preview = str(r.get("data", r.get("error", "")))[:90].replace("\n", " ")
    print(f"[{status}] {name:<14} {eid:<28} {r.get('ms', '-'):>5}ms  {preview}")

print("-" * 60)
if net_blocks and hits == 0:
    print("NETWORK RESTRICTED in this environment (DNS/TLS blocked).")
    print("This is expected in sandboxed dev machines. On a normal PC these")
    print("endpoints open. The system stays OFFLINE-FIRST either way:")
    print("SIMULATE / VAULT / local AI / CSPRNG work without any internet.")
print(f"LIVE HIT RATE: {hits}/{len(TESTS)} endpoints answered with ZERO API keys")
