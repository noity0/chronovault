# 🔌 KEYLESS PROVIDER NETWORK — 1888 Real Endpoints, ZERO API Keys

> TL;DR: User se KABHI API key nahi mangi jayegi (policy: `config.json → policy.api_keys_required: false`).
> Iske bajaye machine ke paas **1888 asli, public, keyless endpoints** hain — timezones,
> languages, currencies, countries, weather models aur quantum hardware sab real URL families
> me expand hote hain. Sab kuch `registry.json` me hai.

---

## 1. REGISTRY STATS (auto-generated: `generate_registry.py`)

| Category | Endpoints | Source families |
|---|---|---|
| time | 1196 | worldtimeapi.org + timeapi.io (598 IANA zones × 2) |
| calendar | 240 | date.nager.at public holidays (120 countries × years) |
| knowledge | 221 | Wikipedia (180+ language editions; major langs ×2: search+summary) |
| finance | 183 | open.er-api.com (160 currencies) + frankfurter (ECB, 29 bases) + crypto |
| weather | 25 | Open-Meteo (23 real forecast models + air + marine + geocoding) |
| quantum | 5 | **ANU QRNG (REAL photon quantum RNG!)** + random.org + local CSPRNG |
| ai | 5 | Pollinations (keyless LLM + image) + Ollama/LM Studio (local AI) |
| world | 4 | USGS earthquakes, NASA APOD (official public DEMO_KEY), World Bank, REST Countries |
| misc | 4 | ZenQuotes, AdviceSlip, Quotable, Universities |
| geo | 3 | Open-Meteo geocoding, Nominatim (OSM), Photon |
| net | 2 | ipwho.is, ipapi.co |
| **TOTAL** | **1888** | sab `requires_key: false` |

**Regenerate:** `python engine/providers/generate_registry.py`
**Live proof:** `python engine/providers/smoke_test.py` (har category ka 1 endpoint ping)

## 2. HEALTH TRACKING (accuracy ka pehla layer)
- `engine/providers/health.json` — har endpoint ka ok/fail count + avg latency.
- `Providers.score(id)` — success rate × failure penalty; unproven endpoints ko thoda
  penalty (reliability × 0.9). Jo baar-baar fail ho wo automatically niche chala jata hai
  (circuit breaker effect). Koi manual configuration nahi chahiye.

## 3. ENSEMBLE CROSS-CHECK (accuracy ka main layer)
```python
p = Providers()
r = p.ensemble("finance", extractor=lambda d: d["rates"]["EUR"], n=4)
# r["verified"] == True  -> 4 independent sources ne SAME jawab diya
# r["agreement"]         -> 0..1, confidence boost isse aata hai
```
- Rule: **minimum 3 independent sources agree** → hi jawab "verified" badge payega.
- Parallel fetch (ThreadPoolExecutor), 12s timeout, fail = health penalty.

## 4. QUANTUM TIER SYSTEM (honesty labels)
| Tier | Source | Kya hai |
|---|---|---|
| 1 | ANU QRNG | **REAL quantum** — photon vacuum fluctuations |
| 2 | random.org | atmospheric noise (quantum nahi, honest label) |
| 3 | os.urandom | offline CSPRNG fallback, hamesha kaam karta hai |

## 5. LOCAL AI (optional, keyless by nature)
- Ollama `localhost:11434` / LM Studio `localhost:1234` — agar user kabhi install kare
  to AI 100% offline. **Zaroori nahi** — Pollinations keyless cloud fallback pehle se
  registry me hai.

## 6. ACCURACY STACK (poora order, top to bottom)
1. **Exact-first routing** — calendar/finance/physics = EXACT math, no prediction
2. **Ensemble cross-check** — ≥3 independent sources, agreement ratio
3. **Health-demoted providers** — endpoints khud apni trust kamate/khote hain
4. **Walk-forward backtesting** — `engine/oracle/accuracy.py::backtest` — model ko
   Vault history pe test karke hi confidence issue hota hai
5. **Calibration table** — raw confidence ko empirical hit-rate se correct karna
6. **Brier scoring** — har prophecy ka score, "Oracle Sach-Rate" dashboard
7. **Provenance badges** — har jawab ke saath source + method, jhooth ka scope hi nahi

## 7. NOTES
- NASA APOD `DEMO_KEY` — NASA ka official public demo key hai (30 req/hr, IP-based),
  ye kisi user ki personal key nahi hai. Baaki sab bilkul keyless.
- Kisi endpoint ka format badle to: health usko demote kar dega, ensemble doosre
  sources se answer dega — system resilient by design.
