"""ChronoVault 2.0 — public keyless registry loader."""
from __future__ import annotations

import json
import random
from typing import Iterable

from .paths import REGISTRY_PATH


class Registry:
    def __init__(self, path: str = REGISTRY_PATH):
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        self.meta = doc["meta"]
        self.endpoints = doc["endpoints"]
        self.by_id = {e["id"]: e for e in self.endpoints}
        self.by_cat: dict[str, list] = {}
        for e in self.endpoints:
            self.by_cat.setdefault(e["category"], []).append(e)

    @property
    def total(self) -> int:
        return len(self.endpoints)

    def get(self, eid: str):
        return self.by_id.get(eid)

    def category(self, cat: str) -> list:
        return self.by_cat.get(cat, [])

    def search(self, q: str = "", category: str = "", limit: int = 40,
               offset: int = 0) -> list:
        q = (q or "").strip().lower()
        out = []
        skipped = 0
        for e in self.endpoints:
            if category and e["category"] != category:
                continue
            if q:
                hay = " ".join([
                    e["id"], e["category"], e.get("docs", ""),
                    " ".join(e.get("tags", [])), e["url"],
                ]).lower()
                if q not in hay:
                    continue
            if skipped < max(0, offset):
                skipped += 1
                continue
            out.append(e)
            if len(out) >= limit:
                break
        return out

    def sample(self, category: str = "", n: int = 5, seed: int | None = None) -> list:
        pool = self.category(category) if category else list(self.endpoints)
        rnd = random.Random(seed)
        return rnd.sample(pool, min(n, len(pool)))

    def ids(self, prefix: str = "") -> Iterable[str]:
        for e in self.endpoints:
            if e["id"].startswith(prefix):
                yield e["id"]

    def stats(self) -> dict:
        return {
            "total": self.total,
            "categories": self.meta.get("categories", {}),
            "generated_at": self.meta.get("generated_at"),
            "registry": REGISTRY_PATH,
        }
