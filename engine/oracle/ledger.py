"""
ChronoVault Oracle — Paradox Ledger (SQLite, self-verification)
===============================================================
Har prediction yahan zinda hoti hai — aur yahan hi uski sachai janchi jati hai:
  prophecy : ek prediction (question, engine, answer, confidence, badge)
  probe    : future-truth harvest job (Task Scheduler wakeup)
  capsule  : time capsule (aam dil me chhoti chhoti messages future ke liye)
Brier scoring + calibration inhe accuracy.py se milte hain.
Stdlib only. No API keys. Ever.
"""
import json
import os
import sqlite3
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "paradox_ledger.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS prophecy(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT, question TEXT, engine TEXT, time_coord TEXT,
  answer TEXT, confidence REAL, badge TEXT,
  due TEXT, status TEXT DEFAULT 'pending',
  truth TEXT, verified_ts TEXT, meta TEXT
);
CREATE TABLE IF NOT EXISTS probe(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT, prophecy_id INTEGER, when_iso TEXT,
  check_json TEXT, task_name TEXT, status TEXT DEFAULT 'scheduled',
  result TEXT
);
CREATE TABLE IF NOT EXISTS capsule(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT, open_date TEXT, message TEXT, author TEXT,
  status TEXT DEFAULT 'sealed'
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        self.con = sqlite3.connect(path)
        self.con.execute("PRAGMA journal_mode=WAL")
        self.con.executescript(SCHEMA)
        self.con.commit()

    def close(self):
        """Windows pe WAL files lock hote hain — selftests must close()."""
        try:
            self.con.commit()
            self.con.close()
        except Exception:
            pass

    # ------------------------------------------------------------- prophecy
    def add_prophecy(self, question: str, engine: str, time_coord: str,
                     answer: str, confidence: float, badge: str,
                     due: str = None, meta: dict = None) -> int:
        cur = self.con.execute(
            "INSERT INTO prophecy(ts,question,engine,time_coord,answer,"
            "confidence,badge,due,meta) VALUES(?,?,?,?,?,?,?,?,?)",
            (now(), question, engine, time_coord, answer, float(confidence),
             badge, due, json.dumps(meta or {}, ensure_ascii=False)))
        self.con.commit()
        return cur.lastrowid

    def resolve(self, prophecy_id: int, fulfilled: bool, truth: str) -> None:
        self.con.execute(
            "UPDATE prophecy SET status=?, truth=?, verified_ts=? WHERE id=?",
            ("fulfilled" if fulfilled else "violated", truth, now(),
             prophecy_id))
        self.con.commit()

    def prophecy(self, pid: int):
        cur = self.con.execute("SELECT * FROM prophecy WHERE id=?", (pid,))
        row = cur.fetchone()
        return self._prophecy_dict(row) if row else None

    def prophecies(self, status: str = None) -> list:
        if status:
            cur = self.con.execute(
                "SELECT * FROM prophecy WHERE status=? ORDER BY id", (status,))
        else:
            cur = self.con.execute("SELECT * FROM prophecy ORDER BY id")
        return [self._prophecy_dict(r) for r in cur.fetchall()]

    def _prophecy_dict(self, row) -> dict:
        keys = ["id", "ts", "question", "engine", "time_coord", "answer",
                "confidence", "badge", "due", "status", "truth",
                "verified_ts", "meta"]
        d = dict(zip(keys, row))
        d["meta"] = json.loads(d.get("meta") or "{}")
        return d

    # ---------------------------------------------------------------- probe
    def add_probe(self, prophecy_id: int, when_iso: str, check: dict,
                  task_name: str = None) -> int:
        cur = self.con.execute(
            "INSERT INTO probe(ts,prophecy_id,when_iso,check_json,task_name)"
            " VALUES(?,?,?,?,?)",
            (now(), prophecy_id, when_iso,
             json.dumps(check, ensure_ascii=False), task_name))
        self.con.commit()
        return cur.lastrowid

    def probe(self, pid: int):
        cur = self.con.execute("SELECT * FROM probe WHERE id=?", (pid,))
        row = cur.fetchone()
        if not row:
            return None
        keys = ["id", "ts", "prophecy_id", "when_iso", "check_json",
                "task_name", "status", "result"]
        d = dict(zip(keys, row))
        d["check"] = json.loads(d.pop("check_json") or "{}")
        d["result"] = json.loads(d.pop("result") or "null")
        return d

    def probes(self, status: str = None) -> list:
        q = "SELECT id FROM probe" + (" WHERE status=?" if status else "") + \
            " ORDER BY id"
        cur = self.con.execute(q, (status,) if status else ())
        return [self.probe(r[0]) for r in cur.fetchall()]

    def set_probe(self, pid: int, status: str, result: dict) -> None:
        self.con.execute("UPDATE probe SET status=?, result=? WHERE id=?",
                         (status, json.dumps(result, ensure_ascii=False), pid))
        self.con.commit()

    # -------------------------------------------------------------- capsule
    def seal_capsule(self, open_date: str, message: str,
                     author: str = "user") -> int:
        cur = self.con.execute(
            "INSERT INTO capsule(ts,open_date,message,author) "
            "VALUES(?,?,?,?)", (now(), open_date, message, author))
        self.con.commit()
        return cur.lastrowid

    def open_capsules(self) -> list:
        today = datetime.now(timezone.utc).date().isoformat()
        cur = self.con.execute(
            "SELECT * FROM capsule WHERE status='sealed' AND open_date<=?",
            (today,))
        keys = ["id", "ts", "open_date", "message", "author", "status"]
        out = []
        for row in cur.fetchall():
            out.append(dict(zip(keys, row)))
        return out

    # ---------------------------------------------------------------- stats
    def stats(self) -> dict:
        from accuracy import engine_report, calibration_table
        allp = self.prophecies()
        rep = engine_report(allp)
        return {
            "prophecies": len(allp),
            "pending": len([p for p in allp if p["status"] == "pending"]),
            "probes": {"total": len(self.probes()),
                       "scheduled": len(self.probes("scheduled")),
                       "harvested": len(self.probes("harvested"))},
            "sach_rate_by_engine": rep,
            "calibration": calibration_table(allp),
        }


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        led = Ledger(os.path.join(td, "t.db"))
        pid = led.add_prophecy("test q", "PREDICT", "future", "42", 0.7,
                               "PREDICTED", due="2027-01-01")
        prid = led.add_probe(pid, "2027-01-01T09:00",
                             {"kind": "fx_rate", "endpoint": "fx_frank_USD",
                              "currency": "EUR", "expect": 42, "tol_pct": 0.5},
                             "ChronoVault_Probe_x")
        led.set_probe(prid, "harvested", {"value": 41.8})
        led.resolve(pid, True, "41.8")
        led.seal_capsule("2027-01-01", "salam future!")          # sealed
        led.seal_capsule("2020-01-01", "purani baat")            # openable
        st = led.stats()
        assert st["prophecies"] == 1 and st["pending"] == 0
        assert st["sach_rate_by_engine"]["PREDICT"]["hits"] == 1
        assert len(led.open_capsules()) == 1
        print(json.dumps(st, indent=1))
        print("LEDGER SELFTEST: PASS")
        led.close()
