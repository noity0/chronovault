"""
ChronoVault FluxCore — Snapshot Engine (tree manifests + time scrub)
====================================================================
git-style hash trees over the Vault:
  file object  = {"c":[chunk hashes], "s":size}      -> vault hash
  dir  object  = {"e":{name: {type,hash,size,mtime}}} -> vault hash (sorted, canonical)
  snapshot     = {"root": dir_hash, "ts": iso, "label": str, "paths": [watched roots]}
Property: UNCHANGED SUBTREES SHARE THE SAME HASH -> diff is O(divergence),
and identical snapshots cost ZERO new bytes. Time scrub = pick snapshot, walk tree.
"""
import fnmatch
import json
import os
from datetime import datetime, timezone

from chunker import chunk_data, MIN_SIZE
from store import Vault

DEFAULT_EXCLUDES = ["node_modules", ".git", "__pycache__", "*.tmp", "*.log",
                    "$RECYCLE.BIN", "System Volume Information", ".venv",
                    "Desktop.ini", "thumbs.db", "Thumbs.db"]


def canon(obj) -> bytes:
    """Deterministic encoding — same structure always -> same hash."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


class Engine:
    def __init__(self, vault: Vault, excludes=None):
        self.v = vault
        self.excludes = list(excludes if excludes is not None else DEFAULT_EXCLUDES)
        self.snaplog = os.path.join(vault.root, "snapshots.jsonl")

    # ------------------------------------------------------------- helpers
    def _excluded(self, name: str) -> bool:
        return any(fnmatch.fnmatch(name, pat) or name == pat for pat in self.excludes)

    # ------------------------------------------------------------- capture
    def _file_object(self, path: str) -> dict:
        with open(path, "rb") as f:
            data = f.read()
        if len(data) <= MIN_SIZE:
            chunk_list = [self.v.put(data)]
        else:
            chunk_list = [self.v.put(c) for c in chunk_data(data)]
        return {"c": chunk_list, "s": len(data)}

    def scan(self, path: str) -> dict:
        """Recursively hash a directory into tree objects (stored in Vault)."""
        path = os.path.abspath(path)
        entries = {}
        try:
            names = sorted(os.listdir(path))
        except OSError as ex:
            return {"e": {}, "err": repr(ex)[:80]}
        for name in names:
            if self._excluded(name):
                continue
            full = os.path.join(path, name)
            if os.path.isdir(full):
                entries[name] = {"type": "dir", **self.scan(full)}
            elif os.path.isfile(full):
                fo = self._file_object(full)
                entries[name] = {"type": "file", "hash": self.v.put(canon(fo)),
                                 "size": fo["s"],
                                 "mtime": os.path.getmtime(full)}
        tree = {"e": entries}
        tree["hash"] = self.v.put(canon(tree))
        return tree

    # ---------------------------------------------------------- snapshots
    def snapshot(self, paths, label: str = "", branch: str = "Prime") -> dict:
        paths = [os.path.abspath(p) for p in paths]
        snap = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "label": label,
            "branch": branch,
            "roots": [{"path": p, "root": self.scan(p)["hash"]} for p in paths],
        }
        snap["id"] = self.v.put(canon({"ts": snap["ts"], "roots": snap["roots"],
                                       "label": label, "branch": branch}))
        with open(self.snaplog, "a", encoding="utf-8") as f:
            f.write(json.dumps(snap, ensure_ascii=False) + "\n")
        return snap

    def snapshots(self) -> list:
        if not os.path.exists(self.snaplog):
            return []
        with open(self.snaplog, "r", encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]

    def load_tree(self, root_hash: str) -> dict:
        return json.loads(self.v.get(root_hash).decode("utf-8"))

    # ---------------------------------------------------------------- diff
    def diff(self, hash_a: str, hash_b: str, prefix: str = "") -> dict:
        """Recursive tree diff, pruned by hash equality (O(divergence))."""
        out = {"added": [], "removed": [], "changed": []}
        ta, tb = self.load_tree(hash_a), self.load_tree(hash_b)
        ea, eb = ta["e"], tb["e"]
        for name, ent_b in eb.items():
            ent_a = ea.get(name)
            p = prefix + name
            if ent_a is None:
                out["added"].append(p)
            elif ent_a["hash"] != ent_b["hash"]:
                if ent_a["type"] == "dir" and ent_b["type"] == "dir":
                    sub = self.diff(ent_a["hash"], ent_b["hash"], p + "\\")
                    for k in out:
                        out[k] += sub[k]
                else:
                    out["changed"].append(p)
        for name, ent_a in ea.items():
            if name not in eb:
                out["removed"].append(prefix + name)
        return out

    # ------------------------------------------------------------- restore
    def read_file(self, file_hash: str) -> bytes:
        fo = json.loads(self.v.get(file_hash).decode("utf-8"))
        return b"".join(self.v.get(c) for c in fo["c"])

    def restore_tree(self, root_hash: str, dest: str) -> dict:
        """Materialize a snapshot tree into dest (SAFE mode: live files that
        are NOT in the snapshot are left untouched and reported).
        Safety contract: caller takes an ANCHOR snapshot first."""
        tree = self.load_tree(root_hash)
        report = {"written": 0, "extra_live_left": []}
        os.makedirs(dest, exist_ok=True)
        live = set(os.listdir(dest))
        written = set()
        self._walk_restore(tree, dest, report, written)
        report["extra_live_left"] = sorted(live - written)
        return report

    def _walk_restore(self, tree, cur_dest, report, written):
        for name, ent in tree["e"].items():
            target = os.path.join(cur_dest, name)
            written.add(name)
            if ent["type"] == "dir":
                os.makedirs(target, exist_ok=True)
                self._walk_restore(self.load_tree(ent["hash"]),
                                   target, report, written)
            else:
                with open(target, "wb") as f:
                    f.write(self.read_file(ent["hash"]))
                report["written"] += 1

    def extract(self, root_hash: str, member: str, out_path: str) -> str:
        """Pull one file as it existed at that snapshot — time travel, single file."""
        cur = self.load_tree(root_hash)
        parts = member.replace("/", "\\").split("\\")
        for i, part in enumerate(parts):
            ent = cur["e"].get(part)
            if ent is None:
                raise KeyError(f"not in this snapshot: {part}")
            if i == len(parts) - 1 and ent["type"] == "file":
                os.makedirs(os.path.dirname(os.path.abspath(out_path)),
                            exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(self.read_file(ent["hash"]))
                return out_path
            cur = self.load_tree(ent["hash"])
        raise KeyError(f"{member} is not a file in this snapshot")

    # --------------------------------------------------------------- stats
    def stats(self) -> dict:
        snaps = self.snapshots()
        return {"snapshots": len(snaps), "vault": self.v.stats()}


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as vault_dir, \
         tempfile.TemporaryDirectory() as work_dir:
        eng = Engine(Vault(vault_dir))
        doc = os.path.join(work_dir, "notes.txt")
        with open(doc, "w", encoding="utf-8") as f:
            f.write("version ONE of my notes\n" * 50)
        s1 = eng.snapshot([work_dir], "before edit")
        with open(doc, "a", encoding="utf-8") as f:
            f.write("version TWO line added later\n")
        s2 = eng.snapshot([work_dir], "after edit")
        d = eng.diff(s1["roots"][0]["root"], s2["roots"][0]["root"])
        print("DIFF:", d)
        out = eng.extract(s1["roots"][0]["root"], "notes.txt",
                          os.path.join(work_dir, "restored.txt"))
        with open(out, "r", encoding="utf-8") as f:
            restored = f.read()
        print("TIME TRAVEL OK:", restored.endswith("version TWO line added later\n") is False
              and restored.startswith("version ONE"))
        print("STATS:", eng.stats())
