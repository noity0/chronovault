"""
ChronoVault Quantum Lab — Shannon Entropy Engine (arrow of time)
================================================================
H = −Σ pᵢ·log₂(pᵢ) — real information theory. Tells how "random" data is.
Uses: chunker tuning (high entropy → skip compression), the Entropy Meter
(thermodynamic graph of your digital life's disorder over time).
Stdlib only.
"""
import collections
import math


def shannon_entropy(data: bytes) -> float:
    """Bits of entropy per byte, 0..8."""
    if not data:
        return 0.0
    counts = collections.Counter(data)
    n = len(counts)
    total = len(data)
    return round(-sum((c / total) * math.log2(c / total) for c in counts.values()), 4)


def classify(entropy: float) -> dict:
    """Practical classification for the chunker/compressor."""
    if entropy < 5.0:
        kind, action = "text-like", "compress (zstd wins)"
    elif entropy < 7.0:
        kind, action = "structured/binary", "compress lightly"
    elif entropy < 7.95:
        kind, action = "already-compressed/media", "store as-is"
    else:
        kind, action = "encrypted/random", "store as-is (dedup still works)"
    return {"entropy": entropy, "kind": kind, "action": action}


def arrow_of_time(entropy_series: list) -> dict:
    """Entropy over successive snapshots — the 'thermodynamic' story of a folder."""
    if len(entropy_series) < 2:
        return {"ok": False, "reason": "need ≥2 samples"}
    diffs = [b - a for a, b in zip(entropy_series, entropy_series[1:])]
    avg = sum(diffs) / len(diffs)
    return {
        "ok": True,
        "trend": "expanding (disorder rising)" if avg > 0.02 else
                 "converging (getting organized)" if avg < -0.02 else
                 "steady state",
        "delta_per_snapshot": round(avg, 5),
        "first": entropy_series[0], "last": entropy_series[-1],
    }


if __name__ == "__main__":
    demo_text = b"the quick brown fox jumps over the lazy dog " * 10
    demo_rand = bytes(range(256)) * 4
    for name, data in [("text", demo_text), ("random", demo_rand)]:
        e = shannon_entropy(data)
        print(name, classify(e))
    print(arrow_of_time([5.2, 5.8, 6.1, 6.4, 7.1]))
