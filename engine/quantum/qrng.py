"""
ChronoVault Quantum Lab — Real Quantum Randomness (keyless)
===========================================================
Tier 1: ANU QRNG      — REAL quantum photons/vacuum fluctuations (Australia)
Tier 2: random.org    — atmospheric noise (not quantum, honest label)
Tier 3: os.urandom    — CSPRNG (offline fallback, honest label)
Machine ALWAYS reports which tier produced the numbers.
No API keys. Ever. Stdlib only.
"""
import json
import os
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; ChronoVault/1.0; quantum-lab)"}
ANU = "https://qrng.anu.edu.au/API/jsonI.php?length={n}&type={t}"
RANDOM_ORG = ("https://www.random.org/integers/?num={n}&min=0&max=65535"
              "&col=1&base=10&format=plain&rnd=new")


def _get(url, timeout=10):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(500_000)


def quantum_uint(n: int = 16) -> dict:
    """Real quantum random integers (0..65535), with honest tier label."""
    n = max(1, min(int(n), 1024))
    # Tier 1 — ANU quantum
    try:
        data = json.loads(_get(ANU.format(n=n, t="uint16")).decode())
        if data.get("success"):
            return {"tier": "QUANTUM (ANU photon vacuum)", "source": "anu_qrng",
                    "values": data["data"], "length": n}
    except Exception:
        pass
    # Tier 2 — atmospheric noise
    try:
        body = _get(RANDOM_ORG.format(n=n)).decode()
        vals = [int(x) for x in body.split() if x.strip().isdigit()]
        if len(vals) == n:
            return {"tier": "ATMOSPHERIC (random.org)", "source": "random_org",
                    "values": vals, "length": n}
    except Exception:
        pass
    # Tier 3 — CSPRNG (offline, always works)
    raw = os.urandom(2 * n)
    return {"tier": "CSPRNG (os.urandom, offline)", "source": "csprng",
            "values": list(int.from_bytes(raw[i:i + 2], "big") for i in range(0, 2 * n, 2)),
            "length": n}


def quantum_seed(bits: int = 64) -> dict:
    """Quantum-seeded hex string — used to seed Multiverse branches."""
    n = max(1, bits // 16)
    r = quantum_uint(n)
    hexes = [f"{v:04x}" for v in r["values"]]
    r["seed"] = "Q-" + "".join(hexes)[:bits // 4]
    return r


def quantum_branch_id() -> str:
    """Full identity for a new Multiverse timeline."""
    return quantum_seed(64)["seed"]


if __name__ == "__main__":
    print(json.dumps(quantum_uint(8), indent=1)[:300])
    print("BRANCH SEED:", quantum_branch_id())
