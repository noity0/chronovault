"""
ChronoVault — `tv` : the time machine CLI (Phase 1 MVP)
=======================================================
  tv init                     — vault ready karo (D:\\Time Machine\\Vault)
  tv watch <path>             — watched folders add karo
  tv snap [label]             — abhi ka snapshot lo ("time anchor")
  tv list                     — timeline dikhaao
  tv diff <a> <b>             — do time points ka farq
  tv travel <n>               — snapshot #n ka tree browse karo
  tv restore <n> <file>       — us time se file wapis laao (anchor-first!)
  tv stats                    — vault ki halat
Stdlib only. No API keys. Anchor-before-restore hamesha.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "fluxcore"))   # core modules live here
sys.path.insert(0, os.path.join(HERE, "oracle"))     # oracle modules
sys.path.insert(0, os.path.join(HERE, "providers"))  # keyless provider client
from store import Vault                    # noqa: E402
from snapshot import Engine                # noqa: E402
from multiverse import Multiverse          # noqa: E402

CONFIG = os.path.join(HERE, "..", "config.json")


def load_cfg() -> dict:
    with open(CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cfg(cfg: dict) -> None:
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def engine() -> Engine:
    cfg = load_cfg()
    return Engine(Vault(cfg["paths"]["vault"]),
                  excludes=cfg.get("excludes"))


def multiverse() -> Multiverse:
    return Multiverse(engine())


# ------------------------------------------------------------------ commands
def cmd_init(_):
    cfg = load_cfg()
    vault_dir = cfg["paths"]["vault"]
    Vault(vault_dir)  # creates folders
    print(f"[OK] Vault ready: {vault_dir}")
    print("     Ab folders add karo:  tv watch <path>")


def cmd_watch(args):
    cfg = load_cfg()
    p = os.path.abspath(args.path)
    if not os.path.isdir(p):
        print(f"[NO] folder nahi mila: {p}")
        return
    if p not in cfg["watched_paths"]:
        cfg["watched_paths"].append(p)
        save_cfg(cfg)
        print(f"[OK] watching: {p} ({len(cfg['watched_paths'])} folders)")
    else:
        print(f"[..] already watching: {p}")


def cmd_snap(args):
    eng = engine()
    cfg = load_cfg()
    watched = cfg["watched_paths"]
    if not watched:
        print("[NO] koi watched folder nahi. Pehle: tv watch <path>")
        return
    branch = getattr(args, "branch", None) or "Prime"
    snap = eng.snapshot(watched, label=args.label or "", branch=branch)
    v = eng.v.stats()
    print(f"[SNAP #{eng.snapshots().index(snap) + 1}] {snap['ts']}  "
          f"[{branch}]  {snap['label'] or '-'}  "
          f"(vault: {v['chunks']} chunks, {v['mb']} MB)")


def cmd_list(_):
    eng = engine()
    snaps = eng.snapshots()
    if not snaps:
        print("[..] timeline khali hai. tv snap chalao.")
        return
    print(f"TIMELINE ({len(snaps)} snapshots) — sabse purana sabse pehle:")
    for i, s in enumerate(snaps, 1):
        print(f"  #{i:<3} {s['ts']}  {s['label'] or '-'}")


def _resolve(eng, ref: str):
    snaps = eng.snapshots()
    idx = int(ref) - 1 if ref.isdigit() else next(
        (i for i, s in enumerate(snaps) if ref in s["ts"]), None)
    if idx is None or not (0 <= idx < len(snaps)):
        raise SystemExit(f"[NO] snapshot nahi mila: {ref}")
    return snaps[idx], idx


def cmd_diff(args):
    eng = engine()
    sa, ia = _resolve(eng, args.a)
    sb, ib = _resolve(eng, args.b)
    d = eng.diff(sa["roots"][0]["root"], sb["roots"][0]["root"])
    print(f"DIFF  #{ia + 1} ({sa['ts']})  ->  #{ib + 1} ({sb['ts']})")
    for kind, sym in [("added", "+"), ("changed", "~"), ("removed", "-")]:
        for p in d[kind]:
            print(f"  {sym} {p}")
    if not (d["added"] or d["changed"] or d["removed"]):
        print("  (koi farq nahi — identical states)")


def cmd_travel(args):
    eng = engine()
    snap, idx = _resolve(eng, args.n)
    tree = eng.load_tree(snap["roots"][0]["root"])
    print(f"TIME VIEW — snapshot #{idx + 1} ({snap['ts']}) root: "
          f"{snap['roots'][0]['path']}")
    _print_tree(eng, tree, depth=0, max_depth=args.depth)


def _print_tree(eng, tree, depth, max_depth):
    for name, ent in sorted(tree["e"].items()):
        print("    " * depth + ("[D] " if ent["type"] == "dir" else "    ")
              + name + ("" if ent["type"] == "dir" else f"  ({ent['size']} B)"))
        if ent["type"] == "dir" and depth + 1 < max_depth:
            _print_tree(eng, eng.load_tree(ent["hash"]), depth + 1, max_depth)


def cmd_restore(args):
    eng = engine()
    snap, idx = _resolve(eng, args.n)
    root = snap["roots"][0]["root"]
    # ANCHOR-FIRST: current state ko pehle snapshot kar lo (safety!)
    cfg = load_cfg()
    anchor = eng.snapshot(cfg["watched_paths"],
                          label=f"anchor: before restore of #{idx + 1}")
    print(f"[ANCHOR] current state saved as snapshot "
          f"#{eng.snapshots().index(anchor) + 1}")
    out = args.out or os.path.join(os.getcwd(), os.path.basename(args.member))
    try:
        eng.extract(root, args.member, out)
        print(f"[TIME TRAVEL] '{args.member}' (snapshot #{idx + 1}, "
              f"{snap['ts']})  ->  {out}")
    except KeyError as ex:
        print(f"[NO] {ex}")
        print("     members dekhne ke liye: tv travel " + str(idx + 1))


def cmd_stats(_):
    eng = engine()
    print(json.dumps(eng.stats(), indent=2))


# ---------------------------------------------------------------- multiverse
def cmd_branch(args):
    mv = multiverse()
    c = args.bcmd
    if c == "list":
        print(f"ACTIVE TIMELINE: {mv.active()}")
        for b in mv.branches():
            h = mv.head(b["name"])
            head_txt = f"head {h['ts']}" if h else "(base state)"
            print(f"  {b['name']:<18} parent={b['parent']:<12} "
                  f"seed={b['seed']} [{b['tier']}]  {head_txt}")
    elif c == "create":
        ev = mv.create(args.name, from_branch=args.from_branch,
                       label=args.label)
        print(f"[FORK] naya timeline: {ev['name']} <- {ev['parent']}")
        print(f"       quantum seed: {ev['seed']}  ({ev['tier']})")
        print(f"       us par jump karne ke liye: tv branch switch {ev['name']}")
    elif c == "switch":
        rep = mv.switch(args.name)
        if rep["anchor"]:
            print(f"[ANCHOR] outgoing timeline '{rep['from']}' pe current "
                  f"state saved ({rep['anchor']['ts']})")
        print(f"[SWITCH] {rep['from']} -> {rep['to']}  "
              f"({rep['files_written']} files materialize hue)")
        if rep["extra_live_left"]:
            print("[SAFE] ye live files target timeline me nahi the, "
                  "chhode gaye:")
            for p in rep["extra_live_left"]:
                print("   ! " + p)
        print(f"[NOW] active timeline: {mv.active()}")
    elif c == "map":
        print(mv.branch_map())
    elif c == "pick":
        out = mv.cherry_pick(args.branch, args.member, args.out)
        print(f"[CHERRY-PICK] {args.member} ({args.branch} se) -> {out}")


# ------------------------------------------------------------------- oracle
def cmd_oracle(args):
    from ledger import Ledger
    led = Ledger()
    try:
        c = args.ocmd
        if c == "ask":
            _oracle_ask(led, args)
        elif c == "simulate":
            import simulate as sim
            k = args.kind
            if k == "day":
                r = sim.future_weekday(args.args[0])
            elif k == "compound":
                p, rate, yrs = (float(x) for x in args.args[:3])
                r = sim.compound(p, rate, yrs)
            elif k == "emi":
                p, rate, m = (float(x) for x in args.args[:3])
                r = sim.emi(p, rate, int(m))
            else:
                print("[NO] kinds: day <iso-date> | compound <p> <rate> "
                      "<years> | emi <p> <rate> <months>")
                return
            pid = led.add_prophecy(" ".join([k] + args.args), "SIMULATE",
                                   "exact", r["answer"], r["confidence"],
                                   r["badge"], meta=r.get("detail"))
            led.resolve(pid, True, truth=r["answer"])
            print(f"[EXACT] {r['answer']}  (ledger #{pid})")
        elif c == "predict":
            from predict import Predict
            r = Predict(ledger=led).fx(base="USD", quote=args.cur.upper(),
                                       days_ahead=args.days)
            print(f"[PREDICT] {r['answer']}  ({r['confidence']:.0%})")
            print(f"          badge: {r['badge']}")
            print(f"          ensemble: {r['ensemble']}")
            print(f"          ledger #{r['ledger_id']} | due {r['due']}")
            if r.get("probe"):
                pr = r["probe"]
                print(f"          PROBE #{pr['probe_id']} planted @ "
                      f"{pr['when']} | scheduled: {pr['scheduled']['ok']}")
                if not pr["scheduled"]["ok"]:
                    print(f"          note: {pr['scheduled'].get('note')}")
        elif c == "harvest":
            from probe import harvest_now
            out = harvest_now(args.probe_id)
            if out.get("ok"):
                print(f"[TRUTH] harvested: {out.get('value')}")
                if "fulfilled" in out:
                    print(f"        prediction: {out['predicted']}")
                    print(f"        verdict: "
                          f"{'FULFILLED' if out['fulfilled'] else 'VIOLATED'}"
                          f" (confidence was {out['confidence']:.0%})")
            else:
                print(f"[NO] {out.get('error')}")
        elif c == "ledger":
            print(json.dumps(led.stats(), ensure_ascii=False, indent=1))
        elif c == "capsule":
            cid = led.seal_capsule(args.open_date, " ".join(args.message))
            print(f"[CAPSULE] #{cid} sealed — {args.open_date} ko khulega")
    except Exception as ex:
        print(f"[NO] {repr(ex)[:140]}")


def _oracle_ask(led, args):
    from accuracy import route
    import simulate as sim
    q = " ".join(args.question)
    r = sim.answer(q)
    if r:
        pid = led.add_prophecy(q, "SIMULATE", "exact", r["answer"],
                               r["confidence"], r["badge"],
                               meta=r.get("detail"))
        led.resolve(pid, True, truth=r["answer"])
        print(f"[EXACT] {r['answer']}")
        print(f"        badge: {r['badge']}  (ledger #{pid})")
        return
    ql = q.lower()
    future = any(w in ql for w in ("kal", "tomorrow", "future", "hoga",
                                   "hogi", "aane wala"))
    plan = route(ql, "future" if future else "now")
    print(f"[ROUTE] engine: {plan}")
    if any(w in ql for w in ("fx", "rate", "exchange", "dollar", "rupee")):
        print("        FX prediction: tv oracle predict fx <CUR> --days N")
    if plan.startswith("PREDICT") or future:
        print("        PREDICT + PROBE: ensemble prediction + future truth "
              "harvest (Task Scheduler)")
    print(f"        (ye sawal exact-math me fit nahi hua: '{q}')")


def main():
    ap = argparse.ArgumentParser(prog="tv",
                                 description="ChronoVault time machine CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    w = sub.add_parser("watch"); w.add_argument("path"); w.set_defaults(fn=cmd_watch)
    s = sub.add_parser("snap"); s.add_argument("label", nargs="?")
    s.add_argument("--branch", default=None,
                   help="is timeline pe snapshot lo (default Prime)")
    s.set_defaults(fn=cmd_snap)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    d = sub.add_parser("diff"); d.add_argument("a"); d.add_argument("b")
    d.set_defaults(fn=cmd_diff)
    t = sub.add_parser("travel"); t.add_argument("n"); t.add_argument(
        "--depth", type=int, default=2); t.set_defaults(fn=cmd_travel)
    r = sub.add_parser("restore"); r.add_argument("n"); r.add_argument("member")
    r.add_argument("--out", default=None); r.set_defaults(fn=cmd_restore)
    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    b = sub.add_parser("branch", help="multiverse timelines")
    bsub = b.add_subparsers(dest="bcmd", required=True)
    bsub.add_parser("list").set_defaults(fn=cmd_branch, bcmd="list")
    bc = bsub.add_parser("create")
    bc.add_argument("name")
    bc.add_argument("--from", dest="from_branch", default=None)
    bc.add_argument("--label", default="")
    bc.set_defaults(fn=cmd_branch, bcmd="create")
    bsw = bsub.add_parser("switch")
    bsw.add_argument("name")
    bsw.set_defaults(fn=cmd_branch, bcmd="switch")
    bsub.add_parser("map").set_defaults(fn=cmd_branch, bcmd="map")
    bp = bsub.add_parser("pick")
    bp.add_argument("branch")
    bp.add_argument("member")
    bp.add_argument("--out", default=None)
    bp.set_defaults(fn=cmd_branch, bcmd="pick")
    o = sub.add_parser("oracle", help="future travel: simulate/predict/probe")
    osub = o.add_subparsers(dest="ocmd", required=True)
    oa = osub.add_parser("ask")
    oa.add_argument("question", nargs="+")
    oa.set_defaults(fn=cmd_oracle, ocmd="ask")
    os = osub.add_parser("simulate")
    os.add_argument("kind")
    os.add_argument("args", nargs="*")
    os.set_defaults(fn=cmd_oracle, ocmd="simulate")
    op = osub.add_parser("predict")
    op.add_argument("kind", choices=["fx"])
    op.add_argument("cur")
    op.add_argument("--days", type=int, default=1)
    op.set_defaults(fn=cmd_oracle, ocmd="predict")
    ol = osub.add_parser("ledger")
    ol.set_defaults(fn=cmd_oracle, ocmd="ledger")
    oh = osub.add_parser("harvest")
    oh.add_argument("probe_id", type=int)
    oh.set_defaults(fn=cmd_oracle, ocmd="harvest")
    oc = osub.add_parser("capsule")
    oc.add_argument("open_date")
    oc.add_argument("message", nargs="+")
    oc.set_defaults(fn=cmd_oracle, ocmd="capsule")
    args = ap.parse_args()
    try:
        args.fn(args)
    except FileNotFoundError as ex:
        print(f"[NO] {ex} — pehle 'tv init' chalao?")


if __name__ == "__main__":
    main()
