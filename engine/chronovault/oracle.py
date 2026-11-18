"""ChronoVault 2.0 — Oracle bridge (Paradox Ledger, prophecies, capsules)."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

from .paths import LEDGER_PATH, ORACLE_DIR

sys.path.insert(0, ORACLE_DIR)
from ledger import Ledger  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Oracle:
    def __init__(self):
        self.ledger = Ledger(LEDGER_PATH)

    # ------------------------------------------------------------- prophecies
    def register(self, question: str, answer: str, confidence: float,
                 badge: str, due: str | None, meta: dict | None = None,
                 engine: str = "CHRONO", time_coord: str = "future") -> int:
        return self.ledger.add_prophecy(question, engine, time_coord, answer,
                                        confidence, badge, due, meta or {})

    def add_probe(self, prophecy_id: int, when_iso: str, check: dict,
                  task_name: str | None = None) -> int:
        return self.ledger.add_probe(prophecy_id, when_iso, check, task_name)

    def resolve(self, pid: int, fulfilled: bool, truth: str) -> None:
        self.ledger.resolve(pid, fulfilled, truth)

    def prophecies(self) -> list:
        return self.ledger.prophecies()

    def pending(self) -> list:
        return [p for p in self.ledger.prophecies() if p.get("status") == "pending"]

    def stats(self) -> dict:
        try:
            s = self.ledger.stats()
        except Exception as e:
            s = {"error": str(e)}
        s["ledger"] = LEDGER_PATH
        return s

    # --------------------------------------------------------------- capsules
    def seal_capsule(self, open_date: str, message: str,
                     author: str = "user") -> int:
        return self.ledger.seal_capsule(open_date, message, author)

    def capsules(self, include_sealed: bool = True) -> list:
        try:
            rows = self.ledger.con.execute(
                "SELECT * FROM capsule ORDER BY open_date").fetchall()
            keys = ["id", "ts", "open_date", "message", "author", "status"]
            out = [dict(zip(keys, r)) for r in rows]
        except Exception:
            out = []
        if not include_sealed:
            today = datetime.now(timezone.utc).date().isoformat()
            out = [c for c in out if c.get("open_date", "") <= today]
        return out

    def open_capsules(self) -> list:
        return self.ledger.open_capsules()


def due_probes(oracle: Oracle) -> list:
    now = _now()
    out = []
    for p in oracle.ledger.probes("scheduled"):
        when = (p.get("when_iso") or "")[:19]
        if when and when <= now[:19]:
            out.append(p)
    return out
