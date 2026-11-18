"""ChronoVault 2.0 — cockpit UI loader (single local HTML file, no CDN)."""
from __future__ import annotations

import os


def render() -> str:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "cockpit.html")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
