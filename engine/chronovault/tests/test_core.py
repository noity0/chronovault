"""Offline unit tests for ChronoVault 2.0 (no network required)."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_DIR = os.path.dirname(os.path.dirname(TESTS_DIR))
sys.path.insert(0, ENGINE_DIR)

from chronovault import formulas, net, text  # noqa: E402
from chronovault.ask import Chrono  # noqa: E402
from chronovault.forecast import forecast, prepare  # noqa: E402
from chronovault.memory import Memory  # noqa: E402
from chronovault.places import find_city, find_country, find_currencies, find_crypto  # noqa: E402
from chronovault.registry import Registry  # noqa: E402
from chronovault.router import route  # noqa: E402


class TestFormulas(unittest.TestCase):
    def test_weekday_known(self):
        d = date(2026, 11, 18)
        r = formulas.weekday_answer(d)
        self.assertTrue(r["ok"])
        self.assertIn("Wednesday", r["text"])

    def test_parse_date(self):
        self.assertEqual(formulas.parse_date("1 Jan 2050"), date(2050, 1, 1))
        self.assertEqual(formulas.parse_date("18 Nov 2026"), date(2026, 11, 18))
        self.assertIsNone(formulas.parse_date("kuch nahi"))

    def test_countdown_future_past(self):
        fut = date.today() + timedelta(days=10)
        r = formulas.countdown(fut)
        self.assertIn("10", r["text"])
        past = date.today() - timedelta(days=3)
        r2 = formulas.countdown(past)
        self.assertIn("guzar chuki hai", r2["text"])

    def test_compound_matches_formula(self):
        p, r, y = 100000.0, 18.0, 5
        got = formulas.compound(p, r, y)
        expected = p * (1 + r / 100 / 12) ** (12 * y)
        self.assertAlmostEqual(got["amount"], expected, delta=1.0)

    def test_simple_interest(self):
        got = formulas.simple_interest(10000, 10, 2)
        self.assertAlmostEqual(got["interest"], 2000.0, places=2)

    def test_emi_matches_standard_formula(self):
        p, annual, years = 5000000.0, 12.0, 5
        m = int(years * 12)
        r = annual / 100 / 12
        expected = p * r * (1 + r) ** m / ((1 + r) ** m - 1)
        got = formulas.emi(p, annual, years)
        self.assertAlmostEqual(got["emi"], expected, delta=1.0)


class TestRouter(unittest.TestCase):
    CASES = [
        ("1 Jan 2050 konsa din hoga?", "date"),
        ("2050 tak kitne din baqi hain?", "countdown"),
        ("100000 @ 18% 5 saal compound interest", "interest"),
        ("50 lakh ka loan 12% 5 saal EMI", "emi"),
        ("100 dollar to PKR", "fx"),
        ("USD/PKR 30 din baad kitna hoga?", "forecast_fx"),
        ("bitcoin 2027 me kitna hoga?", "forecast_crypto"),
        ("Lahore ka mausam kaisa hai?", "weather"),
        ("Lahore me abhi kitne baje hain?", "time"),
        ("Pakistan me 2026 ki holidays batao", "holiday"),
        ("Japan ki capital kya hai?", "country"),
        ("latest AI news", "news"),
        ("ISS kahan hai abhi", "space"),
        ("aaj ke earthquakes", "space"),
        ("time travel kya hai?", "knowledge"),
        ("Pakistan ka future kya hoga?", "forecast"),
        ("salam", "smalltalk"),
        ("tum kon ho?", "identity"),
        ("time capsule banao: 1 saal baad kholna, bharosa rakho", "capsule"),
    ]

    def test_intents(self):
        for q, kind in self.CASES:
            with self.subTest(q=q):
                it = route(q)
                self.assertEqual(it.kind, kind, f"{q} -> {it.to_dict()}")

    def test_slots(self):
        it = route("100 dollar to PKR")
        self.assertEqual(it.slots.get("from"), "USD")
        self.assertEqual(it.slots.get("to"), "PKR")
        self.assertAlmostEqual(it.slots.get("amount"), 100.0)
        w = route("Lahore ka mausam")
        self.assertEqual(w.slots.get("city"), "Lahore")


class TestForecast(unittest.TestCase):
    def test_linear_series_predicts_trend(self):
        base = date(2026, 1, 1)
        series = [((base + timedelta(days=i)).isoformat(),
                   100.0 + i * 0.4 + (i % 7) * 0.2) for i in range(120)]
        f = forecast(series, 10)
        self.assertIsNotNone(f)
        self.assertGreater(f["predicted"], series[-1][1] - 5)
        self.assertLess(f["predicted"], 100 + 120 * 0.4 + 5)
        self.assertEqual(f["target_date"], (base + timedelta(days=129)).isoformat())
        self.assertLessEqual(f["confidence"], 0.84)
        self.assertGreaterEqual(f["confidence"], 0.24)

    def test_short_series_returns_none(self):
        self.assertIsNone(forecast([("2026-01-01", 1.0)] * 3, 10))

    def test_prepare_dedupes(self):
        xs, ys = prepare([("2026-01-01", 1.0), ("2026-01-01", 2.0),
                          ("2026-01-02", 3.0)])
        self.assertEqual(xs, [0, 1])
        self.assertEqual(ys, [2.0, 3.0])


class TestRegistryAndPlaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = Registry()

    def test_registry_size_and_uniqueness(self):
        self.assertGreaterEqual(self.reg.total, 3900)
        ids = [e["id"] for e in self.reg.endpoints]
        self.assertEqual(len(ids), len(set(ids)))

    def test_search(self):
        rows = self.reg.search("bitcoin", limit=5)
        self.assertTrue(rows)
        self.assertIn("bitcoin", rows[0]["id"].lower())

    def test_categories(self):
        cats = self.reg.stats()["categories"]
        self.assertIn("finance", cats)
        self.assertGreater(cats.get("calendar", 0), 500)

    def test_places(self):
        city = find_city("Lahore ka mausam")
        self.assertIsNotNone(city)
        self.assertEqual(city[0], "Lahore")
        self.assertEqual(find_country("Saudi Arabia"), "SA")
        self.assertIn("USD", find_currencies("100 dollars"))
        self.assertEqual(find_crypto("btc price"), "bitcoin")


class TestText(unittest.TestCase):
    def test_clean_html(self):
        self.assertEqual(text.clean("<b>Salam</b> &amp; salam"), "Salam & salam")

    def test_shorten(self):
        self.assertLessEqual(len(text.shorten("a" * 1000, 80)), 81)

    def test_parse_rss(self):
        xml = """<rss><channel>
          <item><title>One</title><link>http://x/1</link><pubDate>Wed, 18 Nov 2026 10:00:00 GMT</pubDate></item>
          <item><title>Two</title><link>http://x/2</link></item>
        </channel></rss>"""
        items = text.parse_rss(xml)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "One")
        self.assertTrue(items[0]["link"].startswith("http"))


class TestMemoryIsolated(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.join(tempfile.gettempdir(), "chrono_test_memory.db")
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(self.tmp + suffix)
            except OSError:
                pass
        import chronovault.memory as memory
        self._old = memory.DB_PATH
        memory.DB_PATH = self.tmp

    def tearDown(self):
        import chronovault.memory as memory
        memory.DB_PATH = self._old

    def test_record_get_history_stats(self):
        mem = Memory()
        aid = mem.record("test question", {
            "kind": "date", "answer": "Wednesday", "confidence": 0.99,
            "badge": "EXACT-MATH", "evidence": [{"source": "math"}],
            "data": {"weekday": "Wednesday"}, "sources": ["math"],
        }, 42)
        row = mem.get(aid)
        self.assertEqual(row["question"], "test question")
        self.assertEqual(row["kind"], "date")
        self.assertEqual(row["data"]["weekday"], "Wednesday")
        hist = mem.history(10)
        self.assertTrue(any(h["id"] == aid for h in hist))
        st = mem.stats()
        self.assertGreaterEqual(st["answers"], 1)
        mem.feedback(aid, 1, "useful")
        mem.event("test", {"ok": True})


class TestAskExactOffline(unittest.TestCase):
    """The orchestrator itself, but only deterministic math (no network/AI)."""

    def setUp(self):
        self.tmp = os.path.join(tempfile.gettempdir(), "chrono_test_ask.db")
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(self.tmp + suffix)
            except OSError:
                pass
        import chronovault.memory as memory
        self._old = memory.DB_PATH
        memory.DB_PATH = self.tmp

    def tearDown(self):
        import chronovault.memory as memory
        memory.DB_PATH = self._old

    def test_exact_date_pipeline(self):
        ans = Chrono(use_llm=False).ask("1 Jan 2050 konsa din hoga?", ai=False)
        self.assertEqual(ans.badge, "EXACT-MATH")
        self.assertGreaterEqual(ans.confidence, 0.99)
        self.assertIn("Saturday", ans.answer)  # 2050-01-01 is a Saturday
        self.assertGreater(ans.answer_id, 0)

    def test_help_identity(self):
        ans = Chrono(use_llm=False).ask("tum kon ho?", ai=False)
        self.assertEqual(ans.kind, "identity")
        self.assertEqual(ans.badge, "INFO")


class TestNetHealth(unittest.TestCase):
    def test_health_shape(self):
        h = net.health_summary()
        for key in ("entries", "alive", "requests_ok", "requests_fail", "success_rate"):
            self.assertIn(key, h)


if __name__ == "__main__":
    unittest.main()
