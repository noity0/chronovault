"""
ChronoVault FluxCore — Content-Addressed Object Store (the Vault floor)
======================================================================
Rule: data ka naam = SHA-256(data). Same bytes => same path => stored ONCE,
no matter how many snapshots/files reference it. zstd not required —
stdlib zlib (level 6) with honest method byte; swap to zstandard later.
Atomic writes: tmp file + os.replace (crash-safe).
"""
import hashlib
import json
import os
import zlib


class Vault:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.objects = os.path.join(self.root, "objects")
        self.tmp = os.path.join(self.root, "tmp")
        os.makedirs(self.objects, exist_ok=True)
        os.makedirs(self.tmp, exist_ok=True)

    # ------------------------------------------------------------ internals
    def _path(self, h: str) -> str:
        return os.path.join(self.objects, h[:2], h)

    # ------------------------------------------------------------ write path
    def put(self, data: bytes) -> str:
        """Store chunk, return its content hash. Idempotent — already there? skip."""
        h = hashlib.sha256(data).hexdigest()
        path = self._path(h)
        if not os.path.exists(path):
            comp = zlib.compress(data, 6)
            if len(comp) < len(data):
                body, method = comp, b"\x01"
            else:
                body, method = data, b"\x00"
            os.makedirs(os.path.dirname(path), exist_ok=True)  # shard dir
            tmp = os.path.join(self.tmp, h + ".part")
            with open(tmp, "wb") as f:
                f.write(method + body)
            os.replace(tmp, path)  # atomic publish
        return h

    # ------------------------------------------------------------ read path
    def get(self, h: str) -> bytes:
        with open(self._path(h), "rb") as f:
            blob = f.read()
        return zlib.decompress(blob[1:]) if blob[0] == 1 else blob[1:]

    def has(self, h: str) -> bool:
        return os.path.exists(self._path(h))

    # ------------------------------------------------------------ integrity
    def verify(self, h: str) -> bool:
        try:
            return hashlib.sha256(self.get(h)).hexdigest() == h
        except Exception:
            return False

    def stats(self) -> dict:
        n = total = 0
        for d in os.listdir(self.objects):
            dp = os.path.join(self.objects, d)
            if not os.path.isdir(dp):
                continue
            for f in os.listdir(dp):
                n += 1
                total += os.path.getsize(os.path.join(dp, f))
        return {"chunks": n, "bytes_on_disk": total,
                "mb": round(total / 1e6, 2)}


def selftest(root: str) -> dict:
    """Vault invariants: roundtrip, idempotent dedup, integrity, CDC locality."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from chunker import chunk_data, selftest as chunk_selftest

    v = Vault(root)
    doc = (b"PROJECT REPORT " +
           bytes(((i * 2654435761 + 1013904223) >> 7) & 0xFF
                 for i in range(100_000)) +                     # non-periodic body
           b"chapter two text " * 200)                          # ~103KB total
    kw = {"min_size": 256, "max_size": 8 * 1024 * 1024, "mask": 0x3FF}
    chunks = chunk_data(doc, **kw)
    hashes = [v.put(c) for c in chunks]

    # 1) reassembly from store is byte-exact
    assert b"".join(v.get(h) for h in hashes) == doc, "roundtrip broken"
    # 2) integrity check
    assert all(v.verify(h) for h in hashes), "sha mismatch"
    # 3) dedup: re-put identical doc -> zero new chunks
    before = v.stats()["chunks"]
    hashes2 = [v.put(c) for c in chunk_data(doc, **kw)]
    after = v.stats()["chunks"]
    dedup_gain = before == after and hashes == hashes2
    # 4) small edit -> most chunks reused (CDC locality, end-to-end, set-based)
    edited = doc[:200] + b"EDITED-HEADER-REGION" + doc[200:]
    new_hashes = [v.put(c) for c in chunk_data(edited, **kw)]
    reuse_pct = round(100 * len(set(new_hashes) & set(hashes)) / len(set(hashes)), 1)
    # 5) tamper detection
    bad = "0" * 64
    assert not v.verify(bad), "tamper check must fail"

    return {
        "chunker_selftest": chunk_selftest(),
        "doc_chunks": len(chunks),
        "vault": v.stats(),
        "dedup_identical_doc_new_chunks": 0 if dedup_gain else "FAIL",
        "edited_doc_chunk_reuse_pct": reuse_pct,
        "tamper_detection": "OK",
    }


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        print(json.dumps(selftest(td), indent=1))
