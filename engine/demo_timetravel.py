"""
ChronoVault — END-TO-END TIME TRAVEL DEMO (real files, real vault)
=================================================================
Runs the full experience on D:\\Time Machine\\Demo:
  create files -> SNAP 1 -> time passes, edits happen -> SNAP 2
  -> diff between days -> TIME TRAVEL: pull Day-1 file back out
After this, play with the CLI:
  python engine\\tv.py list / travel 1 / diff 1 2 / restore 1 story.txt
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "fluxcore"))
from store import Vault        # noqa: E402
from snapshot import Engine    # noqa: E402

ROOT = r"D:\Time Machine"
VAULT = os.path.join(ROOT, "Vault")
DEMO = os.path.join(ROOT, "Demo")
os.makedirs(DEMO, exist_ok=True)
eng = Engine(Vault(VAULT))

print("=" * 62)
print("CHRONOVAULT TIME TRAVEL DEMO")
print("=" * 62)

# ---------------------------------------------------------- Day 1: files born
story = os.path.join(DEMO, "story.txt")
with open(story, "w", encoding="utf-8") as f:
    f.write("Ek zamana tha jab files ke paas sirf ek version hota tha...\n" * 20)
plan = os.path.join(DEMO, "plan.md")
with open(plan, "w", encoding="utf-8") as f:
    f.write("# Time Machine Plan\n\n- [x] Vault\n- [ ] Oracle\n")

s1 = eng.snapshot([DEMO], "Day 1: files paida hue")
print("[SNAP 1]", s1["ts"], "-", s1["label"])
time.sleep(1.1)  # time actually passes (distinct mtimes/timestamps)

# ------------------------------------------------- Day 2: zindagi badal gayi
with open(story, "a", encoding="utf-8") as f:
    f.write("\nNaya chapter: version 2 me hum time travel kar sakte hain!\n")
with open(plan, "w", encoding="utf-8") as f:
    f.write("# Time Machine Plan\n\n- [x] Vault\n- [x] Oracle\n"
            "- [x] Quantum\n- [x] Multiverse\n")

s2 = eng.snapshot([DEMO], "Day 2: edits ho gaye")
print("[SNAP 2]", s2["ts"], "-", s2["label"])

# ------------------------------------------------------------------- diff
d = eng.diff(s1["roots"][0]["root"], s2["roots"][0]["root"])
print("[DIFF Day1 -> Day2]")
for kind, sym in [("added", "+"), ("changed", "~"), ("removed", "-")]:
    for p in d[kind]:
        print(f"   {sym} {p}")

# --------------------------------------------- TIME TRAVEL: Day 1 se wapis
out = eng.extract(s1["roots"][0]["root"], "story.txt",
                  os.path.join(ROOT, "restored_story_DAY1.txt"))
with open(out, encoding="utf-8") as f:
    content = f.read()
time_travel_ok = "version 2" not in content and "Ek zamana tha" in content
print(f"[TIME TRAVEL] story.txt (Day-1 state) -> {out}")
print(f"[VERIFY] Day-1 content, v2 line NAHI hai: {time_travel_ok}")

# ------------------------------------------------------------- timeline
print("[TIMELINE]")
for i, s in enumerate(eng.snapshots(), 1):
    print(f"   #{i}  {s['ts']}  {s['label']}")

vstats = eng.stats()["vault"]
print(f"[VAULT] {vstats['chunks']} chunks, {vstats['mb']} MB — "
      f"dedup: sirf naya content store hota hai")
print("=" * 62)
print("MILESTONE: Phase 1 core COMPLETE — time machine ka dil dhadak raha hai")
