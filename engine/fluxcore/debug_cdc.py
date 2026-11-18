"""Debug CDC locality: rolling-hash correctness + boundary alignment."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chunker import (chunk_boundaries, WINDOW, MIN_SIZE, M, B, _POW_B_W)  # noqa

base = bytes(((i * 2654435761 + 1013904223) >> 7) & 0xFF
             for i in range(150_000)) + b"IMPORTANT DOCUMENT CONTENT " * 300
H = b"NEW HEADER BYTES " * 40
ins = H + base


def naive_window_hash(buf: bytes) -> int:
    h = 0
    for b in buf:
        h = (h * B + b) % M
    return h


def check_cuts(data: bytes, cuts: list, name: str):
    bad = 0
    for c in cuts[:-1]:  # last cut is EOF, not content-defined
        wh = naive_window_hash(data[c - WINDOW:c])
        if (wh & 0xFFFF) != 0:
            bad += 1
    print(f"{name}: {len(cuts)} cuts, {bad} cuts FAIL naive-hash criterion")


b1 = chunk_boundaries(base)
b2 = chunk_boundaries(ins)
check_cuts(base, b1, "base")
check_cuts(ins, b2, "ins")
print("cuts base:", b1[:6], "... total", len(b1))
print("cuts ins :", b2[:6], "... total", len(b2))
print("shifted base cuts (+680):", [c + 680 for c in b1[:6]])
print("sizes base:", [b1[0]] + [b1[i] - b1[i - 1] for i in range(1, len(b1))][:5])
print("sizes ins :", [b2[0]] + [b2[i] - b2[i - 1] for i in range(1, len(b2))][:5])
