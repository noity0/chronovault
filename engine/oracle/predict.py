"""
ChronoVault Oracle — PREDICT Engine (ensemble + calibration)
=============================================================
Future sawal jahan exact math possible nahi:
  1. ENSEMBLE  — >=3 keyless sources se abhi-ka truth cross-check
  2. MODEL     — honest persistence model (label saaf likha jata hai)
  3. CALIBRATE — confidence ko ledger history se correct kiya jata hai
  4. REGISTER  — prophecy Paradox Ledger me pending status ke saath save
  5. PROBE     — future date pe truth harvest hoke prediction verify hogi
Har prediction ke saath PROVENANCE BADGE lazmi hai (jhoot allowed nahi).
Stdlib only. No API keys. Ever.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                                        # ledger etc
sys.path.insert(0, os.path.join(_HERE, "..", "providers"))       # client
import client as providers_client                                # noqa: E402
from accuracy import (ensemble_confidence, calibration_table,    # noqa: E402
                      calibrated_confidence)
from ledger import Ledger                                        # noqa: E402


def _fx_extractor(quote: str):
    def ex(d):
        if isinstance(d, dict):
            rates = d.get("rates")
            if isinstance(rates, dict) and quote in rates:
                try:
                    return float(rates[quote])
                except (TypeError, ValueError):
                    return None
        return None
    return ex


class Predict:
    def __init__(self, ledger: Ledger = None, providers=None):
        self.led = ledger or Ledger()
        self.p = providers or providers_client.Providers()

    # ------------------------------------------------------------- FX model
    def fx(self, base: str = "USD", quote: str = "EUR", days_ahead: int = 1,
           plant_probe: bool = True) -> dict:
        """Predict FX rate N days ahead via persistence + ensemble consensus.
        Honest: persistence = 'jo rate abhi hai wahi rahega' — ka simple model,
        confidence isi ensemble agreement + calibration se aati hai."""
        base, quote = base.upper(), quote.upper()
        ens = self.p.ensemble("finance", _fx_extractor(quote), n=5, base=base)
        # NOTE: ensemble params (base=...) get() ko jate hain; endpoints jo
        # base nahi lete wo fail honge (honest demotion). Fallback: ek proven
        # finance endpoint.
        if not ens or not ens["values"]:
            r = self.p.get("fx_frank_USD", base=base)
            if r.get("ok"):
                v = _fx_extractor(quote)(r["data"])
                ens = {"sources": [{"id": r["id"], "value": v, "ms": r["ms"]}],
                       "values": [v] if v is not None else [],
                       "distinct": 1 if v is not None else 0,
                       "agreement": 0.0, "verified": False,
                       "consensus": v}
        if not ens or not ens["values"]:
            return {"engine": "PREDICT", "answer": None,
                    "note": "network restricted — abhi sources se FX nahi "
                            "mila (offline honest mode)",
                    "confidence": 0.0, "badge": "UNAVAILABLE"}

        consensus = ens["consensus"]
        disagree = consensus is None
        if disagree:
            vals = sorted(ens["values"])
            consensus = vals[len(vals) // 2]      # median: honest middle
        raw_conf = ensemble_confidence(ens["agreement"], base=0.6) * 0.8
        if disagree:
            raw_conf *= 0.5      # sources disagree -> confidence girna chahiye
        raw_conf = ensemble_confidence(ens["agreement"], base=0.6) * 0.8
        table = calibration_table(self.led.prophecies())
        conf = calibrated_confidence(min(raw_conf, 0.85), table)
        model = "persistence (current consensus rate held forward)"

        due = (datetime.now(timezone.utc) + timedelta(days=days_ahead)) \
            .date().isoformat()
        q = f"{base}/{quote} rate {due} ko kitna hoga?"
        ans = f"{consensus:.4f} {quote} per {base}"
        if disagree:
            ans += (f"  [warning: {len(ens['values'])} sources DISAGREE"
                    " — median likha]")
        model = "persistence (current consensus rate held forward)"
        meta = {"sources": ens["sources"], "model": model,
                "agreement": ens["agreement"], "verified": ens["verified"],
                "all_values": ens["values"]}
        pid = self.led.add_prophecy(q, "PREDICT", "future", ans, conf,
                                    f"PREDICTED ({model}; "
                                    f"{len(ens['values'])} sources)",
                                    due=due, meta=meta)

        out = {"engine": "PREDICT", "question": q, "answer": ans,
               "confidence": conf, "badge": f"PREDICTED ({model})",
               "due": due, "ledger_id": pid, "consensus": consensus,
               "model": model,
               "ensemble": {"sources": len(ens["values"]),
                            "agreement": ens["agreement"],
                            "verified": ens["verified"]}}

        if plant_probe:
            from probe import plant
            out["probe"] = plant(self.led, pid, due, "09:00",
                                 {"kind": "fx_rate", "endpoint":
                                  "fx_frank_USD", "base": base,
                                  "currency": quote,
                                  "expect": round(consensus, 4),
                                  "tol_pct": 0.5})
        return out


if __name__ == "__main__":
    import json
    p = providers_client.Providers()
    print("registry:", p.meta["total_endpoints"], "endpoints")
    r = Predict(providers=p).fx()
    print(json.dumps(r, ensure_ascii=False, indent=1)[:1200])
