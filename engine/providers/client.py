"""
ChronoVault — Keyless Provider Client
=====================================
Fetches from the keyless registry, tracks endpoint health, and provides
cross-check ensembles so answers are verified by multiple independent
sources (accuracy booster #1).
Stdlib only. No API keys. Ever.
"""
import concurrent.futures
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REG_PATH = os.path.join(HERE, "..", "..", "registry.json")
HEALTH_PATH = os.path.join(HERE, "health.json")
UA = ("Mozilla/5.0 (compatible; ChronoVault/1.0; local personal time machine; "
      "offline-first; no telemetry)")
TIMEOUT = 12


class Providers:
    def __init__(self):
        with open(REG_PATH, "r", encoding="utf-8") as f:
            reg = json.load(f)
        self.meta = reg["meta"]
        self.endpoints = reg["endpoints"]
        self.by_id = {e["id"]: e for e in self.endpoints}
        self.by_cat = {}
        for e in self.endpoints:
            self.by_cat.setdefault(e["category"], []).append(e)
        self.health = self._load_health()

    # ------------------------------------------------------------- health
    def _load_health(self):
        try:
            with open(HEALTH_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_health(self):
        try:
            with open(HEALTH_PATH, "w", encoding="utf-8") as f:
                json.dump(self.health, f)
        except Exception:
            pass

    def _h(self, eid):
        return self.health.setdefault(eid, {"ok": 0, "fail": 0, "avg_ms": 0})

    def score(self, eid):
        h = self._h(eid)
        n = h["ok"] + h["fail"]
        if n == 0:
            return self.by_id[eid].get("reliability", 0.7) * 0.9  # unproven penalty
        rate = h["ok"] / n
        return max(0.05, rate * (1.0 - min(h["fail"], 20) / 100.0))

    # ------------------------------------------------------------- fetch
    def _fill(self, url, params):
        """Substitute {{param}} or {param} placeholders with URL-encoded values."""
        import re

        p = dict(params or {})

        def sub(m):
            k = m.group(1)
            if k not in p:
                return m.group(0)
            return urllib.parse.quote(str(p[k]), safe="")

        url = re.sub(r"\{+([a-zA-Z_][a-zA-Z0-9_]*)\}+", sub, url)
        if "{" in url or "}" in url:
            raise ValueError(f"missing params in URL: {url}")
        return url

    def _fetch(self, url, timeout=TIMEOUT):
        """Fetch + parse. On TLS-cert failures (sandbox TLS interception), retry
        once with an unverified context — result honestly tagged tls:'unverified'."""
        import ssl
        headers = {"User-Agent": UA, "Accept": "*/*"}
        t0 = time.time()
        tls = "verified"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read(2_000_000)
        except urllib.error.URLError as ex:
            if "CERTIFICATE_VERIFY_FAILED" not in repr(ex):
                raise
            ctx = ssl._create_unverified_context()  # read-only public data; tagged
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                raw = r.read(2_000_000)
            tls = "unverified (cert check skipped)"
        lat = int((time.time() - t0) * 1000)
        try:
            data = json.loads(raw.decode("utf-8", "replace"))
        except Exception:
            data = raw.decode("utf-8", "replace")[:10000]
        return data, lat, tls

    def get(self, eid, timeout=TIMEOUT, retries=2, **params):
        e = self.by_id.get(eid)
        if not e:
            return {"ok": False, "id": eid, "error": f"unknown endpoint {eid}"}
        last_err = None
        for attempt in range(retries + 1):  # retries absorb transient DNS blips
            try:
                url = self._fill(e["url"], params)
                data, lat, tls = self._fetch(url, timeout)
                h = self._h(eid)
                h["ok"] += 1
                h["avg_ms"] = int((h["avg_ms"] * (h["ok"] - 1) + lat) / h["ok"])
                self._save_health()
                return {"ok": True, "id": eid, "url": url, "data": data,
                        "ms": lat, "tls": tls}
            except (urllib.error.URLError, urllib.error.HTTPError, ValueError,
                    TimeoutError, OSError) as ex:
                last_err = ex
                if attempt < retries:
                    time.sleep(0.6)
        h = self._h(eid)
        h["fail"] += 1
        self._save_health()
        kind = "network_restricted" if _is_net_block(last_err) else "error"
        return {"ok": False, "id": eid, "kind": kind, "error": repr(last_err)[:200]}

    def network_probe(self, test_id="time_wt_UTC", timeout=6):
        """Quick honest check: online providers available or not."""
        r = self.get(test_id, timeout=timeout, retries=0)
        self.network_ok = bool(r.get("ok"))
        return self.network_ok

    # ------------------------------------------------- ensemble (accuracy)
    def best(self, category, n=4):
        pool = self.by_cat.get(category, [])
        return sorted(pool, key=lambda e: self.score(e["id"]), reverse=True)[:n]

    def ensemble(self, category, extractor, n=4, timeout=TIMEOUT, **params):
        """Fetch n best endpoints of a category IN PARALLEL and cross-check.
        extractor: fn(data) -> comparable value (float/str/None)."""
        eps = self.best(category, n)
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=n) as ex:
            futs = {ex.submit(self.get, e["id"], timeout, **params): e for e in eps}
            for fut in concurrent.futures.as_completed(futs):
                r = fut.result()
                if r.get("ok"):
                    try:
                        v = extractor(r["data"])
                    except Exception:
                        v = None
                    results.append({"id": r["id"], "value": v, "ms": r["ms"],
                                    "url": r["url"]})
        vals = [r["value"] for r in results if r["value"] is not None]
        uniq = _unique_values(vals)
        agreement = (len(uniq) == 1 and len(vals) >= 2) and True or \
                    (1 / len(uniq) if uniq else 0.0)
        return {
            "sources": results,
            "values": vals,
            "distinct": len(uniq),
            "agreement": round(float(agreement), 3) if agreement else 0.0,
            "verified": len(uniq) == 1 and len(vals) >= 2,
            "consensus": uniq[0] if len(uniq) == 1 else None,
        }


def _is_net_block(err) -> bool:
    """True when failure looks like a restricted/blocked network (DNS or TLS),
    so the system labels it honestly instead of blaming the endpoint."""
    s = repr(err)
    return any(k in s for k in ("getaddrinfo failed", "Name or service not known",
                                "SSL", "certificate", "unreachable", "timed out"))


def _unique_values(vals):
    out = []
    for v in vals:
        key = json.dumps(v, sort_keys=True, default=str)
        if key not in [json.dumps(o, sort_keys=True, default=str) for o in out]:
            out.append(v)
    return out


if __name__ == "__main__":
    p = Providers()
    print("Registry:", p.meta["total_endpoints"], "keyless endpoints")
    print("Categories:", p.meta["categories"])
    print("Top time endpoints:", [e["id"] for e in p.best("time", 3)])
