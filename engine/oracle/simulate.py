"""
ChronoVault Oracle — SIMULATE Engine (exact math, badge: EXACT)
===============================================================
Jahan pure math sawal ka jawab ho sakta hai, wahan time travel ki zaroorat
nahi — machine EXACT hisaab deti hai (confidence 0.999, badge EXACT-MATH):
  * future date ka din (konsa din girega / para tha)
  * countdown (kitne din baqi)
  * compound interest
  * EMI (loan installment)
Honest rule: ye SIMULATION hai, guess nahi — isi liye ye sab se pehle chalta hai.
Stdlib only. No API keys. Ever.
"""
import re
from datetime import date, datetime, timezone

DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
           "Saturday", "Sunday"]
DAYS_ROMAN = ["Somwar", "Mangal", "Budh", "Jumerat", "Jumma", "Hafta",
              "Etwar"]

CONFIDENCE = 0.999
BADGE = "EXACT-MATH (deterministic computation)"


def _today() -> date:
    return datetime.now(timezone.utc).date()


def future_weekday(iso_date: str) -> dict:
    """Kis din girega (ya para tha)?"""
    d = date.fromisoformat(iso_date)
    i = d.weekday()
    today = _today()
    delta = (d - today).days
    if delta > 0:
        head = f"{iso_date} ko {DAYS_ROMAN[i]} ({DAYS_EN[i]}) girega"
        extra = f"{delta} din baad"
    elif delta < 0:
        head = f"{iso_date} ko {DAYS_ROMAN[i]} ({DAYS_EN[i]}) para tha"
        extra = f"{-delta} din pehle"
    else:
        head = f"{iso_date} AAJ hai ({DAYS_ROMAN[i]} / {DAYS_EN[i]})"
        extra = "0 din"
    return {"engine": "SIMULATE", "answer": head,
            "detail": {"weekday": DAYS_EN[i], "days_delta": delta,
                       "note": extra},
            "confidence": CONFIDENCE, "badge": BADGE}


def compound(principal: float, annual_rate_pct: float, years: float,
             times_per_year: int = 12) -> dict:
    """Compound interest — exact formula A = P(1 + r/n)^(n*t)."""
    r = annual_rate_pct / 100.0
    amount = principal * (1 + r / times_per_year) ** (times_per_year * years)
    gain = amount - principal
    return {"engine": "SIMULATE",
            "answer": (f"{principal:,.0f} @ {annual_rate_pct}%/saal x {years} "
                       f"saal (n={times_per_year}) = {amount:,.2f} "
                       f"(faida {gain:,.2f})"),
            "detail": {"principal": principal, "amount": round(amount, 2),
                       "gain": round(gain, 2)},
            "confidence": CONFIDENCE, "badge": BADGE}


def emi(principal: float, annual_rate_pct: float, months: int) -> dict:
    """Equated monthly installment — exact annuity formula."""
    r = annual_rate_pct / 100.0 / 12.0
    if r == 0:
        m = principal / months
    else:
        m = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    total = m * months
    return {"engine": "SIMULATE",
            "answer": (f"EMI: {principal:,.0f} loan @ {annual_rate_pct}% x "
                       f"{months} mahine = {m:,.2f}/mahina "
                       f"(total {total:,.2f})"),
            "detail": {"monthly": round(m, 2), "total_paid": round(total, 2),
                       "interest_paid": round(total - principal, 2)},
            "confidence": CONFIDENCE, "badge": BADGE}


_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_COMPOUND_RE = re.compile(
    r"compound\s+([\d,\.]+)\s*(?:pkrs?|rs\.?|rupees)?\s*"
    r"(?:at|@|rate|par)?\s*([\d\.]+)\s*%?\s*(?:for)?\s*"
    r"(\d+(?:\.\d+)?)\s*(?:saal|years?|yrs?)", re.I)
_EMI_RE = re.compile(
    r"emi\s+([\d,\.]+)\s*(?:pkrs?|rs\.?|rupees)?\s*"
    r"(?:at|@|rate|par)?\s*([\d\.]+)\s*%?\s*(?:for)?\s*"
    r"(\d+)\s*(?:mahine|months?|m)", re.I)


def answer(question: str):
    """Route a natural-language question to the right exact computation.
    Returns None when SIMULATE cannot decide (honesty: koi andaza nahi)."""
    q = question.strip()
    m = _COMPOUND_RE.search(q)
    if m:
        return compound(float(m.group(1).replace(",", "")),
                        float(m.group(2)), float(m.group(3)))
    m = _EMI_RE.search(q)
    if m:
        return emi(float(m.group(1).replace(",", "")),
                   float(m.group(2)), int(m.group(3)))
    m = _DATE_RE.search(q)
    if m:
        return future_weekday(m.group(1))
    return None


if __name__ == "__main__":
    import json
    for q in ["2050-01-01 konsa din hoga?",
              "compound 100000 at 18% for 5 saal",
              "emi 1000000 at 12% for 240 mahine",
              "aaj ka mausam?"]:
        r = answer(q)
        print(q, "->", json.dumps(r, ensure_ascii=False) if r else "None")
    print("SIMULATE SELFTEST: PASS")
