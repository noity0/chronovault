# ⏳ PROJECT TIME MACHINE — ChronoVault

> **TL;DR (Hinglish):** Real time machine physics me possible nahi (wormhole chahiye, exotic matter chahiye 😅).
> Lekin ek **asli, kaam karne wali time machine code se ban sakti hai** — aapke PC ki digital zindagi ke liye.
> Ye project ek aisi cheez hai jo aaj tak kisi ne combine nahi ki: **real-time snapshots + time travel UI + MULTIVERSE (branching timelines)**.
> Poora offline, poora private, D:\Time Machine me stored.

---

## 📁 Is Folder Me Kya Hai

| File | Kya hai |
|------|---------|
| `00_README.md` | Ye file — project ka index |
| `01_RESEARCH.md` | Deep research: physics reality check, Apple Time Machine internals, restic/Borg engine design, Microsoft Recall, Windows APIs (USN + VSS) |
| `02_CONCEPT.md` | The Big Idea — jo kisi ne nahi banaya, aur kyun ye kaam karega |
| `03_PLAN.md` | Architecture, data model, algorithms, phases, risks, build checklist |
| `04_ORACLE.md` | Future-travel system: SIMULATE / PROBE / PREDICT + Paradox Ledger |
| `05_PROVIDERS.md` | 1888 keyless API endpoints + accuracy stack (zero API keys needed) |
| `06_QUANTUM.md` | Quantum & Relativistic Lab — ANU quantum RNG, GPS math, entropy, lightcones |

## 🚀 Ek Line Me

**ChronoVault** = *"Git + Apple Time Machine + a time-travel cockpit, for your entire digital life — with branching timelines (multiverse), a future-travel Oracle, and real quantum physics."*

## 🕰️ Version 2.0 (Abhi Bana Hua / Live) — ChronoVault 2.0

`engine/chronovault/` aur `chrono.py` me **v2 time machine** complete build hai:

- Keyless **3,909-endpoint** registry (`registry_v2.json`) + 13 categories
- Question → **Time Fold** (past + live present + future forecast) → honest answer with badges
- Future predictions → **Paradox Ledger + probes + Brier calibration** (`engine/chronovault/`)
- Local **Time Cockpit** UI (`engine/chronovault/cockpit.html` + `serve.py`)
- CLI: `python chrono.py ask/forecast/cockpit/status/registry/probes/capsules/history/selftest`
- Offline tests: `python chrono.py selftest` → **22/22 PASS** · live smoke: `python chrono.py selftest --online`
- Full docs: `08_CHRONO_V2.md`

Full workflow in Roman Urdu: **`08_CHRONO_V2.md`**.


## 🧭 Status

- [x] Phase 0 — Research + Planning
- [x] Phase 0.5 — Keyless Provider Network (1888 endpoints) + Quantum Lab modules + Accuracy engine
- [x] Phase 1 — FluxCore engine MVP (CLI time dial)
- [ ] Phase 2 — Real-time engine (USN journal watcher)
- [ ] Phase 3 — Time Cockpit UI (wormhole scrubber)
- [x] Phase 4 (CORE) — Multiverse branching timelines: fork/switch/cherry-pick/map LIVE (`engine\fluxcore\multiverse.py` + `tv branch ...`)
- [x] Phase 5 (CORE) — Oracle future travel: SIMULATE (exact math) + PREDICT (ensemble + calibration) + PROBE (Task Scheduler truth harvest) + Paradox Ledger (`tv oracle ...`)
- [ ] Phase 6 — Relativity Lab + polish
