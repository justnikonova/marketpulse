"""
var.py — Ticker Lists & Sector Mappings
========================================
Static ticker lists with (Sector, Sub-Industry) tuples.
Used by the combined Market Pulse + Signal Scanner application.
"""

# ─── S&P 500 Stocks with GICS Sector/Sub-Industry ────────────────────────────
SP500_STOCKS = {
    # TECHNOLOGY
    "ADBE": ("Information Technology", "Application Software"),
    "APP": ("Information Technology", "Application Software"),
    "CDNS": ("Information Technology", "Application Software"),
    "CRM": ("Information Technology", "Application Software"),
    "INTU": ("Information Technology", "Application Software"),
    "ORCL": ("Information Technology", "Application Software"),
    "PLTR": ("Information Technology", "Application Software"),
    "SNPS": ("Information Technology", "Application Software"),
    "ANET": ("Information Technology", "Communications Equipment"),
    "CSCO": ("Information Technology", "Communications Equipment"),
    "MSI": ("Information Technology", "Communications Equipment"),
    "APH": ("Information Technology", "Electronic Components"),
    "GLW": ("Information Technology", "Electronic Components"),
    "KEYS": ("Information Technology", "Electronic Equipment & Instruments"),
    "TEL": ("Information Technology", "Electronic Manufacturing Services"),
    "ACN": ("Information Technology", "IT Consulting & Other Services"),
    "IBM": ("Information Technology", "IT Consulting & Other Services"),
    "AMAT": ("Information Technology", "Semiconductor Materials & Equipment"),
    "KLAC": ("Information Technology", "Semiconductor Materials & Equipment"),
    "LRCX": ("Information Technology", "Semiconductor Materials & Equipment"),
    "TER": ("Information Technology", "Semiconductor Materials & Equipment"),
    "ADI": ("Information Technology", "Semiconductors"),
    "AMD": ("Information Technology", "Semiconductors"),
    "AVGO": ("Information Technology", "Semiconductors"),
    "INTC": ("Information Technology", "Semiconductors"),
    "MPWR": ("Information Technology", "Semiconductors"),
    "MU": ("Information Technology", "Semiconductors"),
    "NVDA": ("Information Technology", "Semiconductors"),
    "NXPI": ("Information Technology", "Semiconductors"),
    "QCOM": ("Information Technology", "Semiconductors"),
    "TXN": ("Information Technology", "Semiconductors"),
    "CRWD": ("Information Technology", "Systems Software"),
    "FTNT": ("Information Technology", "Systems Software"),
    "MSFT": ("Information Technology", "Systems Software"),
    "NOW": ("Information Technology", "Systems Software"),
    "PANW": ("Information Technology", "Systems Software"),
    "AAPL": ("Information Technology", "Technology Hardware, Storage & Peripherals"),
    "DELL": ("Information Technology", "Technology Hardware, Storage & Peripherals"),
    "SNDK": ("Information Technology", "Technology Hardware, Storage & Peripherals"),
    "STX": ("Information Technology", "Technology Hardware, Storage & Peripherals"),
    "WDC": ("Information Technology", "Technology Hardware, Storage & Peripherals"),

    # COMMUNICATION SERVICES
    "WBD": ("Communication Services", "Broadcasting"),
    "CMCSA": ("Communication Services", "Cable & Satellite"),
    "T": ("Communication Services", "Integrated Telecommunication Services"),
    "VZ": ("Communication Services", "Integrated Telecommunication Services"),
    "EA": ("Communication Services", "Interactive Home Entertainment"),
    "GOOGL": ("Communication Services", "Interactive Media & Services"),
    "META": ("Communication Services", "Interactive Media & Services"),
    "DIS": ("Communication Services", "Movies & Entertainment"),
    "NFLX": ("Communication Services", "Movies & Entertainment"),
    "TMUS": ("Communication Services", "Wireless Telecommunication Services"),
    "TTWO": ("Communication Services", "Entertainment"),

    # CONSUMER CYCLICAL
    "ROST": ("Consumer Discretionary", "Apparel Retail"),
    "TJX": ("Consumer Discretionary", "Apparel Retail"),
    "NKE": ("Consumer Discretionary", "Apparel, Accessories & Luxury Goods"),
    "F": ("Consumer Discretionary", "Automobile Manufacturers"),
    "GM": ("Consumer Discretionary", "Automobile Manufacturers"),
    "TSLA": ("Consumer Discretionary", "Automobile Manufacturers"),
    "AZO": ("Consumer Discretionary", "Automotive Retail"),
    "ORLY": ("Consumer Discretionary", "Automotive Retail"),
    "AMZN": ("Consumer Discretionary", "Broadline Retail"),
    "HD": ("Consumer Discretionary", "Home Improvement Retail"),
    "LOW": ("Consumer Discretionary", "Home Improvement Retail"),
    "MAR": ("Consumer Discretionary", "Hotels, Resorts & Cruise Lines"),
    "ABNB": ("Consumer Discretionary", "Hotels, Resorts & Cruise Lines"),
    "BKNG": ("Consumer Discretionary", "Hotels, Resorts & Cruise Lines"),
    "HLT": ("Consumer Discretionary", "Hotels, Resorts & Cruise Lines"),
    "RCL": ("Consumer Discretionary", "Hotels, Resorts & Cruise Lines"),
    "MCD": ("Consumer Discretionary", "Restaurants"),
    "SBUX": ("Consumer Discretionary", "Restaurants"),
    "DASH": ("Consumer Discretionary", "Specialized Consumer Services"),

    # CONSUMER DEFENSIVE
    "COST": ("Consumer Staples", "Consumer Staples Merchandise Retail"),
    "TGT": ("Consumer Staples", "Consumer Staples Merchandise Retail"),
    "WMT": ("Consumer Staples", "Consumer Staples Merchandise Retail"),
    "CL": ("Consumer Staples", "Household Products"),
    "MDLZ": ("Consumer Staples", "Packaged Foods & Meats"),
    "PG": ("Consumer Staples", "Personal Care Products"),
    "KO": ("Consumer Staples", "Soft Drinks & Non-alcoholic Beverages"),
    "MNST": ("Consumer Staples", "Soft Drinks & Non-alcoholic Beverages"),
    "PEP": ("Consumer Staples", "Soft Drinks & Non-alcoholic Beverages"),
    "MO": ("Consumer Staples", "Tobacco"),
    "PM": ("Consumer Staples", "Tobacco"),

    # HEALTHCARE
    "ABBV": ("Health Care", "Biotechnology"),
    "AMGN": ("Health Care", "Biotechnology"),
    "GILD": ("Health Care", "Biotechnology"),
    "REGN": ("Health Care", "Biotechnology"),
    "VRTX": ("Health Care", "Biotechnology"),
    "CAH": ("Health Care", "Health Care Distributors"),
    "COR": ("Health Care", "Health Care Distributors"),
    "MCK": ("Health Care", "Health Care Distributors"),
    "ABT": ("Health Care", "Health Care Equipment"),
    "BDX": ("Health Care", "Health Care Equipment"),
    "BSX": ("Health Care", "Health Care Equipment"),
    "IDXX": ("Health Care", "Health Care Equipment"),
    "ISRG": ("Health Care", "Health Care Equipment"),
    "MDT": ("Health Care", "Health Care Equipment"),
    "SYK": ("Health Care", "Health Care Equipment"),
    "HCA": ("Health Care", "Health Care Facilities"),
    "CI": ("Health Care", "Health Care Services"),
    "CVS": ("Health Care", "Health Care Services"),
    "DHR": ("Health Care", "Life Sciences Tools & Services"),
    "TMO": ("Health Care", "Life Sciences Tools & Services"),
    "ELV": ("Health Care", "Managed Health Care"),
    "UNH": ("Health Care", "Managed Health Care"),
    "BMY": ("Health Care", "Pharmaceuticals"),
    "JNJ": ("Health Care", "Pharmaceuticals"),
    "LLY": ("Health Care", "Pharmaceuticals"),
    "MRK": ("Health Care", "Pharmaceuticals"),
    "PFE": ("Health Care", "Pharmaceuticals"),
    "ZTS": ("Health Care", "Pharmaceuticals"),

    # FINANCIAL
    "APO": ("Financials", "Asset Management & Custody Banks"),
    "BK": ("Financials", "Asset Management & Custody Banks"),
    "BLK": ("Financials", "Asset Management & Custody Banks"),
    "BX": ("Financials", "Asset Management & Custody Banks"),
    "KKR": ("Financials", "Asset Management & Custody Banks"),
    "AXP": ("Financials", "Consumer Finance"),
    "COF": ("Financials", "Consumer Finance"),
    "BAC": ("Financials", "Diversified Banks"),
    "C": ("Financials", "Diversified Banks"),
    "JPM": ("Financials", "Diversified Banks"),
    "PNC": ("Financials", "Diversified Banks"),
    "TFC": ("Financials", "Diversified Banks"),
    "USB": ("Financials", "Diversified Banks"),
    "WFC": ("Financials", "Diversified Banks"),
    "CME": ("Financials", "Financial Exchanges & Data"),
    "ICE": ("Financials", "Financial Exchanges & Data"),
    "MCO": ("Financials", "Financial Exchanges & Data"),
    "SPGI": ("Financials", "Financial Exchanges & Data"),
    "AJG": ("Financials", "Insurance Brokers"),
    "AON": ("Financials", "Insurance Brokers"),
    "MRSH": ("Financials", "Insurance Brokers"),
    "GS": ("Financials", "Investment Banking & Brokerage"),
    "HOOD": ("Financials", "Investment Banking & Brokerage"),
    "MS": ("Financials", "Investment Banking & Brokerage"),
    "SCHW": ("Financials", "Investment Banking & Brokerage"),
    "AFL": ("Financials", "Life & Health Insurance"),
    "ALL": ("Financials", "Property & Casualty Insurance"),
    "CB": ("Financials", "Property & Casualty Insurance"),
    "PGR": ("Financials", "Property & Casualty Insurance"),
    "TRV": ("Financials", "Property & Casualty Insurance"),
    "MA": ("Financials", "Transaction & Payment Processing Services"),
    "V": ("Financials", "Transaction & Payment Processing Services"),

    # INDUSTRIALS
    "BA": ("Industrials", "Aerospace & Defense"),
    "GD": ("Industrials", "Aerospace & Defense"),
    "GE": ("Industrials", "Aerospace & Defense"),
    "HWM": ("Industrials", "Aerospace & Defense"),
    "LHX": ("Industrials", "Aerospace & Defense"),
    "LMT": ("Industrials", "Aerospace & Defense"),
    "NOC": ("Industrials", "Aerospace & Defense"),
    "RTX": ("Industrials", "Aerospace & Defense"),
    "TDG": ("Industrials", "Aerospace & Defense"),
    "DE": ("Industrials", "Agricultural & Farm Machinery"),
    "FDX": ("Industrials", "Air Freight & Logistics"),
    "UPS": ("Industrials", "Air Freight & Logistics"),
    "CARR": ("Industrials", "Building Products"),
    "JCI": ("Industrials", "Building Products"),
    "TT": ("Industrials", "Building Products"),
    "PWR": ("Industrials", "Construction & Engineering"),
    "CAT": ("Industrials", "Construction Machinery & Heavy Transportation Equipment"),
    "CMI": ("Industrials", "Construction Machinery & Heavy Transportation Equipment"),
    "PCAR": ("Industrials", "Construction Machinery & Heavy Transportation Equipment"),
    "CTAS": ("Industrials", "Diversified Support Services"),
    "AME": ("Industrials", "Electrical Components & Equipment"),
    "EMR": ("Industrials", "Electrical Components & Equipment"),
    "ETN": ("Industrials", "Electrical Components & Equipment"),
    "RSG": ("Industrials", "Environmental & Facilities Services"),
    "WM": ("Industrials", "Environmental & Facilities Services"),
    "GEV": ("Industrials", "Heavy Electrical Equipment"),
    "ADP": ("Industrials", "Human Resource & Employment Services"),
    "HON": ("Industrials", "Industrial Conglomerates"),
    "MMM": ("Industrials", "Industrial Conglomerates"),
    "GWW": ("Industrials", "Industrial Machinery & Supplies & Components"),
    "ITW": ("Industrials", "Industrial Machinery & Supplies & Components"),
    "PH": ("Industrials", "Industrial Machinery & Supplies & Components"),
    "UBER": ("Industrials", "Passenger Ground Transportation"),
    "CSX": ("Industrials", "Rail Transportation"),
    "NSC": ("Industrials", "Rail Transportation"),
    "UNP": ("Industrials", "Rail Transportation"),
    "FAST": ("Industrials", "Trading Companies & Distributors"),
    "URI": ("Industrials", "Trading Companies & Distributors"),

    # ENERGY
    "CVX": ("Energy", "Integrated Oil & Gas"),
    "XOM": ("Energy", "Integrated Oil & Gas"),
    "BKR": ("Energy", "Oil & Gas Equipment & Services"),
    "SLB": ("Energy", "Oil & Gas Equipment & Services"),
    "COP": ("Energy", "Oil & Gas Exploration & Production"),
    "EOG": ("Energy", "Oil & Gas Exploration & Production"),
    "OXY": ("Energy", "Oil & Gas Exploration & Production"),
    "MPC": ("Energy", "Oil & Gas Refining & Marketing"),
    "PSX": ("Energy", "Oil & Gas Refining & Marketing"),
    "VLO": ("Energy", "Oil & Gas Refining & Marketing"),
    "KMI": ("Energy", "Oil & Gas Storage & Transportation"),
    "OKE": ("Energy", "Oil & Gas Storage & Transportation"),
    "WMB": ("Energy", "Oil & Gas Storage & Transportation"),

    # REAL ESTATE
    "DLR": ("Real Estate", "Data Center REITs"),
    "EQIX": ("Real Estate", "Data Center REITs"),
    "WELL": ("Real Estate", "Health Care REITs"),
    "PLD": ("Real Estate", "Industrial REITs"),
    "O": ("Real Estate", "Retail REITs"),
    "SPG": ("Real Estate", "Retail REITs"),
    "PSA": ("Real Estate", "Self-Storage REITs"),
    "AMT": ("Real Estate", "Telecom Tower REITs"),

    # UTILITIES
    "AEP": ("Utilities", "Electric Utilities"),
    "CEG": ("Utilities", "Electric Utilities"),
    "DUK": ("Utilities", "Electric Utilities"),
    "SO": ("Utilities", "Electric Utilities"),
    "VST": ("Utilities", "Electric Utilities"),
    "D": ("Utilities", "Multi-Utilities"),
    "NEE": ("Utilities", "Multi-Utilities"),
    "SRE": ("Utilities", "Multi-Utilities"),

    # BASIC MATERIALS
    "CRH": ("Materials", "Construction Materials"),
    "FCX": ("Materials", "Copper"),
    "CTVA": ("Materials", "Fertilizers & Agricultural Chemicals"),
    "NEM": ("Materials", "Gold"),
    "APD": ("Materials", "Industrial Gases"),
    "LIN": ("Materials", "Industrial Gases"),
    "ECL": ("Materials", "Specialty Chemicals"),
    "SHW": ("Materials", "Specialty Chemicals"),

    # ADDITIONAL TICKERS (Trade History & Custom Watchlists)
    "AKAM": ("Information Technology", "IT Consulting & Other Services"),
    "APA": ("Energy", "Oil & Gas Exploration & Production"),
    "BG": ("Consumer Staples", "Agricultural Products & Services"),
    "BIIB": ("Health Care", "Biotechnology"),
    "CFG": ("Financials", "Regional Banks"),
    "CHRW": ("Industrials", "Air Freight & Logistics"),
    "CIEN": ("Information Technology", "Communications Equipment"),
    "CTRA": ("Energy", "Oil & Gas Exploration & Production"),
    "DVN": ("Energy", "Oil & Gas Exploration & Production"),
    "FANG": ("Energy", "Oil & Gas Exploration & Production"),
    "FIX": ("Industrials", "Building Products"),
    "HAS": ("Consumer Discretionary", "Leisure Products"),
    "HUBB": ("Industrials", "Electrical Components & Equipment"),
    "IBKR": ("Financials", "Investment Banking & Brokerage"),
    "JBL": ("Information Technology", "Electronic Manufacturing Services"),
    "LUV": ("Industrials", "Passenger Airlines"),
    "PKG": ("Materials", "Paper & Plastic Packaging Products & Materials"),
    "SWK": ("Industrials", "Industrial Machinery & Supplies & Components"),
    "TDY": ("Industrials", "Aerospace & Defense"),
    "TRGP": ("Energy", "Oil & Gas Storage & Transportation"),
    "VTRS": ("Health Care", "Pharmaceuticals"),
    "WAB": ("Industrials", "Rail Transportation"),
}

# ─── NASDAQ 100 Stocks with Sector/Sub-Industry ──────────────────────────────
# Static list — no runtime Wikipedia fetching required
NASDAQ100_STOCKS = {
    # TECHNOLOGY
    "AAPL": ("Information Technology", "Technology Hardware, Storage & Peripherals"),
    "MSFT": ("Information Technology", "Systems Software"),
    "NVDA": ("Information Technology", "Semiconductors"),
    "AVGO": ("Information Technology", "Semiconductors"),
    "AMD": ("Information Technology", "Semiconductors"),
    "QCOM": ("Information Technology", "Semiconductors"),
    "TXN": ("Information Technology", "Semiconductors"),
    "INTC": ("Information Technology", "Semiconductors"),
    "MU": ("Information Technology", "Semiconductors"),
    "MRVL": ("Information Technology", "Semiconductors"),
    "NXPI": ("Information Technology", "Semiconductors"),
    "MPWR": ("Information Technology", "Semiconductors"),
    "ON": ("Information Technology", "Semiconductors"),
    "ADI": ("Information Technology", "Semiconductors"),
    "ADBE": ("Information Technology", "Application Software"),
    "CRM": ("Information Technology", "Application Software"),
    "INTU": ("Information Technology", "Application Software"),
    "SNPS": ("Information Technology", "Application Software"),
    "CDNS": ("Information Technology", "Application Software"),
    "PANW": ("Information Technology", "Systems Software"),
    "CRWD": ("Information Technology", "Systems Software"),
    "FTNT": ("Information Technology", "Systems Software"),
    "AMAT": ("Information Technology", "Semiconductor Materials & Equipment"),
    "KLAC": ("Information Technology", "Semiconductor Materials & Equipment"),
    "LRCX": ("Information Technology", "Semiconductor Materials & Equipment"),
    "CSCO": ("Information Technology", "Communications Equipment"),
    "ANET": ("Information Technology", "Communications Equipment"),
    "APP": ("Information Technology", "Application Software"),
    "TEAM": ("Information Technology", "Application Software"),
    "TTD": ("Information Technology", "Application Software"),
    "DASH": ("Consumer Discretionary", "Specialized Consumer Services"),
    "WDAY": ("Information Technology", "Application Software"),
    "ZS": ("Information Technology", "Systems Software"),
    "DDOG": ("Information Technology", "Application Software"),
    "MSTR": ("Information Technology", "Application Software"),

    # COMMUNICATION SERVICES
    "GOOGL": ("Communication Services", "Interactive Media & Services"),
    "GOOG": ("Communication Services", "Interactive Media & Services"),
    "META": ("Communication Services", "Interactive Media & Services"),
    "NFLX": ("Communication Services", "Movies & Entertainment"),
    "CMCSA": ("Communication Services", "Cable & Satellite"),
    "TMUS": ("Communication Services", "Wireless Telecommunication Services"),
    "EA": ("Communication Services", "Interactive Home Entertainment"),
    "TTWO": ("Communication Services", "Entertainment"),

    # CONSUMER DISCRETIONARY
    "AMZN": ("Consumer Discretionary", "Broadline Retail"),
    "TSLA": ("Consumer Discretionary", "Automobile Manufacturers"),
    "BKNG": ("Consumer Discretionary", "Hotels, Resorts & Cruise Lines"),
    "ABNB": ("Consumer Discretionary", "Hotels, Resorts & Cruise Lines"),
    "ROST": ("Consumer Discretionary", "Apparel Retail"),
    "LULU": ("Consumer Discretionary", "Apparel, Accessories & Luxury Goods"),
    "ORLY": ("Consumer Discretionary", "Automotive Retail"),
    "SBUX": ("Consumer Discretionary", "Restaurants"),
    "MELI": ("Consumer Discretionary", "Broadline Retail"),
    "CPRT": ("Consumer Discretionary", "Specialized Consumer Services"),
    "CSGP": ("Consumer Discretionary", "Real Estate Services"),
    "PAYX": ("Industrials", "Human Resource & Employment Services"),
    "FAST": ("Industrials", "Trading Companies & Distributors"),

    # CONSUMER STAPLES
    "COST": ("Consumer Staples", "Consumer Staples Merchandise Retail"),
    "PEP": ("Consumer Staples", "Soft Drinks & Non-alcoholic Beverages"),
    "MNST": ("Consumer Staples", "Soft Drinks & Non-alcoholic Beverages"),
    "KHC": ("Consumer Staples", "Packaged Foods & Meats"),
    "MDLZ": ("Consumer Staples", "Packaged Foods & Meats"),
    "KO": ("Consumer Staples", "Soft Drinks & Non-alcoholic Beverages"),
    "WBA": ("Consumer Staples", "Drug Retail"),

    # HEALTH CARE
    "AMGN": ("Health Care", "Biotechnology"),
    "GILD": ("Health Care", "Biotechnology"),
    "VRTX": ("Health Care", "Biotechnology"),
    "REGN": ("Health Care", "Biotechnology"),
    "BIIB": ("Health Care", "Biotechnology"),
    "ILMN": ("Health Care", "Life Sciences Tools & Services"),
    "ISRG": ("Health Care", "Health Care Equipment"),
    "IDXX": ("Health Care", "Health Care Equipment"),
    "DXCM": ("Health Care", "Health Care Equipment"),
    "MRNA": ("Health Care", "Biotechnology"),
    "AZN": ("Health Care", "Pharmaceuticals"),
    "LIN": ("Materials", "Industrial Gases"),

    # FINANCIALS
    "PYPL": ("Financials", "Transaction & Payment Processing Services"),
    "ADP": ("Industrials", "Human Resource & Employment Services"),
    "CSX": ("Industrials", "Rail Transportation"),

    # INDUSTRIALS
    "HON": ("Industrials", "Industrial Conglomerates"),
    "GE": ("Industrials", "Aerospace & Defense"),
    "GEV": ("Industrials", "Heavy Electrical Equipment"),
    "VRSK": ("Industrials", "Research & Consulting Services"),
    "ODFL": ("Industrials", "Trucking"),
    "CTAS": ("Industrials", "Diversified Support Services"),
    "CDW": ("Information Technology", "Technology Distributors"),
    "BKR": ("Energy", "Oil & Gas Equipment & Services"),

    # ENERGY / UTILITIES
    "CEG": ("Utilities", "Electric Utilities"),
    "XEL": ("Utilities", "Electric Utilities"),
    "EXC": ("Utilities", "Electric Utilities"),
    "AEP": ("Utilities", "Electric Utilities"),

    # OTHER
    "GEHC": ("Health Care", "Health Care Equipment"),
    "ARM": ("Information Technology", "Semiconductors"),
    "SMCI": ("Information Technology", "Technology Hardware, Storage & Peripherals"),
    "COIN": ("Financials", "Financial Exchanges & Data"),
    "MCHP": ("Information Technology", "Semiconductors"),
    "FICO": ("Information Technology", "Application Software"),
    "ANSS": ("Information Technology", "Application Software"),
    "CTSH": ("Information Technology", "IT Consulting & Other Services"),
    "NTES": ("Communication Services", "Interactive Home Entertainment"),
    "JD": ("Consumer Discretionary", "Broadline Retail"),
    "PDD": ("Consumer Discretionary", "Broadline Retail"),
    "PCAR": ("Industrials", "Construction Machinery & Heavy Transportation Equipment"),
    "CHTR": ("Communication Services", "Cable & Satellite"),
    "MAR": ("Consumer Discretionary", "Hotels, Resorts & Cruise Lines"),
    "ROP": ("Information Technology", "Application Software"),
    "DLTR": ("Consumer Discretionary", "General Merchandise Stores"),
    "FANG": ("Energy", "Oil & Gas Exploration & Production"),
    "KDP": ("Consumer Staples", "Soft Drinks & Non-alcoholic Beverages"),
    "CCEP": ("Consumer Staples", "Soft Drinks & Non-alcoholic Beverages"),
    "LNTH": ("Health Care", "Pharmaceuticals"),
    "AXON": ("Industrials", "Aerospace & Defense"),
}

# ─── Sector Display Colors ───────────────────────────────────────────────────
SECTOR_COLORS = {
    "Information Technology": "#1a6b3c",
    "Communication Services": "#1a5c8c",
    "Consumer Discretionary": "#7b3f00",
    "Consumer Staples": "#4a7b3f",
    "Health Care": "#2d5a8c",
    "Financials": "#6b2d6b",
    "Industrials": "#4a4a8c",
    "Energy": "#8c6b2d",
    "Real Estate": "#5a8c5a",
    "Utilities": "#3d6b6b",
    "Materials": "#8c5a2d",
}

# ─── Sector ETF Mappings ─────────────────────────────────────────────────────
SECTOR_ETFS = {
    "Information Technology": "XLK",
    "Communication Services": "XLC",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Health Care": "XLV",
    "Financials": "XLF",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
    "Materials": "XLB",
}

# ─── Convenience: merged lookup for any ticker ───────────────────────────────
def get_all_stocks():
    """Return a merged dict of all known tickers with sector info."""
    merged = {}
    merged.update(SP500_STOCKS)
    merged.update(NASDAQ100_STOCKS)
    return merged

def get_ticker_list(universe: str) -> list:
    """Return a sorted list of tickers for the given universe name."""
    if universe == "S&P 500":
        return sorted(SP500_STOCKS.keys())
    elif universe == "NASDAQ 100":
        return sorted(NASDAQ100_STOCKS.keys())
    else:
        return []

def get_sector_for_ticker(ticker: str) -> str:
    """Look up sector for a ticker across all lists."""
    all_stocks = get_all_stocks()
    if ticker in all_stocks:
        return all_stocks[ticker][0]
    return "Unknown"

def get_sub_industry_for_ticker(ticker: str) -> str:
    """Look up sub-industry for a ticker across all lists."""
    all_stocks = get_all_stocks()
    if ticker in all_stocks:
        return all_stocks[ticker][1]
    return "Unknown"