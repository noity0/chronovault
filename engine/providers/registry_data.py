"""
ChronoVault v2 — Registry Data
==============================
Static, real-world data used to expand the keyless provider network into
thousands of concrete endpoint definitions.  Nothing here is an API key:
every URL is a public endpoint (or a localhost AI server the user may run).

Design rule: one definition = one real URL.  Variants (city, country, year,
language, category) are real URL variants, not invented services.
"""

# ---------------------------------------------------------------------------
# Cities: (name, country, lat, lon) — used for weather / air / marine / prayer
# ---------------------------------------------------------------------------
CITIES = [
    ("Lahore", "Pakistan", 31.5497, 74.3436),
    ("Karachi", "Pakistan", 24.8607, 67.0011),
    ("Islamabad", "Pakistan", 33.6844, 73.0479),
    ("Rawalpindi", "Pakistan", 33.5651, 73.0169),
    ("Faisalabad", "Pakistan", 31.4504, 73.1350),
    ("Multan", "Pakistan", 30.1575, 71.5249),
    ("Peshawar", "Pakistan", 34.0151, 71.5249),
    ("Quetta", "Pakistan", 30.1798, 66.9750),
    ("Sialkot", "Pakistan", 32.4945, 74.5229),
    ("Hyderabad", "Pakistan", 25.3960, 68.3578),
    ("Delhi", "India", 28.6139, 77.2090),
    ("Mumbai", "India", 19.0760, 72.8777),
    ("Bengaluru", "India", 12.9716, 77.5946),
    ("Kolkata", "India", 22.5726, 88.3639),
    ("Chennai", "India", 13.0827, 80.2707),
    ("Dhaka", "Bangladesh", 23.8103, 90.4125),
    ("Kabul", "Afghanistan", 34.5553, 69.2075),
    ("Tehran", "Iran", 35.6892, 51.3890),
    ("Istanbul", "Turkey", 41.0082, 28.9784),
    ("Dubai", "United Arab Emirates", 25.2048, 55.2708),
    ("Abu Dhabi", "United Arab Emirates", 24.4539, 54.3773),
    ("Riyadh", "Saudi Arabia", 24.7136, 46.6753),
    ("Jeddah", "Saudi Arabia", 21.4858, 39.1925),
    ("Mecca", "Saudi Arabia", 21.3891, 39.8579),
    ("Medina", "Saudi Arabia", 24.5247, 39.5692),
    ("Cairo", "Egypt", 30.0444, 31.2357),
    ("Doha", "Qatar", 25.2854, 51.5310),
    ("Kuwait City", "Kuwait", 29.3759, 47.9774),
    ("Muscat", "Oman", 23.5880, 58.3829),
    ("London", "United Kingdom", 51.5074, -0.1278),
    ("Paris", "France", 48.8566, 2.3522),
    ("Berlin", "Germany", 52.5200, 13.4050),
    ("Madrid", "Spain", 40.4168, -3.7038),
    ("Rome", "Italy", 41.9028, 12.4964),
    ("Moscow", "Russia", 55.7558, 37.6173),
    ("New York", "United States", 40.7128, -74.0060),
    ("Los Angeles", "United States", 34.0522, -118.2437),
    ("Chicago", "United States", 41.8781, -87.6298),
    ("Toronto", "Canada", 43.6532, -79.3832),
    ("Sydney", "Australia", -33.8688, 151.2093),
    ("Tokyo", "Japan", 35.6762, 139.6503),
    ("Beijing", "China", 39.9042, 116.4074),
    ("Shanghai", "China", 31.2304, 121.4737),
    ("Singapore", "Singapore", 1.3521, 103.8198),
    ("Kuala Lumpur", "Malaysia", 3.1390, 101.6869),
    ("Jakarta", "Indonesia", -6.2088, 106.8456),
    ("Nairobi", "Kenya", -1.2921, 36.8219),
    ("Johannesburg", "South Africa", -26.2041, 28.0473),
    ("Sao Paulo", "Brazil", -23.5505, -46.6333),
    ("Buenos Aires", "Argentina", -34.6037, -58.3816),
    ("Mexico City", "Mexico", 19.4326, -99.1332),
    ("Hong Kong", "Hong Kong", 22.3193, 114.1694),
    ("Bangkok", "Thailand", 13.7563, 100.5018),
    ("Seoul", "South Korea", 37.5665, 126.9780),
    ("Amsterdam", "Netherlands", 52.3676, 4.9041),
    ("Zurich", "Switzerland", 47.3769, 8.5417),
    ("Vienna", "Austria", 48.2082, 16.3738),
    ("Stockholm", "Sweden", 59.3293, 18.0686),
    ("Oslo", "Norway", 59.9139, 10.7522),
    ("Copenhagen", "Denmark", 55.6761, 12.5683),
    ("Helsinki", "Finland", 60.1699, 24.9384),
    ("Warsaw", "Poland", 52.2297, 21.0122),
    ("Prague", "Czechia", 50.0755, 14.4378),
    ("Budapest", "Hungary", 47.4979, 19.0402),
    ("Athens", "Greece", 37.9838, 23.7275),
    ("Lisbon", "Portugal", 38.7223, -9.1393),
    ("Dublin", "Ireland", 53.3498, -6.2603),
    ("Brussels", "Belgium", 50.8503, 4.3517),
    ("Geneva", "Switzerland", 46.2044, 6.1432),
    ("Colombo", "Sri Lanka", 6.9271, 79.8612),
    ("Kathmandu", "Nepal", 27.7172, 85.3240),
    ("Tashkent", "Uzbekistan", 41.2995, 69.2401),
    ("Baku", "Azerbaijan", 40.4093, 49.8671),
    ("Almaty", "Kazakhstan", 43.2220, 76.8512),
    ("Manila", "Philippines", 14.5995, 120.9842),
    ("Hanoi", "Vietnam", 21.0285, 105.8542),
    ("Taipei", "Taiwan", 25.0330, 121.5654),
    ("Auckland", "New Zealand", -36.8485, 174.7633),
    ("Vancouver", "Canada", 49.2827, -123.1207),
    ("Miami", "United States", 25.7617, -80.1918),
    ("Washington", "United States", 38.9072, -77.0369),
    ("San Francisco", "United States", 37.7749, -122.4194),
    ("Tel Aviv", "Israel", 32.0853, 34.7818),
    ("Jerusalem", "Israel", 31.7683, 35.2137),
    ("Amman", "Jordan", 31.9454, 35.9284),
    ("Beirut", "Lebanon", 33.8938, 35.5018),
    ("Baghdad", "Iraq", 33.3152, 44.3661),
    ("Damascus", "Syria", 33.5138, 36.2765),
    ("Kyiv", "Ukraine", 50.4501, 30.5234),
    ("Bucharest", "Romania", 44.4268, 26.1025),
    ("Belgrade", "Serbia", 44.7866, 20.4489),
    ("Sarajevo", "Bosnia and Herzegovina", 43.8563, 18.4131),
    ("Reykjavik", "Iceland", 64.1466, -21.9426),
]

# ---------------------------------------------------------------------------
# ISO country codes (REST Countries alpha endpoint)
# ---------------------------------------------------------------------------
COUNTRY_CODES = """
AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN
BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ
DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL
GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM
JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME
MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP
NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD
SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO
TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW
""".split()

# ---------------------------------------------------------------------------
# World Bank indicators (real codes)
# ---------------------------------------------------------------------------
WB_INDICATORS = [
    "NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD", "SP.POP.TOTL", "SL.UEM.TOTL.ZS",
    "SI.POV.DDAY", "FP.CPI.TOTL.ZG", "BX.KLT.DINV.CD.WD", "NE.EXP.GNFS.ZS",
    "NE.IMP.GNFS.ZS", "SE.XPD.TOTL.GD.ZS", "SH.XPD.CHEX.GD.ZS",
    "EN.ATM.CO2E.PC", "AG.LND.FRST.ZS", "EG.USE.PCAP.KG.OE",
    "IT.NET.USER.ZS", "SP.DYN.LE00.IN", "SL.TLF.CACT.ZS", "GC.DOD.TOTL.GD.ZS",
]
WB_COUNTRIES = ["PK", "IN", "US", "GB", "CN", "JP", "DE", "FR", "AE", "SA",
                "BD", "TR", "ID", "BR", "ZA", "NG", "EG", "CA", "AU", "KR"]

# ---------------------------------------------------------------------------
# Stack Exchange sites (real slugs)
# ---------------------------------------------------------------------------
STACK_SITES = """
stackoverflow superuser serverfault askubuntu math physics chemistry biology
cs cstheory stats datascience ai robotics electronics electrical engineering
mechanics softwareengineering codereview programmers dba security cryptography
reverseengineering webapps webmasters android apple ubuntu windows unix askdifferent
gaming gamedev graphicdesign ux photo video sound music movies scifi literature
history philosophy linguistics english ell spanish french german italian portuguese
russian japanese chinese korean arabic islam judaism christianity hinduism buddhism
travel outdoors fitness health medicalsciences psychology economics money law
politics workplace parenting cooking diy homebrew gardening pets bicycles cars
motorcycles aviation drones space astronomy earthscience geology weather
sustainability opensource devops sre cloud aws azure googlecloud terraform
kubernetes docker git bash powershell vim emacs vi sublime-text notepad regex sql
oracle postgresql mysql sqlserver mongodb redis elasticsearch kafka blockchain
ethereum bitcoin quant algotrading data opendata gis blender 3dprinting woodworking
crafts sewing chess poker boardgames puzzles mathoverflow matheducators
""".split()

# ---------------------------------------------------------------------------
# arXiv categories (real codes)
# ---------------------------------------------------------------------------
ARXIV_CATS = """
cs.AI cs.CL cs.CV cs.LG cs.NE cs.RO cs.SE cs.CR cs.DB cs.DC cs.DS cs.GT cs.HC cs.IR
cs.IT cs.MA cs.MM cs.NI cs.OS cs.PL cs.SC cs.SD cs.SY stat.ML stat.AP stat.CO stat.ME
stat.TH math.OC math.PR math.ST math.NA math.AP math.CO math.DS math.FA math.GR
math.LO math.NT math.RT eess.AS eess.IV eess.SP eess.SY econ.EM econ.GN econ.TH
q-bio.BM q-bio.GN q-bio.NC q-bio.PE q-bio.QM q-fin.CP q-fin.EC q-fin.GN q-fin.PM
q-fin.RM q-fin.ST q-fin.TR astro-ph.CO astro-ph.EP astro-ph.GA astro-ph.HE
astro-ph.IM astro-ph.SR cond-mat.mtrl-sci cond-mat.soft cond-mat.stat-mech
gr-qc hep-ex hep-lat hep-ph hep-th math-ph nlin.AO nlin.CD nucl-ex nucl-th
physics.ao-ph physics.atom-ph physics.bio-ph physics.chem-ph physics.comp-ph
physics.data-an physics.flu-dyn physics.gen-ph physics.geo-ph physics.ins-det
physics.med-ph physics.optics physics.soc-ph physics.space-ph quant-ph
""".split()

# ---------------------------------------------------------------------------
# RSS feeds (real public feeds) — (id, url, category)
# ---------------------------------------------------------------------------
RSS_FEEDS = [
    ("bbc_top", "https://feeds.bbci.co.uk/news/rss.xml", "news"),
    ("bbc_world", "https://feeds.bbci.co.uk/news/world/rss.xml", "world"),
    ("bbc_tech", "https://feeds.bbci.co.uk/news/technology/rss.xml", "tech"),
    ("bbc_science", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "science"),
    ("bbc_business", "https://feeds.bbci.co.uk/news/business/rss.xml", "finance"),
    ("bbc_urdu", "https://feeds.bbci.co.uk/urdu/rss.xml", "news"),
    ("guardian_world", "https://www.theguardian.com/world/rss", "world"),
    ("guardian_tech", "https://www.theguardian.com/uk/technology/rss", "tech"),
    ("guardian_science", "https://www.theguardian.com/science/rss", "science"),
    ("guardian_business", "https://www.theguardian.com/business/rss", "finance"),
    ("nyt_world", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "world"),
    ("nyt_tech", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "tech"),
    ("nyt_science", "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml", "science"),
    ("nyt_business", "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "finance"),
    ("aljazeera_all", "https://www.aljazeera.com/xml/rss/all.xml", "news"),
    ("cnn_world", "http://rss.cnn.com/rss/edition_world.rss", "world"),
    ("cnn_tech", "http://rss.cnn.com/rss/edition_technology.rss", "tech"),
    ("npr_news", "https://feeds.npr.org/1001/rss.xml", "news"),
    ("npr_tech", "https://feeds.npr.org/1019/rss.xml", "tech"),
    ("npr_science", "https://feeds.npr.org/1006/rss.xml", "science"),
    ("dw_all", "https://rss.dw.com/rdf/rss-en-all", "news"),
    ("dw_science", "https://rss.dw.com/rdf/rss-en-sci", "science"),
    ("france24", "https://www.france24.com/en/rss", "world"),
    ("sky_world", "https://feeds.skynews.com/feeds/rss/world.rss", "world"),
    ("sky_tech", "https://feeds.skynews.com/feeds/rss/technology.rss", "tech"),
    ("verge", "https://www.theverge.com/rss/index.xml", "tech"),
    ("ars", "https://feeds.arstechnica.com/arstechnica/index", "tech"),
    ("techcrunch", "https://techcrunch.com/feed/", "tech"),
    ("wired", "https://www.wired.com/feed/rss", "tech"),
    ("hn_front", "https://hnrss.org/frontpage", "tech"),
    ("mit_tr", "https://www.technologyreview.com/feed/", "tech"),
    ("nature", "https://www.nature.com/nature.rss", "science"),
    ("science_news", "https://www.science.org/rss/news_current.xml", "science"),
    ("nasa", "https://www.nasa.gov/rss/dyn/breaking_news.rss", "space"),
    ("esa", "https://www.esa.int/rssfeed/Our_Activities/Space_News", "space"),
    ("dawn_home", "https://www.dawn.com/feeds/home", "news"),
    ("dawn_world", "https://www.dawn.com/feeds/world", "world"),
    ("ary_news", "https://arynews.tv/feed/", "news"),
    ("thenews", "https://www.thenews.com.pk/rss/1/1", "news"),
    ("tribune_home", "https://tribune.com.pk/feed/home", "news"),
    ("samaa", "https://www.samaa.tv/feed/", "news"),
    ("brecorder", "https://www.brecorder.com/feed/", "finance"),
    ("express_pk", "https://www.express.pk/feed/", "news"),
    ("aaj", "https://aaj.tv/feed/", "news"),
    ("jang", "https://jang.com.pk/rss/", "news"),
    ("voa_urdu", "https://www.voanews.com/rss/urdu", "news"),
    ("reddit_technology", "https://www.reddit.com/r/technology/hot.json?limit=10", "tech"),
    ("reddit_programming", "https://www.reddit.com/r/programming/hot.json?limit=10", "tech"),
    ("reddit_science", "https://www.reddit.com/r/science/hot.json?limit=10", "science"),
    ("reddit_worldnews", "https://www.reddit.com/r/worldnews/hot.json?limit=10", "world"),
    ("reddit_pakistan", "https://www.reddit.com/r/pakistan/hot.json?limit=10", "news"),
    ("reddit_artificial", "https://www.reddit.com/r/artificial/hot.json?limit=10", "ai"),
    ("reddit_ml", "https://www.reddit.com/r/MachineLearning/hot.json?limit=10", "ai"),
    ("reddit_localllama", "https://www.reddit.com/r/LocalLLaMA/hot.json?limit=10", "ai"),
    ("reddit_space", "https://www.reddit.com/r/space/hot.json?limit=10", "space"),
    ("reddit_futurology", "https://www.reddit.com/r/Futurology/hot.json?limit=10", "future"),
    ("reddit_crypto", "https://www.reddit.com/r/CryptoCurrency/hot.json?limit=10", "finance"),
    ("reddit_bitcoin", "https://www.reddit.com/r/Bitcoin/hot.json?limit=10", "finance"),
    ("reddit_personalfinance", "https://www.reddit.com/r/personalfinance/hot.json?limit=10", "finance"),
    ("reddit_todayilearned", "https://www.reddit.com/r/todayilearned/hot.json?limit=10", "knowledge"),
    ("reddit_explainlikeimfive", "https://www.reddit.com/r/explainlikeimfive/hot.json?limit=10", "knowledge"),
]

# ---------------------------------------------------------------------------
# Local AI servers (real APIs, no key; user may run any of these)
# ---------------------------------------------------------------------------
LOCAL_AI = [
    # id, base URL, style, label
    ("ollama", "http://localhost:11434", "ollama", "Ollama"),
    ("lmstudio", "http://localhost:1234", "openai", "LM Studio"),
    ("llamacpp", "http://localhost:8080", "llamacpp", "llama.cpp server"),
    ("localai8081", "http://localhost:8081", "openai", "LocalAI"),
    ("vllm", "http://localhost:8000", "openai", "vLLM"),
    ("textgenwebui", "http://localhost:5000", "openai", "text-generation-webui"),
    ("koboldcpp", "http://localhost:5001", "kobold", "KoboldCpp"),
    ("jan", "http://localhost:1337", "openai", "Jan"),
    ("gpt4all", "http://localhost:4891", "openai", "GPT4All"),
    ("openwebui", "http://localhost:3000", "openai", "Open WebUI"),
    ("anythingllm", "http://localhost:3001", "openai", "AnythingLLM"),
    ("msty", "http://localhost:5050", "openai", "Msty"),
    ("llamafile", "http://localhost:8082", "openai", "llamafile"),
    ("sglang", "http://localhost:30000", "openai", "SGLang"),
]

# Generic OpenAI-compatible ports scanned for local AI discovery
OPENAI_PORTS = [11434, 1234, 8080, 8081, 8000, 5000, 5001, 1337, 4891, 3000,
                3001, 5050, 8082, 30000, 7860, 7861, 8001, 9000]

# ---------------------------------------------------------------------------
# Health / science / space / dev / entertainment / transport
# ---------------------------------------------------------------------------
OPENFDA = [
    ("drug_label", "https://api.fda.gov/drug/label.json?search=openfda.brand_name:%22{query}%22&limit=1"),
    ("drug_event", "https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:%22{query}%22&limit=1"),
    ("drug_recall", "https://api.fda.gov/drug/enforcement.json?search=product_description:%22{query}%22&limit=1"),
    ("food_recall", "https://api.fda.gov/food/enforcement.json?search=product_description:%22{query}%22&limit=1"),
    ("device_recall", "https://api.fda.gov/device/enforcement.json?search=product_description:%22{query}%22&limit=1"),
    ("device_event", "https://api.fda.gov/device/event.json?search=device.brand_name:%22{query}%22&limit=1"),
]

DISEASE_SH = [
    ("covid_all", "https://disease.sh/v3/covid-19/all"),
    ("covid_countries", "https://disease.sh/v3/covid-19/countries"),
    ("covid_historical", "https://disease.sh/v3/covid-19/historical/{country}?lastdays=30"),
    ("covid_vaccine", "https://disease.sh/v3/covid-19/vaccine"),
    ("influenza", "https://disease.sh/v3/influenza/cdc/US"),
    ("vaccines", "https://disease.sh/v3/vaccine/coverage?lastdays=30"),
]

WHO_INDICATORS = [
    "WHOSIS_000001", "WHOSIS_000002", "WHOSIS_000004", "WHOSIS_000007",
    "MDG_0000000001", "MDG_0000000020", "SH.DYN.MORT", "SH.STA.BASS.ZS",
]

NASA_APIS = [
    ("apod", "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"),
    ("neows", "https://api.nasa.gov/neo/rest/v1/feed?start_date={start}&end_date={end}&api_key=DEMO_KEY"),
    ("donki_cme", "https://api.nasa.gov/DONKI/CME?startDate={start}&endDate={end}&api_key=DEMO_KEY"),
    ("donki_flare", "https://api.nasa.gov/DONKI/FLR?startDate={start}&endDate={end}&api_key=DEMO_KEY"),
    ("donki_geomag", "https://api.nasa.gov/DONKI/GST?startDate={start}&endDate={end}&api_key=DEMO_KEY"),
    ("epic", "https://api.nasa.gov/EPIC/api/natural?api_key=DEMO_KEY"),
    ("mars_photos", "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key=DEMO_KEY"),
    ("earth_imagery", "https://api.nasa.gov/planetary/earth/imagery?lon={lon}&lat={lat}&date={date}&api_key=DEMO_KEY"),
]

SPACE_APIS = [
    ("spacex_launches", "https://api.spacexdata.com/v4/launches/latest"),
    ("spacex_rockets", "https://api.spacexdata.com/v4/rockets"),
    ("spacex_crew", "https://api.spacexdata.com/v4/crew"),
    ("iss_now", "http://api.open-notify.org/iss-now.json"),
    ("iss_astronauts", "http://api.open-notify.org/astros.json"),
    ("iss_passes", "http://api.open-notify.org/iss-pass.json?lat={lat}&lon={lon}"),
    ("noaa_alerts", "https://services.swpc.noaa.gov/products/alerts.json"),
    ("noaa_solar_wind", "https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json"),
    ("launchlibrary", "https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=5"),
    ("usgs_volcano", "https://volcano.si.edu/news/WeeklyVolcanoRSS.xml"),
]

DEV_APIS = [
    ("github_repos", "https://api.github.com/search/repositories?q={q}&per_page=3"),
    ("github_users", "https://api.github.com/search/users?q={q}&per_page=3"),
    ("github_issues", "https://api.github.com/search/issues?q={q}&per_page=3"),
    ("gitlab_projects", "https://gitlab.com/api/v4/projects?search={q}&per_page=3"),
    ("npm_package", "https://registry.npmjs.org/{q}"),
    ("npm_search", "https://registry.npmjs.org/-/v1/search?text={q}&size=3"),
    ("pypi_project", "https://pypi.org/pypi/{q}/json"),
    ("crates_search", "https://crates.io/api/v1/crates?q={q}&per_page=3"),
    ("nuget_search", "https://azuresearch-usnc.nuget.org/query?q={q}&take=3"),
    ("maven_search", "https://search.maven.org/solrsearch/select?q={q}&rows=3&wt=json"),
    ("rubygems_search", "https://rubygems.org/api/v1/search.json?query={q}"),
    ("packagist_search", "https://packagist.org/search.json?q={q}"),
    ("docker_search", "https://hub.docker.com/v2/search/repositories/?query={q}&page_size=3"),
    ("devto", "https://dev.to/api/articles?tag={q}&per_page=3"),
    ("lobsters", "https://lobste.rs/hottest.json"),
    ("hackernews", "https://hn.algolia.com/api/v1/search?query={q}&hitsPerPage=3"),
]

ENTERTAINMENT_APIS = [
    ("jikan_anime", "https://api.jikan.moe/v4/anime?q={q}&limit=3"),
    ("jikan_manga", "https://api.jikan.moe/v4/manga?q={q}&limit=3"),
    ("jikan_characters", "https://api.jikan.moe/v4/characters?q={q}&limit=3"),
    ("anilist", "https://graphql.anilist.co"),
    ("musicbrainz_artist", "https://musicbrainz.org/ws/2/artist?query={q}&fmt=json&limit=3"),
    ("musicbrainz_release", "https://musicbrainz.org/ws/2/release?query={q}&fmt=json&limit=3"),
    ("musicbrainz_recording", "https://musicbrainz.org/ws/2/recording?query={q}&fmt=json&limit=3"),
    ("meal_search", "https://www.themealdb.com/api/json/v1/1/search.php?s={q}"),
    ("meal_random", "https://www.themealdb.com/api/json/v1/1/random.php"),
    ("cocktail_search", "https://www.thecocktaildb.com/api/json/v1/1/search.php?s={q}"),
    ("cocktail_random", "https://www.thecocktaildb.com/api/json/v1/1/random.php"),
    ("openfood_search", "https://world.openfoodfacts.org/api/v2/search?categories_tags={q}&page_size=3"),
    ("openfood_product", "https://world.openfoodfacts.org/api/v2/product/{q}.json"),
]

TRANSPORT_APIS = [
    ("transport_db", "https://v6.db.transport.rest"),
    ("transport_vbb", "https://vbb.transport.rest"),
    ("transport_bvg", "https://bvg.transport.rest"),
    ("transport_insa", "https://insa.transport.rest"),
    ("transport_saarfahrplan", "https://saarfahrplan.transport.rest"),
    ("transport_nahsh", "https://nahsh.transport.rest"),
    ("transport_avv", "https://avv.transport.rest"),
    ("transport_rvv", "https://rvv.transport.rest"),
    ("transport_vrn", "https://vrn.transport.rest"),
    ("transport_nvv", "https://nvv.transport.rest"),
]

MISC_APIS = [
    ("numbers", "http://numbersapi.com/{q}"),
    ("agify", "https://api.agify.io?name={q}"),
    ("genderize", "https://api.genderize.io?name={q}"),
    ("nationalize", "https://api.nationalize.io?name={q}"),
    ("dns_cloudflare", "https://cloudflare-dns.com/dns-query?name={q}&type=A"),
    ("dns_google", "https://dns.google/resolve?name={q}&type=A"),
    ("open_trivia", "https://opentdb.com/api.php?amount=3&type=multiple"),
    ("yesno", "https://yesno.wtf/api"),
    ("bored", "https://www.boredapi.com/api/activity"),
    ("advice", "https://api.adviceslip.com/advice"),
    ("zenquotes", "https://zenquotes.io/api/random"),
    ("quotable", "https://api.quotable.io/random"),
    ("http_cat", "https://http.cat/200"),
    ("http_dog", "https://http.dog/200.jpg"),
]

CRYPTO_APIS = [
    ("binance", "https://api.binance.com/api/v3/ticker/price?symbol={pair}"),
    ("coinbase", "https://api.coinbase.com/v2/prices/{pair}/spot"),
    ("kraken", "https://api.kraken.com/0/public/Ticker?pair={pair}"),
    ("bitfinex", "https://api-pub.bitfinex.com/v2/ticker/{pair}"),
    ("okx", "https://www.okx.com/api/v5/market/ticker?instId={pair}"),
    ("bybit", "https://api.bybit.com/v5/market/tickers?category=spot&symbol={pair}"),
    ("kucoin", "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={pair}"),
    ("gateio", "https://api.gateio.ws/api/v4/spot/tickers?currency_pair={pair}"),
    ("mexc", "https://api.mexc.com/api/v3/ticker/price?symbol={pair}"),
    ("cryptocom", "https://api.crypto.com/v2/public/get-ticker?instrument_name={pair}"),
    ("coingecko_price", "https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={vs}"),
    ("coingecko_list", "https://api.coingecko.com/api/v3/coins/list"),
    ("coingecko_chart", "https://api.coingecko.com/api/v3/coins/{id}/market_chart?vs_currency=usd&days={days}"),
]

# ---------------------------------------------------------------------------
# Al Quran / Hadith (keyless)
# ---------------------------------------------------------------------------
QURAN_EDITIONS = [
    "en.asad", "en.sahih", "ur.jalandhry", "ur.junagarhi", "ar.alafasy",
    "fr.hamidullah", "de.aburida", "tr.diyanet", "id.indonesian", "es.cortes",
]
