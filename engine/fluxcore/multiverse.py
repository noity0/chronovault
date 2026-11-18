"""
ChronoVault FluxCore — Multiverse (branching timelines)
======================================================
THE novel feature: timelines fork like universes.

Ledger: branches.jsonl (append-only, vault root) — event types:
  {"ev":"branch",   name, parent, base:[{path,root}], seed:"Q-...", tier, ts}
  {"ev":"activate", name, ts}
  {"ev":"cherry",   from, member, into, ts}

Rules:
  * every branch is born with a REAL quantum seed (engine/quantum/qrng.py,
    tiered ANU -> atmospheric -> CSPRNG, honest tier label stored forever)
  * active = last activate event, else "Prime"
  * head(branch) = newest snapshot tagged with that branch; legacy snapshots
    without a branch field count as Prime
  * switch() = ANCHOR current state on the outgoing timeline -> materialize
    the target timeline's head via Engine.restore_tree (SAFE mode) ->
    append activate event. Anchor-first, always.
"""
import json
import os
import sys
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "quantum"))
import qrng  # noqa: E402

RESERVED = {"Prime"}
_UNSAFE = set('/\\:*?"<>|')


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Multiverse:
    def __init__(self, engine):
        self.eng = engine
        self.ledger = os.path.join(engine.v.root, "branches.jsonl")

    # ------------------------------------------------------------ ledger io
    def _events(self) -> list:
        if not os.path.exists(self.ledger):
            return []
        with open(self.ledger, "r", encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]

    def _append(self, ev: dict) -> dict:
        with open(self.ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ev

    # -------------------------------------------------------------- queries
    def active(self) -> str:
        acts = [e["name"] for e in self._events() if e["ev"] == "activate"]
        return acts[-1] if acts else "Prime"

    def branches(self) -> list:
        out = {}
        for e in self._events():
            if e["ev"] == "branch":
                out[e["name"]] = e          # birth order preserved
        return list(out.values())

    def exists(self, name: str) -> bool:
        return name == "Prime" or any(b["name"] == name for b in self.branches())

    def head(self, branch: str):
        """Newest snapshot on this timeline, or None if none yet."""
        for s in reversed(self.eng.snapshots()):
            if s.get("branch", "Prime") == branch:
                return s
        return None

    def head_roots(self, branch: str) -> list:
        """Roots to materialize for a timeline: its head snapshot, else the
        branch's birth base (the parent's head at fork time)."""
        s = self.head(branch)
        if s:
            return s["roots"]
        for b in self.branches():
            if b["name"] == branch:
                return b.get("base", [])
        if branch == "Prime":
            return []                       # virgin Prime: nothing yet
        raise KeyError(f"unknown branch: {branch}")

    # ---------------------------------------------------------------- forks
    def create(self, name: str, from_branch: str = None,
               label: str = "") -> dict:
        if not name or any(c in _UNSAFE for c in name):
            raise ValueError("branch name: clean single token chahiye")
        if name in RESERVED:
            raise ValueError("'Prime' main timeline ke liye reserved hai")
        if self.exists(name):
            raise ValueError(f"branch already exists: {name}")
        parent = from_branch or self.active()
        if not self.exists(parent):
            raise KeyError(f"unknown parent branch: {parent}")
        q = qrng.quantum_seed(64)           # REAL quantum randomness (tiered)
        return self._append({
            "ev": "branch", "name": name, "parent": parent,
            "base": self.head_roots(parent),
            "seed": q["seed"], "tier": q["tier"],
            "label": label, "ts": _now(),
        })

    def activate(self, name: str) -> dict:
        if not self.exists(name):
            raise KeyError(f"unknown branch: {name}")
        return self._append({"ev": "activate", "name": name, "ts": _now()})

    # ------------------------------------------------------ switch (jump!)
    def switch(self, name: str, watched_paths=None) -> dict:
        """TIME TRAVEL BETWEEN TIMELINES:
        1) ANCHOR current live state on the outgoing timeline
        2) materialize target timeline's head into its paths (SAFE mode)
        3) activate the target timeline
        """
        if not self.exists(name):
            raise KeyError(f"unknown branch: {name}")
        out_branch = self.active()
        paths = watched_paths if watched_paths is not None else self._watched()
        anchor = None
        if paths and out_branch != name:
            anchor = self.eng.snapshot(
                paths, label=f"anchor: before switch {out_branch} -> {name}",
                branch=out_branch)
        written_total, extras = 0, []
        for r in self.head_roots(name):
            rep = self.eng.restore_tree(r["root"], r["path"])
            written_total += rep["written"]
            extras += rep["extra_live_left"]
        self.activate(name)
        return {"from": out_branch, "to": name, "anchor": anchor,
                "files_written": written_total, "extra_live_left": extras}

    def _watched(self) -> list:
        cfg_p = os.path.join(os.path.dirname(os.path.dirname(_HERE)),
                             "config.json")           # engine/fluxcore -> root
        try:
            with open(cfg_p, "r", encoding="utf-8") as f:
                return json.load(f)["watched_paths"]
        except Exception:
            return []

    # -------------------------------------------------------- cherry-picking
    def cherry_pick(self, from_branch: str, member: str,
                    out_path: str = None) -> str:
        """Borrow ONE file from another timeline into this one. Provenance
        event ledger me append hota hai (Paradox Ledger spirit)."""
        roots = self.head_roots(from_branch)
        if not roots:
            raise KeyError(f"branch {from_branch} ka koi materialized state "
                           "nahi hai abhi")
        if out_path is None:
            out_path = os.path.join(roots[0]["path"],
                                    "picked_" + os.path.basename(member))
        self.eng.extract(roots[0]["root"], member, out_path)
        self._append({"ev": "cherry", "from": from_branch, "member": member,
                      "into": out_path, "ts": _now()})
        return out_path

    # ------------------------------------------------------------------ map
    def branch_map(self) -> str:
        lines = [f"MULTIVERSE MAP (active: {self.active()})"]
        for b in self.branches():
            h = self.head(b["name"])
            head_txt = f"head {h['ts']}" if h else "(base state)"
            extra = f"  {b['label']}" if b.get("label") else ""
            lines.append(f"  {b['name']} <- {b['parent']}  "
                         f"seed={b['seed']} [{b['tier']}]  {head_txt}{extra}")
        for e in self._events():
            if e["ev"] == "cherry":
                lines.append(f"  cherry: {e['member']} (from {e['from']}) "
                             "-> " + e["into"])
        return "\n".join(lines)


def selftest(tmpdir) -> dict:
    """Multiverse invariants on a scratch vault + scratch work dir."""
    from store import Vault
    from snapshot import Engine

    eng = Engine(Vault(os.path.join(tmpdir, "vault")))
    work = os.path.join(tmpdir, "work")
    os.makedirs(work)
    doc = os.path.join(work, "doc.txt")
    with open(doc, "w", encoding="utf-8") as f:
        f.write("PRIME STATE\n" * 30)
    eng.snapshot([work], "prime day", branch="Prime")

    mv = Multiverse(eng)
    assert mv.active() == "Prime"
    ev = mv.create("WhatIf", label="test fork")
    assert ev["seed"].startswith("Q-") and ev["tier"], "quantum seed required"
    try:
        mv.create("Prime")
        raise AssertionError("reserved name must be rejected")
    except ValueError:
        pass

    mv.switch("WhatIf", watched_paths=[work])       # base state materialize
    assert mv.active() == "WhatIf"
    with open(doc, "a", encoding="utf-8") as f:
        f.write("WHATIF ONLY LINE\n")
    eng.snapshot([work], "whatif edit", branch="WhatIf")

    mv.switch("Prime", watched_paths=[work])        # timeline jump back
    content = open(doc, encoding="utf-8").read()
    assert "WHATIF ONLY" not in content, "timeline switch leaked branch state"
    assert mv.active() == "Prime"

    picked = mv.cherry_pick("WhatIf", "doc.txt")    # borrow across timelines
    assert "WHATIF ONLY" in open(picked, encoding="utf-8").read()

    return {"branches": [b["name"] for b in mv.branches()],
            "switch_back_clean": True,
            "cherry_pick": os.path.basename(picked),
            "seed": ev["seed"], "tier": ev["tier"]}


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        print(json.dumps(selftest(td), indent=1))
        print("MULTIVERSE SELFTEST: PASS")
