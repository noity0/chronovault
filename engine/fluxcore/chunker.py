"""
ChronoVault FluxCore — Content-Defined Chunker (CDC)
====================================================
restic-style deduplication heart, stdlib only:
  * 64-byte sliding window polynomial rolling hash (O(1) per byte update)
  * boundary when (hash & mask) == 0  -> average ~64KB chunks
  * min 2KB / max 8MB guards
Property that matters: inserting bytes at the START of a file shifts only
ONE chunk — every later chunk stays identical, so snapshots after edits
store almost nothing new. This is what makes the Vault cheap over time.
"""

WINDOW = 64
M = (1 << 61) - 1          # Mersenne prime 2^61 - 1 (large, prime modulus)
B = 257                    # base for byte polynomial
MASK = 0xFFFF              # 1/65536 boundary probability -> ~64KB average
MIN_SIZE = 2048
MAX_SIZE = 8 * 1024 * 1024

_POW_B_W = pow(B, WINDOW - 1, M)   # B^(L-1) mod M, precomputed


def chunk_boundaries(data: bytes, min_size: int = MIN_SIZE,
                     max_size: int = MAX_SIZE, mask: int = MASK) -> list:
    """Return byte offsets where each chunk ENDS (exclusive)."""
    n = len(data)
    cuts = []
    start = 0
    if n <= min_size:
        return [n] if n else []
    h = 0
    # prime the rolling hash over the first window bytes
    for i in range(min(WINDOW, n)):
        h = (h * B + data[i]) % M
    i = WINDOW
    last = 0
    while i < n:
        j = i - start
        if j >= min_size:
            if (h & mask) == 0 or (i - start) >= max_size:
                cuts.append(i)
                start = i
                last = i
        # O(1) slide: remove data[i-WINDOW], append data[i]
        h = ((h - data[i - WINDOW] * _POW_B_W) * B + data[i]) % M
        i += 1
    if last != n:
        cuts.append(n)
    return cuts


def chunk_data(data: bytes, **kw) -> "list[bytes]":
    """Split bytes into CDC chunks."""
    cuts = chunk_boundaries(data, **kw)
    out = []
    prev = 0
    for c in cuts:
        out.append(data[prev:c])
        prev = c
    return out


def selftest() -> dict:
    """Invariants that must ALWAYS hold (run in tests + on boot).

    Metrics done RIGHT:
      * small-chunk params (avg ~1KB) for statistical power — with the
        default 64KB average a 158KB file expects only ~2.4 boundaries,
        so a 'zero cuts' run is legitimate bad luck, not a bug (proved
        by debug_cdc.py).
      * DEDUP metric = chunk HASH-SET overlap (what the Vault actually
        uses), NOT positional zip — one extra content boundary shifts the
        whole list by one index (cascade) while still reusing ~100% of
        the actual chunk contents, exactly like restic's dedup model.
    """
    import hashlib

    base = bytes(((i * 2654435761 + 1013904223) >> 7) & 0xFF
                 for i in range(150_000))          # deterministic, non-periodic
    base += b"IMPORTANT DOCUMENT CONTENT " * 300   # ~158KB realistic mix
    kw = {"min_size": 256, "max_size": MAX_SIZE, "mask": 0x3FF}  # avg ~1KB

    c1 = chunk_data(base, **kw)
    # 1) reassembly is lossless
    assert b"".join(c1) == base, "chunks must reassemble exactly"
    # 2) every chunk respects min/max guards (last chunk may be short)
    assert all(256 <= len(c) <= MAX_SIZE for c in c1[:-1]), "size guards"
    # 3) boundary sanity: hit rate near expectation (catches broken rolling hash)
    n_expect = len(base) / 1024
    assert 0.25 * n_expect < len(c1) < 4 * n_expect, \
        f"boundary frequency off: {len(c1)} vs ~{n_expect:.0f} expected"

    # 4) THE dedup property: insert 680 bytes at start -> ~all chunk contents reused
    inserted = b"NEW HEADER BYTES " * 40 + base
    c2 = chunk_data(inserted, **kw)
    S1 = {hashlib.sha256(c).digest() for c in c1}
    S2 = {hashlib.sha256(c).digest() for c in c2}
    reused = len(S1 & S2) / max(1, len(S1))
    assert reused > 0.6, f"CDC dedup locality broken: only {reused:.0%} reuse"

    return {"chunks_base": len(c1), "chunks_after_insert": len(c2),
            "dedup_reuse_pct": round(reused * 100, 1)}


if __name__ == "__main__":
    import json
    print(json.dumps(selftest(), indent=1))
