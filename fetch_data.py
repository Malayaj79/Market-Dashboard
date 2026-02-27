"""
Momentum Command Centre — Data Fetcher
Runs via GitHub Actions daily at 22:00 UTC (6pm ET, after US market close).
Writes data/market_data.json which index.html reads.

To update MA signals: edit the ma= value in THEMES below (1=bull, 0=neutral, -1=bear).
"""
import json, datetime, time, urllib.request

THEMES = [
  ("ai",        "Artificial Intelligence",     "AI",          "⚡","Technology",     "AIQ",  ["NVDA","MSFT","GOOGL","META","AMZN","PLTR"],  "#00d4ff", 0),
  ("semi",      "Semiconductors & Chips",      "Semis",       "💎","Technology",     "SOXX", ["NVDA","AMD","AVGO","ASML","TSM","AMAT"],     "#818cf8",-1),
  ("cloud",     "Cloud Computing",             "Cloud",       "☁","Technology",     "WCLD", ["AMZN","MSFT","GOOGL","SNOW","NET","DDOG"],   "#60a5fa",-1),
  ("cyber",     "Cybersecurity",               "Cyber",       "🔐","Technology",    "HACK", ["CRWD","PANW","ZS","FTNT","S","OKTA"],        "#22d3ee", 1),
  ("quantum",   "Quantum Computing",           "Quantum",     "🔬","Technology",    "QTUM", ["IONQ","RGTI","QUBT","IBM","GOOGL","MSFT"],   "#a78bfa", 1),
  ("robotics",  "Robotics & Automation",       "Robots",      "🤖","Technology",    "ROBO", ["ISRG","ABB","PATH","TSLA","FANUY","BRZE"],   "#c084fc", 1),
  ("iot",       "Internet of Things",          "IoT",         "📡","Technology",    "SNSR", ["CSCO","TXN","MCHP","PTC","SWKS","QRVO"],    "#38bdf8", 0),
  ("print3d",   "3D Printing",                 "3D Print",    "🖨","Technology",    "PRNT", ["DDD","SSYS","MKFG","XMTR","NNDM","MTLS"],   "#7c3aed",-1),
  ("saas",      "Software as a Service",       "SaaS",        "🧩","Technology",    "IGV",  ["CRM","NOW","WDAY","HUBS","ZM","BILL"],       "#6ee7b7", 0),
  ("datacntr",  "Data Centers & Infra",        "DataCtrs",    "🏭","Technology",    "SRVR", ["EQIX","DLR","NVDA","SMCI","VRT","ETN"],      "#fca5a5", 1),
  ("memory",    "Memory & Data Storage",       "Memory",      "💾","Memory & Storage","MU", ["SNDK","WDC","STX","MU","MRVL","NTAP"],       "#38bdf8", 1),
  ("fiber",     "Fiber Optics & Optical Net.", "Fiber",       "🔆","Fiber Optics",  "CIEN", ["AAOI","LITE","COHR","CIEN","VIAV"],          "#bbf7d0", 1),
  ("nuclear",   "Nuclear Energy",              "Nuclear",     "⚛","Energy",         "NLR",  ["CEG","VST","NRG","CCJ","BWXT","SMR"],        "#fde68a", 1),
  ("uranium",   "Uranium Mining",              "Uranium",     "☢","Energy",         "URNM", ["CCJ","NXE","DNN","UUUU","URG"],              "#f59e0b", 1),
  ("clean",     "Clean & Renewable Energy",    "Clean NRG",   "🌱","Energy",        "ICLN", ["ENPH","FSLR","NEE","SEDG","RUN","BEP"],      "#4ade80", 1),
  ("battery",   "Battery Technology",          "Battery",     "🔋","Energy",        "LIT",  ["TSLA","QS","ALB","SQM","FLNC","STEM"],       "#34d399", 0),
  ("grid",      "Power Grid Modernization",    "Grid",        "🔌","Energy",        "GRID", ["ETN","VRT","EMR","HUBB","PWR","GEV"],        "#86efac", 1),
  ("oilgas",    "Traditional Oil & Gas",       "Oil & Gas",   "🛢","Energy",        "XLE",  ["XOM","CVX","COP","SLB","EOG","MPC"],         "#d97706",-1),
  ("minerals",  "Critical Minerals",           "Minerals",    "⛏","Materials",      "COPX", ["FCX","MP","ALB","VALE","RIO","LTHM"],        "#fb923c", 1),
  ("gold",      "Gold & Gold Miners",          "Gold",        "🥇","Precious Metals","GLD",  ["GLD","NEM","GOLD","AEM","WPM","FNV"],        "#ffd700", 1),
  ("silver",    "Silver & Silver Miners",      "Silver",      "🥈","Precious Metals","SLV",  ["SLV","PAAS","AG","HL","MAG","WPM"],          "#e2e8f0", 1),
  ("jrgold",    "Junior Gold Miners",          "Jr. Gold",    "⛏","Precious Metals","GDXJ", ["GDXJ","ORLA","KNT","MAI","NGD","AUMN"],      "#fcd34d", 1),
  ("pgm",       "Platinum Group Metals",       "PGMs",        "⚗","Precious Metals","PPLT", ["PPLT","PALL","SBSW","IMPUY","ANGPY"],        "#cbd5e1", 0),
  ("broadmet",  "Broad Precious Metals",       "Prec. Metals","🏅","Precious Metals","GLTR", ["GLD","SLV","PPLT","PALL","WPM","FNV"],       "#f0abfc", 1),
  ("water",     "Water Management",            "Water",       "💧","Utilities",      "PHO",  ["AWK","XYL","WTRG","PNR","MSEX","CWCO"],      "#0ea5e9", 0),
  ("space",     "Space Exploration",           "Space",       "🚀","Industrials",    "UFO",  ["ASTS","LUNR","RKLB","RDW","ASTR","SPCE"],    "#8b5cf6", 1),
  ("defense",   "Defense & Military Tech",     "Defense",     "🛡","Industrials",    "ITA",  ["LMT","RTX","NOC","GD","BA","HII"],           "#ff6b35", 1),
  ("drones",    "Drones & Autonomous",         "Drones",      "🛸","Industrials",    "IFLY", ["ACHR","JOBY","AVAV","KTOS","RCAT","UAVS"],   "#f472b6", 1),
  ("reshoring", "Supply Chain Reshoring",      "Reshoring",   "🏗","Industrials",    "PAVE", ["CAT","DE","URI","MLM","VMC","NUE"],           "#fdba74", 0),
  ("machinery", "Heavy Machinery & Infra",     "Machinery",   "🔧","Industrials",    "XLI",  ["CAT","DE","CMI","PCAR","TEX","WNC"],          "#94a3b8", 0),
]

def fetch(ticker, period="3mo"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={period}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read())
        res = d["chart"]["result"][0]
        return {"ts": res["timestamp"], "closes": res["indicators"]["quote"][0]["close"],
                "price": res["meta"].get("regularMarketPrice") or res["meta"].get("previousClose")}
    except Exception as e:
        print(f"  ERR {ticker}: {e}"); return None

def price_on(ts, closes, target):
    best = None
    for t, p in zip(ts, closes):
        if t <= target and p is not None: best = p
    return best

def pct(cur, base):
    if cur and base and base != 0: return round((cur-base)/abs(base)*100, 2)
    return None

now = datetime.datetime.utcnow()
yesterday = now - datetime.timedelta(days=1)
days_since_fri = (now.weekday() - 4) % 7
last_fri = now - datetime.timedelta(days=max(days_since_fri, 1))
month_end = now.replace(day=1) - datetime.timedelta(days=1)
def mkets(dt): return int(datetime.datetime(dt.year, dt.month, dt.day, 21, 0).timestamp())

print("Fetching SPY...")
spy_raw = fetch("SPY")
spy = {"d":None,"w":None,"m":None}
if spy_raw:
    c = spy_raw["price"]
    spy = {
        "d": pct(c, price_on(spy_raw["ts"], spy_raw["closes"], mkets(yesterday))),
        "w": pct(c, price_on(spy_raw["ts"], spy_raw["closes"], mkets(last_fri))),
        "m": pct(c, price_on(spy_raw["ts"], spy_raw["closes"], mkets(month_end))),
    }
    print(f"  SPY 1D={spy['d']}% 1W={spy['w']}% 1M={spy['m']}%")

results = []
for (tid, name, short, icon, sector, etf, stocks, color, ma) in THEMES:
    print(f"Fetching {etf}...")
    raw = fetch(etf); time.sleep(0.35)
    if not raw: continue
    c = raw["price"]
    r1D = pct(c, price_on(raw["ts"], raw["closes"], mkets(yesterday)))
    r1W = pct(c, price_on(raw["ts"], raw["closes"], mkets(last_fri)))
    r1M = pct(c, price_on(raw["ts"], raw["closes"], mkets(month_end)))
    rs1D = round(r1D - spy["d"], 2) if r1D is not None and spy["d"] is not None else None
    rs1W = round(r1W - spy["w"], 2) if r1W is not None and spy["w"] is not None else None
    rs1M = round(r1M - spy["m"], 2) if r1M is not None and spy["m"] is not None else None
    score = None
    if None not in (r1D, r1W, r1M, rs1D, rs1W, rs1M):
        score = round((r1D*.20+r1W*.35+r1M*.45)*.45 + (rs1D*.20+rs1W*.35+rs1M*.45)*.35 + ma*7, 1)
    spark5 = [round(x,2) for x in raw["closes"] if x is not None][-5:]
    results.append({"id":tid,"name":name,"short":short,"icon":icon,"sector":sector,"etf":etf,
        "stocks":stocks,"color":color,"ma":ma,"price":round(c,2) if c else None,
        "ret1D":r1D,"ret1W":r1W,"ret1M":r1M,"rs1D":rs1D,"rs1W":rs1W,"rs1M":rs1M,
        "score":score,"spark5":spark5})
    print(f"  {etf}: ${c:.2f} 1M={r1M}% score={score}")

results.sort(key=lambda x: x["score"] if x["score"] is not None else -999, reverse=True)
out = {"updated": now.strftime("%Y-%m-%d %H:%M UTC"), "spy": spy, "themes": results}
with open("data/market_data.json","w") as f: json.dump(out, f, indent=2)
print(f"\n✅ Wrote {len(results)} themes. Top 3: {', '.join(r['name'] for r in results[:3])}")
