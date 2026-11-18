"""
ChronoVault - MULTIVERSE DEMO (branching timelines, real vault)
===============================================================
Full timeline-jump experience on D:\\Time Machine\\Demo + real Vault:
  1. Prime stable state        -> snapshot on Prime
  2. FORK                      -> "WhatIf-Risky" timeline (quantum seed)
  3. JUMP to WhatIf-Risky      -> risky edits live ONLY there
  4. JUMP back to Prime        -> risky content GONE (materialized state)
  5. CHERRY-PICK               -> borrow one file from the risky timeline
CLI se khelo: python engine\\tv.py branch map / list / switch <name>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "fluxcore"))
from store import Vault        # noqa: E402
from snapshot import Engine    # noqa: E402
from multiverse import Multiverse  # noqa: E402

ROOT = r"D:\Time Machine"
VAULT = os.path.join(ROOT, "Vault")
DEMO = os.path.join(ROOT, "Demo")
os.makedirs(DEMO, exist_ok=True)

eng = Engine(Vault(VAULT))
mv = Multiverse(eng)
story = os.path.join(DEMO, "story.txt")

print("=" * 62)
print("CHRONOVAULT MULTIVERSE DEMO")
print("=" * 62)

# ---------------------------------------------------- 1) Prime stable state
with open(story, "w", encoding="utf-8") as f:
    f.write("PRIME TIMELINE: sab kuch theek chal raha hai.\n" * 15)
s_prime = eng.snapshot([DEMO], "Prime stable state", branch="Prime")
print("[1] Prime snap:", s_prime["ts"])

# --------------------------------------------- 2) FORK: WhatIf-Risky (seed)
ev = mv.create("WhatIf-Risky", label="kya ho agar risky edit karein?")
print("[2] FORK:", ev["name"], "<-", ev["parent"],
      "| seed", ev["seed"], "|", ev["tier"])

# ------------------------------------------------- 3) JUMP to the timeline
rep = mv.switch("WhatIf-Risky", watched_paths=[DEMO])
print("[3] SWITCH:", rep["from"], "->", rep["to"],
      "| active:", mv.active())

# ------------------------------------- 4) risky edits live ONLY on WhatIf
with open(story, "a", encoding="utf-8") as f:
    f.write("RISKY EXPERIMENT LINE - sirf is timeline pe exist karti hai\n")
risky = os.path.join(DEMO, "risky_experiment.txt")
with open(risky, "w", encoding="utf-8") as f:
    f.write("Ye file risky timeline ki hai.\n")
s_risky = eng.snapshot([DEMO], "risky edit on WhatIf",
                       branch="WhatIf-Risky")
print("[4] WhatIf snap:", s_risky["ts"])

# ---------------------------------------------------- 5) JUMP back: Prime
rep = mv.switch("Prime", watched_paths=[DEMO])
content = open(story, encoding="utf-8").read()
clean = "RISKY EXPERIMENT LINE" not in content
print("[5] SWITCH BACK:", rep["from"], "->", rep["to"])
print("    story.txt se risky line GAYAB:", clean)
print("    SAFE mode - ye live files Prime pe nahi the (chhode gaye):",
      rep["extra_live_left"])

# --------------------------------------- 6) cherry-pick across timelines
picked = mv.cherry_pick("WhatIf-Risky", "story.txt",
                        os.path.join(DEMO, "picked_risky_story.txt"))
pk = open(picked, encoding="utf-8").read()
print("[6] CHERRY-PICK:", picked)
print("    risky content file me aa gaya:",
      "RISKY EXPERIMENT LINE" in pk)

# --------------------------------------------------------------- 7) map
print(mv.branch_map())
print("=" * 62)
ok = clean and mv.active() == "Prime"
print("MULTIVERSE CHECKS:", "PASS" if ok else "FAIL")
print("MILESTONE: branching timelines LIVE - past se nayi timeline ban sakti hai")
