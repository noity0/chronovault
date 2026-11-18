"""ChronoVault 2.0 — HTTP layer: cache, TLS fallback, health, parallel fetch.

Design goals:
  * never leave the user waiting forever (hard timeout)
  * work behind corporate TLS interception (retry unverified, mark it)
  * cache aggressively (offline-first)
  * keep honest health statistics per endpoint
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import sqlite3
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from .paths import CACHE_DIR, DB_PATH, HEALTH_PATH, UA, ensure_dirs

ensure_dirs()

_LOCK = threading.RLock()
_HOST_LOCKS: dict[str, float] = {}
_MEM: dict[str, tuple[float, dict]] = {}
_MEM_TTL = 20.0
MAX_BODY = 2_500_000


@dataclass
class Result:
    ok: bool
    url: str
    status: int | None = None
    data: Any = None
    text: str = ""
    ms: int = 0
    cached: bool = False
    stale: bool = False
    tls_unverified: bool = False
    error: str = ""
    fetched_at: float = field(default_factory=time.time)
    endpoint_id: str = ""

    def brief(self, limit: int = 220) -> str:
        if isinstance(self.data, (dict, list)):
            try:
                s = json.dumps(self.data, ensure_ascii=False)
            except Exception:
                s = str(self.data)
        else:
            s = self.text or str(self.data or "")
        s = " ".join(s.split())
        return s[:limit]


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, timeout=20, check_same_thread=False)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute(
        "CREATE TABLE IF NOT EXISTS http("
        "k TEXT PRIMARY KEY, ts REAL, status INT, ctype TEXT, body BLOB)"
    )
    return con


def _cache_get(key: str):
    with _LOCK:
        con = _db()
        try:
            row = con.execute(
                "SELECT ts,status,ctype,body FROM http WHERE k=?", (key,)
            ).fetchone()
        finally:
            con.close()
    return row


def _cache_put(key: str, status: int, ctype: str, body: bytes) -> None:
    with _LOCK:
        con = _db()
        try:
            con.execute(
                "INSERT OR REPLACE INTO http(k,ts,status,ctype,body) VALUES(?,?,?,?,?)",
                (key, time.time(), status, ctype, sqlite3.Binary(body[:MAX_BODY])),
            )
            con.commit()
        finally:
            con.close()


def _health_update(eid: str, ok: bool, ms: int) -> None:
    if not eid:
        return
    with _LOCK:
        try:
            with open(HEALTH_PATH, "r", encoding="utf-8") as f:
                h = json.load(f)
        except Exception:
            h = {}
        rec = h.get(eid) or {"ok": 0, "fail": 0, "avg_ms": 0}
        if ok:
            n = rec.get("ok", 0) + 1
            rec["avg_ms"] = int((rec.get("avg_ms", 0) * rec.get("ok", 0) + ms) / n)
            rec["ok"] = n
        else:
            rec["fail"] = rec.get("fail", 0) + 1
        rec["last"] = int(time.time())
        h[eid] = rec
        tmp = HEALTH_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(h, f, indent=0)
        os.replace(tmp, HEALTH_PATH)


def _decode_body(raw: bytes, ctype: str) -> str:
    enc = ""
    for part in ctype.split(";"):
        part = part.strip()
        if part.lower().startswith("charset="):
            enc = part.split("=", 1)[1].strip('"\'')
    for candidate in ([enc] if enc else []) + ["utf-8", "utf-8-sig", "latin-1"]:
        try:
            return raw.decode(candidate)
        except Exception:
            continue
    return raw.decode("utf-8", "replace")


def _parse(text: str, ctype: str, kind: str):
    if kind == "binary":
        return None
    if kind in ("text", "xml"):
        return text
    stripped = text.lstrip()
    if kind == "json" or "json" in ctype or stripped[:1] in "{[":
        try:
            return json.loads(text)
        except Exception:
            pass
    return text


def _do_request(url: str, data: bytes | None, headers: dict, timeout: float,
                insecure: bool) -> tuple[int, str, bytes, str]:
    req = urllib.request.Request(url, data=data, headers=headers)
    ctx = ssl._create_unverified_context() if insecure else None
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            raw = r.read(MAX_BODY)
            ctype = r.headers.get("Content-Type", "")
            if r.headers.get("Content-Encoding", "").lower() == "gzip":
                raw = gzip.decompress(raw)
            return r.status, ctype, raw, ""
    except urllib.error.HTTPError as e:
        try:
            raw = e.read(MAX_BODY)
        except Exception:
            raw = b""
        return e.code, e.headers.get("Content-Type", "") if e.headers else "", raw, f"HTTP {e.code}"
    except Exception as e:
        return 0, "", b"", f"{type(e).__name__}: {e}"


def fetch(url: str, params: dict | None = None, *, endpoint_id: str = "",
          ttl: int = 0, timeout: float = 9.0, kind: str = "json",
          method: str = "GET", json_body: dict | None = None,
          headers: dict | None = None, allow_insecure: bool = True) -> Result:
    """Fetch one URL with cache + TLS fallback. Never raises for network errors."""
    if params:
        # fill {{name}} placeholders, keep unknown ones out of the URL
        for k, v in params.items():
            url = url.replace("{{" + k + "}}", urllib.parse.quote(str(v), safe=""))
        url = url.replace("{{", "").replace("}}", "")
    body = None
    hdrs = {
        "User-Agent": UA,
        "Accept": "*/*",
    }
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    if headers:
        hdrs.update(headers)

    key_src = method + "\n" + url + "\n" + (body or b"").decode("utf-8", "ignore")
    key = hashlib.sha256(key_src.encode("utf-8")).hexdigest()

    # memory cache
    now = time.time()
    if ttl > 0:
        with _LOCK:
            hit = _MEM.get(key)
        if hit and now - hit[0] <= min(ttl, _MEM_TTL):
            r = Result(**hit[1])
            r.cached = True
            return r

    # disk cache
    if ttl > 0:
        row = _cache_get(key)
        if row:
            ts, status, ctype, raw = row
            if now - ts <= ttl:
                text = _decode_body(raw, ctype)
                res = Result(True, url, status, _parse(text, ctype, kind), text,
                             ms=0, cached=True, endpoint_id=endpoint_id,
                             fetched_at=ts)
                with _LOCK:
                    _MEM[key] = (now, res.__dict__.copy())
                return res
            stale_row = row
        else:
            stale_row = None
    else:
        stale_row = None

    # polite per-host spacing
    host = urllib.parse.urlsplit(url).netloc
    with _LOCK:
        last = _HOST_LOCKS.get(host, 0.0)
        wait = 0.12 - (now - last)
        if wait > 0:
            time.sleep(min(wait, 0.4))
        _HOST_LOCKS[host] = time.time()

    t0 = time.time()
    status, ctype, raw, err = _do_request(url, body, hdrs, timeout, False)
    # One polite retry for transient gateway/timeout failures (502/503/504).
    if status == 0 or 500 <= status < 600:
        time.sleep(0.3)
        s2, c2, r2, e2 = _do_request(url, body, hdrs, timeout, False)
        if s2 and (status == 0 or s2 < 500):
            status, ctype, raw, err = s2, c2, r2, e2
    insecure = False
    if status == 0 and allow_insecure and any(
        s in err for s in ("CERTIFICATE_VERIFY_FAILED", "SSL", "certificate")
    ):
        status, ctype, raw, err2 = _do_request(url, body, hdrs, timeout, True)
        insecure = status != 0
        if status == 0:
            err = err2
    ms = int((time.time() - t0) * 1000)

    if status == 0:
        if stale_row:
            ts, st, ctype0, raw0 = stale_row
            text = _decode_body(raw0, ctype0)
            return Result(True, url, st, _parse(text, ctype0, kind), text, ms=ms,
                          cached=True, stale=True, error=err,
                          endpoint_id=endpoint_id, fetched_at=ts)
        _health_update(endpoint_id, False, ms)
        return Result(False, url, None, None, "", ms, error=err,
                      endpoint_id=endpoint_id)

    text = _decode_body(raw, ctype)
    data = _parse(text, ctype, kind)
    ok = 200 <= status < 400
    if ttl > 0 and ok:
        _cache_put(key, status, ctype, raw)
        res = Result(True, url, status, data, text, ms=ms,
                     tls_unverified=insecure, endpoint_id=endpoint_id)
        with _LOCK:
            _MEM[key] = (time.time(), res.__dict__.copy())
    _health_update(endpoint_id, ok, ms)
    if not ok:
        return Result(False, url, status, data, text, ms,
                      tls_unverified=insecure,
                      error=f"HTTP {status}", endpoint_id=endpoint_id)
    return Result(True, url, status, data, text, ms=ms,
                  tls_unverified=insecure, endpoint_id=endpoint_id)


def get(eid_or_url: str, params: dict | None = None, *, registry=None,
        ttl: int | None = None, timeout: float = 9.0, kind: str | None = None,
        method: str = "GET", json_body: dict | None = None) -> Result:
    """Resolve a registry id (or URL) and fetch it."""
    if "://" in eid_or_url:
        return fetch(eid_or_url, params, ttl=ttl or 0, timeout=timeout,
                     kind=kind or "json", method=method, json_body=json_body)
    if registry is None:
        from .registry import Registry
        registry = Registry()
    e = registry.get(eid_or_url)
    if not e:
        return Result(False, eid_or_url, error="endpoint not in registry")
    return fetch(e["url"], params, endpoint_id=e["id"],
                 ttl=e.get("cache_s", 0) if ttl is None else ttl,
                 timeout=timeout, kind=kind or e.get("kind", "json"),
                 method=method, json_body=json_body)


def get_many(jobs: list[dict], timeout: float = 9.0, registry=None) -> list[Result]:
    """Parallel fetch. jobs: [{id|url, params, kind, ttl}]."""
    import concurrent.futures as cf
    if not jobs:
        return []
    if registry is None:
        from .registry import Registry
        registry = Registry()

    def one(j):
        return get(j.get("id") or j.get("url"), j.get("params"),
                   registry=registry, ttl=j.get("ttl"), timeout=j.get("timeout", timeout),
                   kind=j.get("kind"), method=j.get("method", "GET"),
                   json_body=j.get("json"))

    with cf.ThreadPoolExecutor(max_workers=min(10, len(jobs))) as ex:
        return list(ex.map(one, jobs))


def health_summary() -> dict:
    try:
        with open(HEALTH_PATH, "r", encoding="utf-8") as f:
            h = json.load(f)
    except Exception:
        h = {}
    ok = sum(v.get("ok", 0) for v in h.values())
    fail = sum(v.get("fail", 0) for v in h.values())
    alive = sum(1 for v in h.values() if v.get("ok", 0) > 0)
    used = len(h)
    return {
        "entries": used, "alive": alive, "requests_ok": ok,
        "requests_fail": fail,
        "success_rate": round(ok / (ok + fail), 3) if ok + fail else None,
        "providers": h,
    }


def clear_cache() -> None:
    with _LOCK:
        con = _db()
        try:
            con.execute("DELETE FROM http")
            con.commit()
        finally:
            con.close()
