# 🏗️ THE PLAN — Architecture, Phases, Build Checklist

> TL;DR: Poora system 5 layers ka hai: FluxCore engine (capture + dedup) → Vault (past) →
> Oracle (future: SIMULATE/PROBE/PREDICT + Paradox Ledger) → Multiverse (branches) →
> Time Cockpit (UI). Python se MVP, baad me Rust-accelerated. Phase-wise checklist neeche.

---

## 1. SYSTEM ARCHITECTURE

```
┌─────────────────────────── WATCHED SOURCES ───────────────────────────┐
│  C:\Users\...\Documents   D:\Projects   ... (user configurable)       │
└──────┬────────────────────────────────────────────────┬───────────────┘
       │ (real-time)                                    │ (consistent point-in-time)
┌──────▼──────────────┐                     ┌───────────▼───────────┐
│ USN Journal Watcher │                     │ VSS Shadow Copy (WMI) │
│ (NTFS change feed)  │                     │ (locked files ke liye)│
└──────┬──────────────┘                     └───────────┬───────────┘
       │ event queue (SQLite WAL)                       │
┌──────▼────────────────────────────────────────────────▼───────────────┐
│                    FLUXCORE ENGINE (Python 3.12)                      │
│  • FastCDC chunker (rolling hash, 64B window; 2KB–8MB chunks)         │
│  • SHA-256 content addressing → Object Store (zstd compressed)        │
│  • Tree manifests (git-style hash trees) + delta vs parent snapshot   │
│  • Retention bands (hourly/daily/weekly/monthly + space guard)        │
└──────┬────────────────────────────────────────────────────────────────┘
       │
┌──────▼────────────────────────────────────────────────────────────────┐
│                          VAULT  (D:\Time Machine\Vault)               │
│  objects/<2>/<64-hex chunk>   •  index.db (SQLite WAL)                │
└──────┬───────────────────────────────────────┬─────────────────────────┘
       │                                       │
┌──────▼─────────────┐              ┌──────────▼─────────────────────────┐
│  PAST — Vault API  │              │  FUTURE — Oracle                   │
│  time scrub, diff, │              │  Router → SIMULATE / PROBE /       │
│  preview, restore  │              │  PREDICT + Paradox Ledger +        │
│  (anchor-first)    │              │  Probes(Task Scheduler) + Capsules │
└──────┬─────────────┘              └──────────┬─────────────────────────┘
       │                                       │
┌──────▼───────────────────────────────────────▼─────────────────────────┐
│  MULTIVERSE — branches (timeline trees) + merge/cherry-pick            │
└──────┬─────────────────────────────────────────────────────────────────┘
       │
┌──────▼─────────────────────────────────────────────────────────────────┐
│  TIME COCKPIT (local web UI: FastAPI + browser)                        │
│  wormhole scrubber • time-forest tree view • answer cards + badges     │
│  branch map (spider-graph) • prophecy dashboard • countdowns           │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2. DATA MODEL (SQLite — `Vault\index.db`)

```sql
-- PAST side
branch(id, name, color, parent_branch_id, parent_snapshot_id, created_at, is_prime, status)
snapshot(id, branch_id, parent_snapshot_id, ts, label, kind, root_tree_hash, size_delta)
tree(hash PK, entries TEXT)              -- dir node: name→(type,child_hash,size,mtime)
chunk(hash PK, size, csize, refcount)    -- content-addressed, zstd compressed
path(id, parent_id, name)                -- normalized path tree
file_version(path_id, snapshot_id, tree_hash, size, mtime, status)
event(id, ts, op, path_id, frn, usn)     -- USN journal feed (real-time layer)

-- FUTURE side (Oracle)
prophecy(id, question, time_coordinate, domain, engine, confidence,
         predicted_answer, target_at, status, actual_answer, verified_at, error)
probe(id, collector_type, params_json, trigger_at, status, result_json, prophecy_id)
capsule(id, payload_path, deliver_at, sealed_hash, status)
calibration(engine, window, brier_score, n_prophecies)
```

## 3. CORE ALGORITHMS

1. **Snapshot:** walk roots → build tree → dir-hash compare with parent (prune identical subtrees) → chunk only new files → store new chunks → write manifest.
2. **CDC chunking:** Rabin-style rolling hash, 64B window, boundary jab low-21-bits zero; min 2KB / avg 64KB / max 8MB (FastCDC-style). Insert file ke start me ho to bhi aage ke chunks reuse.
3. **Travel (read past):** resolve snapshot root tree → serve tree (UI time-view) — disk kabhi touch nahi hota.
4. **Restore:** pehle current state ka anchor snapshot ("You are here") → phir copy out. Never in-place without anchor (btrfs-timeline ka lesson: history tool ki worst failure current file destroy karna).
5. **Branch switch:** anchor current → write target branch head's tree → update active_branch. Warning UI for unsaved work.
6. **Forecast:** snapshot-history time series → backtest 3 models on last N weeks → best model → project forward with CI.
7. **Probe lifecycle:** prophecy → probe row → `schtasks /create` trigger at X → collector runs → ledger update → cockpit notification.

## 4. TECH STACK

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.12 | Fast to build, stdlib rich; Rust later for hot paths |
| Storage | SQLite WAL + files | Zero-config, robust, local |
| Compression | zstandard | Speed + ratio |
| Chunking | FastCDC-style (own impl; Rust crate later) | Dedup efficiency |
| Real-time | USN Journal (pywin32 ctypes) + watchdog fallback | Live history, works offline |
| Locked files | VSS via WMI `Win32_ShadowCopy.Create` | Open files bhi capture |
| Scheduler | Windows Task Scheduler (schtasks) | Probes/capsules — PC off ho to next boot pe catch-up |
| UI | FastAPI + single-page (vanilla/htmx first) | Local web cockpit, no Electron bloat |
| CLI | rich + click (a.k.a `tv`) | Power-user + scripts |

## 5. PHASES

### ✅ Phase 0 — Research + Plan (DONE — aaj)
### Phase 1 — FluxCore MVP (CLI "time dial")  ← NEXT
- [ ] `tv init` — config: watched paths, excludes (.git, node_modules, *.tmp, cloud placeholders), vault quota
- [ ] `tv snap` — manual snapshot → CDC store → tree manifest
- [ ] `tv list` — timeline of snapshots (size deltas)
- [ ] `tv travel <date|id>` — browse read-only tree at that moment
- [ ] `tv diff <a> <b>` — two moments ka file-level diff
- [ ] `tv restore <path> [--from <date>]` — anchor-first restore
- [ ] `tv stats` — vault size, dedup ratio, chunk counts
- [ ] Unit tests: chunker invariants, restore round-trip

### Phase 2 — Real-time engine
- [ ] USN journal watcher (admin) + event queue
- [ ] Debounced auto-snapshots ("change detected → snap in ≤60s")
- [ ] VSS path for locked files
- [ ] Retention auto-thin + space guard (80% quota → prune bands)
- [ ] Auto-start (startup task) + health heartbeat

### Phase 3 — Time Cockpit (UI)
- [ ] Wormhole scrubber (date dial → time-forest tree view)
- [ ] Version preview + side-by-side diff
- [ ] Timeline of day (USN events as "kya hua is din")
- [ ] Search across versions (FTS5)

### Phase 4 — Multiverse
- [ ] `tv branch <from_snapshot> "what-if-name"`
- [ ] Timeline switch + branch map visualization
- [ ] Cherry-pick files across timelines + timeline diff

### Phase 5 — Oracle (Future travel)  ← tumhara favorite 😄
- [ ] Question router (time coordinate + domain classify)
- [ ] SIMULATE: calendar math, finance, file-growth models
- [ ] PREDICT: forecast + confidence → prophecy rows
- [ ] PROBE: Task Scheduler collectors (FileState first, web opt-in later)
- [ ] Paradox Ledger: verification, Brier scores, "Oracle Sach-Rate" dashboard
- [ ] Time Capsules + Sealed Answers + countdown dashboard

### Phase 6 — Relativity Lab + polish
- [ ] Lorentz calculator (speed/altitude → real dilation)
- [ ] Wormhole animations, sounds, sci-fi skin
- [ ] Packaging (single folder, task-scheduler install, README)

## 6. RISKS & MITIGATIONS

| Risk | Mitigation |
|---|---|
| Admin rights chahiye (USN/VSS) | Graceful fallback (watchdog polling), clear setup wizard |
| Locked files | VSS path; skip-with-log last resort |
| Storage bloat | CDC dedup + retention bands + quota guard + big-file threshold |
| Restore destroys current | ALWAYS anchor-first + dry-run preview + never in-place silently |
| Antivirus false positives | Simple known-good patterns, local only, no obfuscation |
| OneDrive/cloud conflicts | Placeholder/attribute detection, exclude by default |
| Wrong confidence (jhooth) | Paradox Ledger + mandatory provenance badges |
| PC off at probe time | Task Scheduler catch-up on boot + "missed probe" honesty badge |

## 7. STORAGE MATH (D: drive — 156 GB free)
- Vault quota default: **80 GB** (safety margin). CDC dedup on typical document/code mixes: 3–10× compression vs naive copies.
- Zstd level 3 default. Text-heavy data: zyada bachat. Videos: kam (chunk-level dedup still helps).
- Prune policy (like Apple): last 24h hourly, last 30d daily, last 12mo weekly, older monthly, minimum space guard 20 GB.

## 8. FIRST BUILD SESSION CHECKLIST (Phase 1 start)
1. `D:\Time Machine\engine\` — Python package: `fluxcore/` (chunker, store, indexer), `vault/` (api), `oracle/` (router stubs), `cli.py`
2. Chunker + store + snapshot of a test folder → verify dedup on second snapshot
3. `tv list/travel/restore` — round-trip test
4. Config + excludes + anchor-restore safety
5. Milestone: **"time scrub karke 1 file purane version me restore karo — successfully"**
