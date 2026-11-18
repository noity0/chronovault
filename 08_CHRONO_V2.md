# ⏳ CHRONOVAULT 2.0 — THE KEYLESS TIME MACHINE

> **TL;DR (Hinglish):** Real time machine physics ka koi hole (wormhole) nahi banta — exotic matter chahiye.
> Lekin **ChronoVault 2.0** wahi kaam **asli code** se karta hai: **"Time Fold"** — past (vault/archives) + present (live keyless sources) + future (statistical forecasts + Paradox probes) = ek honest jawab.

## 🧠 Kaise Kaam Karta Hai

Jab aap kuch poochte hain:

1. **Route** — question intent detect hota hai (`router.py`): date / countdown / interest / EMI / FX / crypto / weather / time / holiday / country / news / space / knowledge / forecast / capsule / help.
2. **Open the Time Fold** — parallel keyless sources se data utha jata hai (`sources.py`, `net.py`).
3. **Verify** - EXACT-MATH (exact math), LIVE-CONSENSUS (2+ sources), ARCHIVE (sources).
4. **Forecast** — agar future ka sawal hai, to walk-forward backtest + interval + confidence (`forecast.py`, naive/drift/mean-reversion/exp-smoothing).
5. **Synthesize** — optional keyless LLM (Pollinations) se Roman Urdu polish; verified evidence ke mutabiq.
6. **Record** — answer SQLite memory me, prophecy + probe Paradox Ledger me.

## 🎖️ Badges (Honest labels)

| Badge | Matlab | Trust |
|---|---|---|
| `EXACT-MATH` | Deterministic formula se calculated | 99% confident |
| `LIVE` | 1 source live | moderate |
| `LIVE-CONSENSUS` | 2+ sources agree | high |
| `LIVE-DISAGREE` | sources mayun baat kar rahe hain | lower |
| `ARCHIVE` | Static/documented source | lower |
| `FORECAST` | Backtested statistical projection | advisory |
| `SPECULATIVE` | Background + signals se speculative | low |
| `NO-DATA` / `ERROR` | Source failed / engine error | honest no |

## 🚀 Commands

```bash
# 1) Exact math / future date / EMI / interest
python chrono.py ask "1 Jan 2050 konsa din hoga?"
python chrono.py ask "100000 @ 18% 5 saal compound interest"
python chrono.py ask "50 lakh ka loan 12% 5 saal EMI"

# 2) Live sources (weather / time / FX / crypto / news / knowledge / space)
python chrono.py ask "Lahore ka mausam kaisa hai?"
python chrono.py ask "Lahore me abhi kitne baje hain?"
python chrono.py ask "100 dollar to PKR"
python chrono.py ask "latest AI news"

# 3) Future / forecast + probe registration
python chrono.py forecast "USD/PKR" --days 30
python chrono.py forecast "BTC" --days 60

# 4) Local UI (Time Cockpit) — dark web UI, streaming stages
python chrono.py cockpit            # http://127.0.0.1:8765

# 5) System / registry / probes / memory
python chrono.py status
python chrono.py registry bitcoin
python chrono.py probes run
python chrono.py probes schedule   # daily Task Scheduler job
python chrono.py history
python chrono.py capsule "2027 me khud ko yaad rakhna" --days 365
python chrono.py selftest           # offline unit tests
python chrono.py selftest --online  # + live source smoke
```

## 🖥️ Time Cockpit (Web UI)

`python chrono.py cockpit` se open hota hai:

- **Ask the Future** — streaming stages (`Routing → Source → Synthesize → Done`), answer card, confidence bar, source chips, evidence fold, forecast fan.
- **Timeline** — stored answers, click karke full evidence.
- **Multiverse** — forecasts ke 3 branches (lower / central / upper), units held se value compare.
- **Oracle** — prophecies, probes, scheduler, Brier/calibration.
- **Network** — live provider health, registry categories, cache.
- **Capsules** — future-self message seal.
- **Registry** — 3,909 endpoints search.

## 📚 Sources & Count

- Generated registry: **3,909 keyless endpoints** across 13 categories (time 1,297 · finance 529 · knowledge 421 · weather 283 · calendar 1,096 · misc 115 · news 63 · world 47 · ai 20 · geo 12 · transport 10 · quantum 8 · net 8).
- Direct working sources in v2: Frankfurter / open.er-api / currency-api / Yahoo Finance (FX history), Open-Meteo + wttr.in + Air (weather), CoinGecko + Binance + Coinbase + Kraken (crypto), timeapi.io / worldtimeapi.org, Nager.Date + Google Holiday Calendar, Wikipedia + DuckDuckGo + OpenAlex + Open Library, News RSS (Google/Bing/BBC/Al Jazeera), wheretheiss.at + Open Notify (ISS), USGS + EMSC (earthquakes), NASA APOD, NOAA SWPC, SpaceX.
- LLM: **Pollinations** (keyless, private). Optional: local Ollama (`config.json` → local_ai).

## 🧪 Honest Limits

- Weather/AQI numbers live hain, but cross-source agreement check hota hai (spread).
- Forecast confidence = backtest skill + data length + directional accuracy — statistical, guarantee nahi.
- AI synthesis hamesha evidence par ground haath rakhta hai; jab no source milta hai to unverified AI answer dikhta hai (badge `UNVERIFIED-AI`).
- Real time travel impossible hai — jo bhi "travel" hai woh retrieval + forecasting + honest labels.

## 🩺 Troubleshooting

| Problem | Fix |
|---|---|
| `HTTP 502` / "local server se connection nahi bana" | Cockpit server band hai — `python chrono.py cockpit` dobara chalayein. VPN/proxy ho to `localhost` bypass karein. |
| Koi source `HTTP 502` de | Engine ek dafa retry karta hai, phir fallback source try karta hai; sab fail hon to jawab `NO-DATA` hota hai (jhoot nahi). |
| Port busy | Server 8765 se 8776 tak khud try karta hai; terminal me asli URL likha hota hai. |
| Console me unicode issue | Windows Terminal use karein ya `$env:PYTHONIOENCODING='utf-8'` set karein. |

## 🔧 Status

- [x] v2 core modules: paths, registry, net, places, text, formulas, forecast, sources, router, ask, memory, oracle, probes
- [x] `chrono.py` CLI complete
- [x] Time Cockpit server + UI complete + browser-verified
- [x] Offline unit tests 22/22 pass
- [x] Live smoke suite `--online` pass (time/fx/weather/crypto/knowledge/space/llm)
- [x] End-to-end QA suite `comprehensive_test.py` — 22/22 pass
- [x] Docs + GitHub packaging final
