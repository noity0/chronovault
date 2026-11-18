"""Cities, countries, currencies, crypto — entity extraction helpers."""
from __future__ import annotations

import os
import re
import sys

from .paths import ENGINE_DIR

sys.path.insert(0, os.path.join(ENGINE_DIR, "providers"))
from registry_data import CITIES  # noqa: E402
from generate_registry_v2 import CITY_ZONES, COUNTRY_NAMES, CURRENCIES  # noqa: E402

CITY_INDEX = {}
for _c in CITIES:
    CITY_INDEX[_c[0].lower()] = _c

CITY_ALIASES = {
    "isb": "Islamabad", "rwp": "Rawalpindi", "lhr": "Lahore", "khi": "Karachi",
    "peshawar": "Peshawar", "quetta": "Quetta", "multan": "Multan",
    "faisalabad": "Faisalabad", "sialkot": "Sialkot", "hyd": "Hyderabad",
    "new delhi": "Delhi", "delhi": "Delhi", "mumbai": "Mumbai",
    "bombay": "Mumbai", "bangalore": "Bengaluru", "bengaluru": "Bengaluru",
    "calcutta": "Kolkata", "kolkata": "Kolkata", "madras": "Chennai",
    "chennai": "Chennai", "dhaka": "Dhaka", "kabul": "Kabul",
    "tehran": "Tehran", "istanbul": "Istanbul", "dubai": "Dubai",
    "abu dhabi": "Abu Dhabi", "riyadh": "Riyadh", "jeddah": "Jeddah",
    "makkah": "Mecca", "mecca": "Mecca", "madinah": "Medina",
    "medina": "Medina", "cairo": "Cairo", "doha": "Doha",
    "kuwait": "Kuwait City", "kuwait city": "Kuwait City", "muscat": "Muscat",
    "london": "London", "paris": "Paris", "berlin": "Berlin",
    "madrid": "Madrid", "rome": "Rome", "moscow": "Moscow",
    "new york": "New York", "nyc": "New York", "los angeles": "Los Angeles",
    "la": "Los Angeles", "chicago": "Chicago", "toronto": "Toronto",
    "sydney": "Sydney", "tokyo": "Tokyo", "beijing": "Beijing",
    "shanghai": "Shanghai", "singapore": "Singapore",
    "kuala lumpur": "Kuala Lumpur", "jakarta": "Jakarta",
    "nairobi": "Nairobi", "johannesburg": "Johannesburg",
    "sao paulo": "Sao Paulo", "buenos aires": "Buenos Aires",
    "mexico city": "Mexico City", "hong kong": "Hong Kong",
    "bangkok": "Bangkok", "seoul": "Seoul", "amsterdam": "Amsterdam",
    "zurich": "Zurich", "vienna": "Vienna", "stockholm": "Stockholm",
    "oslo": "Oslo", "copenhagen": "Copenhagen", "helsinki": "Helsinki",
    "warsaw": "Warsaw", "prague": "Prague", "budapest": "Budapest",
    "athens": "Athens", "lisbon": "Lisbon", "dublin": "Dublin",
    "brussels": "Brussels", "geneva": "Geneva", "colombo": "Colombo",
    "kathmandu": "Kathmandu", "tashkent": "Tashkent", "baku": "Baku",
    "almaty": "Almaty", "manila": "Manila", "hanoi": "Hanoi",
    "taipei": "Taipei", "auckland": "Auckland", "vancouver": "Vancouver",
    "miami": "Miami", "washington": "Washington",
    "san francisco": "San Francisco", "tel aviv": "Tel Aviv",
    "jerusalem": "Jerusalem", "amman": "Amman", "beirut": "Beirut",
    "baghdad": "Baghdad", "damascus": "Damascus", "kyiv": "Kyiv",
    "bucharest": "Bucharest", "belgrade": "Belgrade",
    "sarajevo": "Sarajevo", "reykjavik": "Reykjavik",
}

CITY_ZONE = dict(CITY_ZONES)
DEFAULT_CITY = "Lahore"
CITY_CANON = {c[0].lower(): c[0] for c in CITIES}
for _name_l, _name_c in CITY_CANON.items():
    CITY_ALIASES.setdefault(_name_l, _name_c)

COUNTRY_ALIASES = {
    "pakistan": "PK", "india": "IN", "bangladesh": "BD", "afghanistan": "AF",
    "iran": "IR", "turkey": "TR", "turkiye": "TR", "uae": "AE",
    "emirates": "AE", "saudi arabia": "SA", "saudi": "SA", "qatar": "QA",
    "kuwait": "KW", "oman": "OM", "egypt": "EG", "uk": "GB",
    "england": "GB", "britain": "GB", "united kingdom": "GB",
    "usa": "US", "america": "US", "united states": "US", "canada": "CA",
    "australia": "AU", "japan": "JP", "china": "CN", "singapore": "SG",
    "malaysia": "MY", "indonesia": "ID", "kenya": "KE", "south africa": "ZA",
    "brazil": "BR", "argentina": "AR", "mexico": "MX", "hong kong": "HK",
    "thailand": "TH", "south korea": "KR", "korea": "KR",
    "netherlands": "NL", "switzerland": "CH", "austria": "AT",
    "sweden": "SE", "norway": "NO", "denmark": "DK", "finland": "FI",
    "poland": "PL", "czechia": "CZ", "czech republic": "CZ",
    "hungary": "HU", "greece": "GR", "portugal": "PT", "ireland": "IE",
    "belgium": "BE", "sri lanka": "LK", "nepal": "NP", "uzbekistan": "UZ",
    "azerbaijan": "AZ", "kazakhstan": "KZ", "philippines": "PH",
    "vietnam": "VN", "taiwan": "TW", "new zealand": "NZ", "israel": "IL",
    "jordan": "JO", "lebanon": "LB", "iraq": "IQ", "syria": "SY",
    "ukraine": "UA", "romania": "RO", "serbia": "RS",
    "bosnia": "BA", "iceland": "IS", "nigeria": "NG", "ethiopia": "ET",
    "ghana": "GH", "tanzania": "TZ", "uganda": "UG", "morocco": "MA",
    "tunisia": "TN", "algeria": "DZ",
}
for _code, _name in COUNTRY_NAMES.items():
    COUNTRY_ALIASES.setdefault(_name.lower(), _code)

CURRENCY_META = {
    "USD": ("US Dollar", "$"), "EUR": ("Euro", "€"), "GBP": ("British Pound", "£"),
    "JPY": ("Japanese Yen", "¥"), "CNY": ("Chinese Yuan", "¥"),
    "PKR": ("Pakistani Rupee", "₨"), "INR": ("Indian Rupee", "₹"),
    "AED": ("UAE Dirham", "د.إ"), "SAR": ("Saudi Riyal", "﷼"),
    "CAD": ("Canadian Dollar", "C$"), "AUD": ("Australian Dollar", "A$"),
    "CHF": ("Swiss Franc", "Fr"), "TRY": ("Turkish Lira", "₺"),
    "BDT": ("Bangladeshi Taka", "৳"), "IDR": ("Indonesian Rupiah", "Rp"),
    "MYR": ("Malaysian Ringgit", "RM"), "SGD": ("Singapore Dollar", "S$"),
    "THB": ("Thai Baht", "฿"), "PHP": ("Philippine Peso", "₱"),
    "VND": ("Vietnamese Dong", "₫"), "KRW": ("South Korean Won", "₩"),
    "RUB": ("Russian Ruble", "₽"), "BRL": ("Brazilian Real", "R$"),
    "MXN": ("Mexican Peso", "Mex$"), "ZAR": ("South African Rand", "R"),
    "NGN": ("Nigerian Naira", "₦"), "EGP": ("Egyptian Pound", "E£"),
    "KWD": ("Kuwaiti Dinar", "د.ك"), "QAR": ("Qatari Riyal", "ر.ق"),
    "OMR": ("Omani Rial", "ر.ع."), "BHD": ("Bahraini Dinar", ".د.ب"),
    "JOD": ("Jordanian Dinar", "د.ا"), "ILS": ("Israeli Shekel", "₪"),
    "SEK": ("Swedish Krona", "kr"), "NOK": ("Norwegian Krone", "kr"),
    "DKK": ("Danish Krone", "kr"), "PLN": ("Polish Zloty", "zł"),
    "CZK": ("Czech Koruna", "Kč"), "HUF": ("Hungarian Forint", "Ft"),
    "RON": ("Romanian Leu", "lei"), "UAH": ("Ukrainian Hryvnia", "₴"),
    "KZT": ("Kazakhstani Tenge", "₸"), "LKR": ("Sri Lankan Rupee", "Rs"),
    "NPR": ("Nepalese Rupee", "Rs"), "AFN": ("Afghan Afghani", "؋"),
    "IQD": ("Iraqi Dinar", "ع.د"), "MAD": ("Moroccan Dirham", "د.م."),
    "TND": ("Tunisian Dinar", "د.ت"), "DZD": ("Algerian Dinar", "د.ج"),
    "KES": ("Kenyan Shilling", "KSh"), "ETB": ("Ethiopian Birr", "Br"),
    "GHS": ("Ghanaian Cedi", "₵"), "TZS": ("Tanzanian Shilling", "TSh"),
    "UGX": ("Ugandan Shilling", "USh"), "CLP": ("Chilean Peso", "$"),
    "COP": ("Colombian Peso", "$"), "PEN": ("Peruvian Sol", "S/"),
    "ARS": ("Argentine Peso", "$"), "NZD": ("New Zealand Dollar", "NZ$"),
    "HKD": ("Hong Kong Dollar", "HK$"), "TWD": ("Taiwan Dollar", "NT$"),
}

CURRENCY_WORDS = {
    "dollar": "USD", "dollars": "USD", "usd": "USD", "bucks": "USD",
    "euro": "EUR", "euros": "EUR", "pound": "GBP", "pounds": "GBP",
    "sterling": "GBP", "rupee": "PKR", "rupees": "PKR", "rupay": "PKR",
    "rupya": "PKR", "rupaye": "PKR", "rs": "PKR", "yen": "JPY",
    "yuan": "CNY", "rmb": "CNY", "dirham": "AED", "dirhams": "AED",
    "riyal": "SAR", "riyals": "SAR", "taka": "BDT", "lira": "TRY",
    "ringgit": "MYR", "won": "KRW", "ruble": "RUB", "ruble": "RUB",
    "rand": "ZAR", "naira": "NGN", "dinar": "KWD", "shekel": "ILS",
    "franc": "CHF", "krona": "SEK", "zloty": "PLN", "baht": "THB",
    "peso": "MXN", "dirham": "AED",
}

CRYPTO_ALIASES = {
    "bitcoin": "bitcoin", "btc": "bitcoin", "ethereum": "ethereum",
    "eth": "ethereum", "ether": "ethereum", "solana": "solana", "sol": "solana",
    "bnb": "binancecoin", "binance coin": "binancecoin", "xrp": "ripple",
    "ripple": "ripple", "cardano": "cardano", "ada": "cardano",
    "dogecoin": "dogecoin", "doge": "dogecoin", "polkadot": "polkadot",
    "dot": "polkadot", "tron": "tron", "trx": "tron", "litecoin": "litecoin",
    "ltc": "litecoin", "chainlink": "chainlink", "link": "chainlink",
    "avalanche": "avalanche-2", "avax": "avalanche-2", "polygon": "matic-network",
    "matic": "matic-network", "stellar": "stellar", "xlm": "stellar",
    "monero": "monero", "xmr": "monero", "toncoin": "the-open-network",
    "ton": "the-open-network", "shiba": "shiba-inu", "shib": "shiba-inu",
    "uniswap": "uniswap", "uni": "uniswap", "cosmos": "cosmos",
    "atom": "cosmos", "near": "near",
}

CRYPTO_SYMBOL = {
    "bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "binancecoin": "BNB",
    "ripple": "XRP", "cardano": "ADA", "dogecoin": "DOGE", "polkadot": "DOT",
    "tron": "TRX", "litecoin": "LTC", "chainlink": "LINK",
    "avalanche-2": "AVAX", "matic-network": "MATIC", "stellar": "XLM",
    "monero": "XMR", "the-open-network": "TON", "shiba-inu": "SHIB",
    "uniswap": "UNI", "cosmos": "ATOM", "near": "NEAR",
}

_ALL_CURRENCIES = set(CURRENCIES)


def _word_in(text: str, word: str) -> bool:
    return bool(re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text))


def find_city(text: str):
    t = " " + re.sub(r"[^\w\s-]", " ", text.lower()) + " "
    best = None
    for alias, canonical in CITY_ALIASES.items():
        if _word_in(t, alias):
            if best is None or len(alias) > len(best[0]):
                best = (alias, canonical)
    if not best:
        return None
    return CITY_INDEX.get(best[1].lower())


def city_zone(city: str) -> str:
    return CITY_ZONE.get(city, "UTC")


def city_slug(city: str) -> str:
    return city.lower().replace(" ", "_")


def find_country(text: str) -> str | None:
    t = " " + re.sub(r"[^\w\s-]", " ", text.lower()) + " "
    best = None
    for alias, code in COUNTRY_ALIASES.items():
        if _word_in(t, alias):
            if best is None or len(alias) > len(best[0]):
                best = (alias, code)
    if best:
        return best[1]
    for code in re.findall(r"\b[A-Z]{2}\b", text):
        if code in COUNTRY_NAMES:
            return code
    return None


def find_currencies(text: str) -> list[str]:
    t = " " + re.sub(r"[^\w\s]", " ", text.lower()) + " "
    found: list[tuple[int, str]] = []
    for w, code in CURRENCY_WORDS.items():
        m = re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", t)
        if m:
            found.append((m.start(), code))
    for code in _ALL_CURRENCIES:
        m = re.search(r"(?<!\w)" + code.lower() + r"(?!\w)", t)
        if m:
            found.append((m.start(), code))
    found.sort()
    out = []
    for _, code in found:
        if code not in out:
            out.append(code)
    return out


def find_crypto(text: str) -> str | None:
    t = " " + re.sub(r"[^\w\s-]", " ", text.lower()) + " "
    best = None
    for alias, coin in CRYPTO_ALIASES.items():
        if _word_in(t, alias):
            if best is None or len(alias) > len(best[0]):
                best = (alias, coin)
    return best[1] if best else None
