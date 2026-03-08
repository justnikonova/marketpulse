"""
Market Pulse + Signal Scanner — Combined Streamlit Application
==============================================================
  - Sidebar navigation: Signal Scanner (default) + Market Pulse
  - Lazy data loading: each page loads only what it needs
  - Scanner uses batch yf.download() instead of per-ticker fetching
  - Market Pulse data (bulk prices + market caps) loaded only when that page is active
  - Ticker lists and sector mappings stored in var.py

RUN:  streamlit run app.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta, date
import pytz
import logging

from var import (
    SP500_STOCKS, NASDAQ100_STOCKS,
    SECTOR_COLORS, SECTOR_ETFS,
    get_all_stocks, get_ticker_list, get_sector_for_ticker, get_sub_industry_for_ticker,
)

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MARKET PULSE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    .stApp { background-color: #0e1117; }
    .block-container { padding-top: 1rem; }
    div[data-testid="metric-container"] { background: #1a1d26; border: 1px solid #2d3144; border-radius: 8px; padding: 12px 16px; }
    .metric-label { font-size: 12px !important; color: #888 !important; }
    .stTabs [data-baseweb="tab-list"] { background: #0d1220; border: 1px solid #1e2d4a; border-radius: 8px; gap: 0; }
    .stTabs [data-baseweb="tab"] { color: #8aabcc; font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.03em; padding: 10px 20px; border-radius: 6px; }
    .stTabs [aria-selected="true"] { color: #e0f0ff !important; background: linear-gradient(135deg, #112240 0%, #0d1a30 100%) !important; border: 1px solid #1e3a5f !important; }
    h1, h2, h3 { color: white !important; }
    .stSelectbox label, .stDateInput label, .stRadio label { color: #ccc !important; }
    hr { border-color: #2d3144; }
    section[data-testid="stSidebar"] { background: #0d1220; border-right: 1px solid #1e2d4a; }
    section[data-testid="stSidebar"] .stMarkdown h2, section[data-testid="stSidebar"] .stMarkdown h3 { color: #4fc3f7; font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; letter-spacing: 0.15em; text-transform: uppercase; }
    .scanner-header { background: linear-gradient(135deg, #0d1220 0%, #112240 100%); border: 1px solid #1e3a5f; border-radius: 8px; padding: 24px 32px; margin-bottom: 24px; position: relative; overflow: hidden; }
    .scanner-header::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #00d4ff, #0066ff, #00d4ff); }
    .scanner-title { font-family: 'IBM Plex Mono', monospace; font-size: 1.6rem; font-weight: 600; color: #e0f0ff; letter-spacing: 0.05em; margin: 0; }
    .scanner-subtitle { font-size: 0.85rem; color: #5a7fa8; margin-top: 4px; font-family: 'IBM Plex Mono', monospace; }
    .metric-row { display: flex; gap: 12px; margin-bottom: 20px; }
    .metric-card { flex: 1; background: #0d1220; border: 1px solid #1e2d4a; border-radius: 8px; padding: 16px 20px; text-align: center; }
    .metric-card .metric-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.8rem; font-weight: 600; line-height: 1; }
    .metric-card .metric-label { font-size: 0.72rem; color: #5a7fa8; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 6px; }
    .buy-card { border-color: #00c853; } .sell-card { border-color: #ff1744; } .hold-card { border-color: #ffc107; } .total-card { border-color: #1e3a5f; }
    .buy-val { color: #00e676; } .sell-val { color: #ff4569; } .hold-val { color: #ffd740; } .total-val { color: #4fc3f7; }
    .section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase; color: #4fc3f7; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #1e2d4a; }
    .status-bar { background: #0d1220; border: 1px solid #1e2d4a; border-radius: 6px; padding: 10px 16px; font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: #4fc3f7; margin-bottom: 16px; }
    .stProgress > div > div { background: #00d4ff; }
    .stButton > button { background: linear-gradient(135deg, #0066ff, #00d4ff); color: white; border: none; border-radius: 6px; font-family: 'IBM Plex Mono', monospace; font-weight: 600; padding: 10px 24px; font-size: 0.9rem; }
    label { color: #8aabcc !important; font-size: 0.82rem !important; }
    .dataframe { font-family: 'IBM Plex Mono', monospace !important; font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  LAZY DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

EARNINGS_BLACKOUT = 10


@st.cache_resource(show_spinner=False)
def load_market_pulse_data() -> dict:
    """Lazy: only called when Market Pulse page is active."""
    from concurrent.futures import ThreadPoolExecutor
    ALL_TICKERS = tuple(sorted(SP500_STOCKS.keys()))
    today = date.today()
    start = (today - timedelta(days=548 + 60)).strftime("%Y-%m-%d")  # ~1.5yr + SMA warmup
    end = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        raw = yf.download(list(ALL_TICKERS), start=start, end=end, auto_adjust=True, progress=False, threads=True)
        prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
        if not isinstance(raw.columns, pd.MultiIndex):
            prices.columns = [ALL_TICKERS[0]]
        prices = prices.ffill().dropna(how="all")
    except Exception:
        prices = pd.DataFrame()

    try:
        etf_raw = yf.download(list(SECTOR_ETFS.values()), start=start, end=end, auto_adjust=True, progress=False, threads=True)
        sector_prices = etf_raw["Close"] if isinstance(etf_raw.columns, pd.MultiIndex) else etf_raw[["Close"]]
        if not isinstance(etf_raw.columns, pd.MultiIndex):
            sector_prices.columns = list(SECTOR_ETFS.values())[:1]
        inv = {v: k for k, v in SECTOR_ETFS.items()}
        sector_prices = sector_prices.rename(columns=inv).ffill().dropna(how="all")
    except Exception:
        sector_prices = pd.DataFrame()

    def _cap(ticker):
        try:
            cap = yf.Ticker(ticker).fast_info.market_cap
            return ticker, float(cap) if cap else 1e9
        except Exception:
            return ticker, 1e9

    market_caps = {}
    with ThreadPoolExecutor(max_workers=20) as ex:
        for ticker, cap in ex.map(_cap, ALL_TICKERS):
            market_caps[ticker] = cap

    return {"prices": prices, "sector_prices": sector_prices, "market_caps": market_caps, "fetched_at": datetime.now(), "start": start}


@st.cache_data(ttl=300, show_spinner=False)
def batch_fetch_ohlcv(tickers_tuple: tuple, period_days: int = 420) -> pd.DataFrame:
    """Batch-fetch OHLCV for all scan tickers in ONE yf.download() call."""
    end = datetime.today() + timedelta(days=1)
    start = end - timedelta(days=period_days + 1)
    try:
        raw = yf.download(list(tickers_tuple), start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"),
                          auto_adjust=True, progress=False, threads=True, group_by="ticker")
    except Exception:
        return pd.DataFrame()
    if raw.empty:
        return pd.DataFrame()
    raw.index = pd.to_datetime(raw.index).tz_localize(None)
    return raw.sort_index()


def extract_ticker_df(batch_data: pd.DataFrame, ticker: str, min_rows: int = 60):
    """Extract a single ticker's OHLCV from batch results."""
    if batch_data.empty:
        return None
    try:
        if isinstance(batch_data.columns, pd.MultiIndex):
            if ticker in batch_data.columns.get_level_values(0):
                df = batch_data[ticker].copy()
            else:
                return None
        else:
            df = batch_data.copy()
        df = df.dropna(subset=["Close"])
        return df if len(df) >= min_rows else None
    except Exception:
        return None


@st.cache_data(ttl=300, show_spinner=False)
def fetch_ticker_single(ticker, period_days=400, min_rows=60):
    """Fallback: fetch one ticker individually."""
    try:
        end = datetime.today() + timedelta(days=1)
        start = end - timedelta(days=period_days + 1)
        raw = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        raw = raw.dropna(subset=["Close"])
        if len(raw) < min_rows:
            return None
        raw.index = pd.to_datetime(raw.index).tz_localize(None)
        return raw.sort_index()
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
#  SHARED UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def get_period_dates(period, reference_date=None):
    ref = reference_date or date.today()
    today_str = ref.strftime("%Y-%m-%d")
    period_map = {"1W": timedelta(weeks=1), "2W": timedelta(weeks=2), "1M": timedelta(days=30), "3M": timedelta(days=91), "6M": timedelta(days=182), "1Y": timedelta(days=365), "1.5Y": timedelta(days=548), "5Y": timedelta(days=1825)}
    start = date(ref.year, 1, 1) if period == "YTD" else ref - period_map.get(period, timedelta(days=30))
    return (start - timedelta(days=5)).strftime("%Y-%m-%d"), today_str

def compute_returns(prices, start_date, end_date):
    if prices.empty: return pd.Series(dtype=float)
    prices.index = pd.to_datetime(prices.index)
    all_days = prices.index
    start_avail = all_days[all_days <= pd.Timestamp(start_date)]
    end_avail = all_days[all_days <= pd.Timestamp(end_date)]
    if start_avail.empty or end_avail.empty: return pd.Series(dtype=float)
    end_ts, start_ts = end_avail[-1], start_avail[-1]
    if start_ts == end_ts:
        idx = all_days.get_loc(start_ts)
        if idx == 0: return pd.Series(dtype=float)
        start_ts = all_days[idx - 1]
    return ((prices.loc[end_ts] - prices.loc[start_ts]) / prices.loc[start_ts] * 100).round(2)

def _sma(s, n): return s.rolling(n).mean()
def _rsi(s, p=14):
    d = s.diff(); g = d.clip(lower=0); l = -d.clip(upper=0)
    return 100 - (100 / (1 + g.ewm(alpha=1/p, adjust=False).mean() / l.ewm(alpha=1/p, adjust=False).mean().replace(0, 1e-10)))
def _atr(h, l, c, p=14):
    tr = np.maximum(h - l, np.maximum((h - c.shift()).abs(), (l - c.shift()).abs()))
    return pd.Series(tr, index=c.index).ewm(alpha=1/p, adjust=False).mean()
def _adx(h, l, c, p=14):
    pm = h.diff(); nm = -l.diff(); pm[pm < 0] = 0; nm[nm < 0] = 0; a = _atr(h, l, c, p)
    pdi = 100 * (pm.ewm(alpha=1/p, adjust=False).mean() / a.replace(0, np.nan))
    ndi = 100 * (nm.ewm(alpha=1/p, adjust=False).mean() / a.replace(0, np.nan))
    dx = (abs(pdi - ndi) / (pdi + ndi).replace(0, np.nan)) * 100
    return dx.ewm(alpha=1/p, adjust=False).mean(), pdi, ndi


# ─── Earnings ────────────────────────────────────────────────────────────────
def _safe_to_timestamps(raw):
    if raw is None: return []
    if isinstance(raw, pd.DataFrame):
        if raw.empty: return []
        raw = raw.index
    if isinstance(raw, pd.DatetimeIndex): raw = raw.tolist()
    if not isinstance(raw, (list, np.ndarray)): raw = [raw]
    clean = []
    for d in raw:
        try:
            ts = pd.Timestamp(d)
            if pd.isna(ts): continue
            if ts.tzinfo is not None: ts = ts.tz_convert(None)
            clean.append(ts.normalize())
        except Exception: continue
    return sorted(set(clean))

@st.cache_data(ttl=600, show_spinner=False)
def fetch_earnings_date(ticker):
    tk = yf.Ticker(ticker); all_dates = []
    try:
        edf = tk.get_earnings_dates(limit=12)
        if edf is not None and not edf.empty: all_dates.extend(_safe_to_timestamps(edf.index))
    except Exception: pass
    try:
        cal = tk.calendar
        if cal is not None:
            ed_raw = cal.get("Earnings Date") if isinstance(cal, dict) else (cal.loc["Earnings Date"].values if hasattr(cal, "loc") and "Earnings Date" in cal.index else None)
            if ed_raw is not None: all_dates.extend(_safe_to_timestamps(ed_raw))
    except Exception: pass
    try:
        edp = getattr(tk, "earnings_dates", None)
        if edp is not None: all_dates.extend(_safe_to_timestamps(edp))
    except Exception: pass
    if not all_dates: return None, None
    dates = sorted(set(all_dates)); now = pd.Timestamp.now().normalize()
    future = [d for d in dates if d >= now - timedelta(days=1)]; past = [d for d in dates if d < now]
    if future: nearest = min(future); return nearest.strftime("%Y-%m-%d"), (nearest - now).days
    elif past: nearest = max(past); return nearest.strftime("%Y-%m-%d"), (nearest - now).days
    return None, None

def is_earnings_blocked(days_until):
    return abs(days_until) <= EARNINGS_BLACKOUT if days_until is not None else False


# ─── Scanner Check Functions ─────────────────────────────────────────────────
def compute_daily_checks(df, cfg):
    c = df["Close"]; h = df["High"]; l = df["Low"]
    s50 = _sma(c, 50); s200 = _sma(c, 200) if len(df) >= 200 else pd.Series([np.nan]*len(df), index=c.index)
    r14 = _rsi(c, 14); adx14, pdi14, ndi14 = _adx(h, l, c, 14)
    s50_slope = ((s50.iloc[-1] - s50.iloc[-6]) / s50.iloc[-6] * 100 if len(df) >= 6 and not np.isnan(s50.iloc[-6]) and s50.iloc[-6] != 0 else np.nan)
    close = c.iloc[-1]; rsi_v = r14.iloc[-1]; adx_v = adx14.iloc[-1]; pdi_v = pdi14.iloc[-1]; ndi_v = ndi14.iloc[-1]; di_spread = pdi_v - ndi_v
    checks = {"above_sma50": bool(close > s50.iloc[-1]) if not np.isnan(s50.iloc[-1]) else False, "above_sma200": bool(close > s200.iloc[-1]) if not np.isnan(s200.iloc[-1]) else False,
        "rsi_bull": bool(cfg["d_rsi_min"] <= rsi_v <= cfg["d_rsi_max"]), "adx_trend": bool(cfg["d_adx_min"] <= adx_v <= cfg["d_adx_max"]),
        "sma50_rising": bool(s50_slope >= cfg.get("d_sma50_slope", 0)) if not np.isnan(s50_slope) else False, "di_bull": bool(pdi_v > ndi_v), "di_spread_ok": bool(di_spread >= cfg.get("d_di_spread", 0))}
    values = {"close": round(close, 2), "sma50": round(s50.iloc[-1], 2) if not np.isnan(s50.iloc[-1]) else None, "sma200": round(s200.iloc[-1], 2) if not np.isnan(s200.iloc[-1]) else None,
        "rsi14": round(rsi_v, 1), "adx14": round(adx_v, 1), "+di": round(pdi_v, 1), "-di": round(ndi_v, 1), "di_spread": round(di_spread, 1), "sma50_slope": round(s50_slope, 3) if not np.isnan(s50_slope) else None}
    passed = sum(checks.values()); total = len(checks)
    return {"checks": checks, "values": values, "score": passed, "total": total, "pass": passed == total}

def compute_weekly_checks(df, cfg):
    cw = df["Close"].resample("W").last().dropna(); hw = df["High"].resample("W").max().dropna(); lw = df["Low"].resample("W").min().dropna()
    if len(cw) < 30: return {"checks": {}, "values": {}, "score": 0, "total": 5, "pass": False}
    s10w = _sma(cw, 10); s20w = _sma(cw, 20); r14w = _rsi(cw, 14); adxw, pdiw, ndiw = _adx(hw, lw, cw, 14); h52w = cw.rolling(52, min_periods=26).max()
    close_w = cw.iloc[-1]; rsi_w = r14w.iloc[-1]; adx_w = adxw.iloc[-1]; p52w = close_w / h52w.iloc[-1] if h52w.iloc[-1] > 0 else np.nan
    checks = {"above_sma10w": bool(close_w > s10w.iloc[-1]) if not np.isnan(s10w.iloc[-1]) else False, "above_sma20w": bool(close_w > s20w.iloc[-1]) if not np.isnan(s20w.iloc[-1]) else False,
        "rsi_bull_w": bool(cfg["w_rsi_min"] <= rsi_w <= cfg["w_rsi_max"]), "adx_trend_w": bool(cfg["w_adx_min"] <= adx_w <= cfg["w_adx_max"]),
        "near_52wh_w": bool(cfg["w_pct52_min"] <= p52w <= cfg["w_pct52_max"]) if not np.isnan(p52w) else False}
    values = {"sma10w": round(s10w.iloc[-1], 2) if not np.isnan(s10w.iloc[-1]) else None, "sma20w": round(s20w.iloc[-1], 2) if not np.isnan(s20w.iloc[-1]) else None,
        "w_rsi14": round(rsi_w, 1), "w_adx14": round(adx_w, 1), "w_pct52": round(p52w, 3) if not np.isnan(p52w) else None}
    passed = sum(checks.values()); total = len(checks)
    return {"checks": checks, "values": values, "score": passed, "total": total, "pass": passed == total}

@st.cache_data(ttl=300, show_spinner=False)
def compute_market_checks(cfg):
    spy_df = fetch_ticker_single("SPY", 400); vix_df = fetch_ticker_single("^VIX", 60, min_rows=1)
    spy_ok = vix_ok = False; spy_rsi = spy_price = spy_sma200 = vix_val = None
    if spy_df is not None and len(spy_df) >= 200:
        c = spy_df["Close"]; s200 = _sma(c, 200); r14 = _rsi(c, 14)
        spy_price = round(c.iloc[-1], 2); spy_sma200 = round(s200.iloc[-1], 2); spy_rsi = round(r14.iloc[-1], 1); spy_ok = bool(c.iloc[-1] > s200.iloc[-1])
    if vix_df is not None and len(vix_df) > 0:
        vix_val = round(vix_df["Close"].iloc[-1], 2); vix_ok = bool(cfg["vix_min"] <= vix_val <= cfg["vix_max"])
    return {"checks": {"spy_above_200": spy_ok, "vix_below_threshold": vix_ok}, "values": {"spy_price": spy_price, "spy_sma200": spy_sma200, "spy_rsi14": spy_rsi, "vix": vix_val}, "score": sum([spy_ok, vix_ok]), "total": 2, "pass": spy_ok and vix_ok}

def score_to_signal(daily, weekly, earnings_blocked=False):
    wc = weekly.get("checks", {}); dc = daily.get("checks", {})
    if (not wc.get("above_sma10w", True) and not wc.get('di_bull', True)) or (not dc.get("above_sma50", True)): return "SELL"    
    if daily["pass"] and weekly["pass"]: return "BLOCKED" if earnings_blocked else "BUY"
    return "HOLD"


# ─── Scanner Multi-Panel Chart Builder ───────────────────────────────────────
from plotly.subplots import make_subplots

def build_scanner_chart(ticker: str, df_daily: pd.DataFrame, title_suffix: str = ""):
    """
    Build a 3-row chart for a given timeframe (daily or weekly):
      Row 1: Price with SMA 5/20/50/200 + ADX DI+/DI-
      Row 2: RSI 14
    Returns a Plotly figure.
    """
    if df_daily is None or df_daily.empty or len(df_daily) < 20:
        return None

    c = df_daily["Close"]; h = df_daily["High"]; l = df_daily["Low"]

    # SMAs
    sma5 = _sma(c, 5); sma20 = _sma(c, 20); sma50 = _sma(c, 50)
    sma200 = _sma(c, 200) if len(df_daily) >= 200 else pd.Series([np.nan]*len(df_daily), index=c.index)

    # Indicators
    rsi14 = _rsi(c, 14)
    adx14, pdi14, ndi14 = _adx(h, l, c, 14)

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.55, 0.22, 0.23],
        subplot_titles=[None, None, None],
    )

    # ── Row 1: Price + SMAs ──────────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=df_daily.index, open=df_daily["Open"], high=h, low=l, close=c,
        name="Price", increasing_line_color="#26a69a", decreasing_line_color="#ef5350",
        showlegend=False,
    ), row=1, col=1)

    for name, series, color, width in [
        ("SMA 5", sma5, "#ffffff", 1.0), ("SMA 20", sma20, "#0c2ce6", 1.2),
        ("SMA 50", sma50, "#b623f5", 1.5), ("SMA 200", sma200, "#e7b111", 1.5),
    ]:
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values, mode="lines", name=name,
            line=dict(color=color, width=width),
        ), row=1, col=1)

    # ── Row 2: ADX + DI+/DI- ────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=adx14.index, y=adx14.values, mode="lines", name="ADX",
        line=dict(color="#4fc3f7", width=1.5),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=pdi14.index, y=pdi14.values, mode="lines", name="+DI",
        line=dict(color="#00e676", width=1.2),
    ), row=2, col=1)
    # fig.add_trace(go.Scatter(
    #     x=ndi14.index, y=ndi14.values, mode="lines", name="-DI",
    #     line=dict(color="#ff4569", width=1.2),
    # ), row=2, col=1)
    fig.add_hline(y=25, line_dash="dot", line_color="rgba(255,255,255,0.2)", line_width=1, row=2, col=1)

    # ── Row 3: RSI ───────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=rsi14.index, y=rsi14.values, mode="lines", name="RSI 14",
        line=dict(color="#ce93d8", width=1.5),
    ), row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="rgba(255,100,100,0.4)", line_width=1, row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="rgba(100,255,100,0.4)", line_width=1, row=3, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="rgba(255,255,255,0.15)", line_width=1, row=3, col=1)

    # ── Layout ───────────────────────────────────────────────────────────
    sector, sub = get_all_stocks().get(ticker, ("", ""))
    ret_pct = (c.iloc[-1] - c.iloc[0]) / c.iloc[0] * 100 if len(c) > 1 else 0
    ret_color = "#00e676" if ret_pct >= 0 else "#ff4569"

    fig.update_layout(
        title=dict(
            text=(f"<b>{ticker}</b>  "
                  f"<span style='font-size:12px;color:#8aabcc'>{sub} · {sector}</span>  "
                  f"<span style='color:{ret_color};font-size:13px'>{ret_pct:+.2f}%</span>  "
                  f"<span style='font-size:11px;color:#5a7fa8'>{title_suffix}</span>"),
            font=dict(size=14, color="white"), x=0.01,
        ),
        xaxis3=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#aaa", size=9)),
        yaxis=dict(title="Price", showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#aaa", size=9), tickprefix="$"),
        yaxis2=dict(title="ADX / DI", showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#aaa", size=9)),
        yaxis3=dict(title="RSI", showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#aaa", size=9), range=[10, 90]),
        legend=dict(orientation="h", x=0.0, y=1.06, font=dict(color="#aaa", size=9), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=60, l=55, r=15, b=30),
        paper_bgcolor="#0e1117", plot_bgcolor="#131720",
        font_color="white", height=560,
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1a1d26", font_color="white"),
    )

    return fig


# ═══════════════════════════════════════════════════════════════════════════════
#  MARKET PULSE — Chart Builders (unchanged logic, just functions)
# ═══════════════════════════════════════════════════════════════════════════════

PERIOD_TO_FRAME_INTERVAL = {"1W": "D", "2W": "D", "1M": "W", "3M": "W", "6M": "ME", "YTD": "ME", "1Y": "ME", "1.5Y": "QE", "Custom": "W"}
FRAME_LABEL_FMT = {"D": "%b %d, %Y", "W": "Week of %b %d, %Y", "ME": "%B %Y", "QE": "Q%q %Y"}
def freq_label(freq): return {"D": "daily", "W": "weekly", "ME": "monthly", "QE": "quarterly"}.get(freq, freq)
def format_checkpoint_label(ts, freq):
    if freq == "QE": return f"Q{(ts.month - 1) // 3 + 1} {ts.year}"
    return ts.strftime(FRAME_LABEL_FMT.get(freq, "%b %d, %Y"))

def get_animation_checkpoints(prices, period, start_date, end_date):
    freq = PERIOD_TO_FRAME_INTERVAL.get(period, "W"); prices.index = pd.to_datetime(prices.index); trading_days = prices.loc[start_date:end_date].index
    if trading_days.empty: return []
    if freq == "D": checkpoints = trading_days.tolist()
    else:
        date_range = pd.date_range(start=trading_days[0], end=trading_days[-1], freq=freq); checkpoints = []
        for d in date_range:
            available = trading_days[trading_days <= d]
            if not available.empty: checkpoints.append(available[-1])
    if checkpoints and checkpoints[-1] != trading_days[-1]: checkpoints.append(trading_days[-1])
    seen = set(); unique = []
    for c in checkpoints:
        key = c.date()
        if key not in seen: seen.add(key); unique.append(c)
    return unique

_COLORSCALE = [[0.0, "#cc2200"], [0.25, "#8b0000"], [0.5, "#1a1a1a"], [0.75, "#1a7a1a"], [1.0, "#00cc00"]]
_DARK_BG = "#0e1117"

def build_heatmap(returns, market_caps, title, color_range=10.0, stock_map=None):
    if stock_map is None: stock_map = SP500_STOCKS
    stock_rows = []
    for ticker, (sector, sub) in stock_map.items():
        if ticker not in returns.index: continue
        ret = float(returns[ticker]); cap = market_caps.get(ticker, 1e9) or 1e9
        stock_rows.append({"id": ticker, "label": f"{ticker}<br>{ret:+.2f}%", "parent": sector, "value": cap, "color": ret, "hover_ticker": ticker, "hover_ret": ret, "hover_sub": sub})
    if not stock_rows:
        fig = go.Figure(); fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=18, color="white")); fig.update_layout(paper_bgcolor=_DARK_BG, height=600); return fig
    df_stocks = pd.DataFrame(stock_rows); sector_rows = []
    for sector in df_stocks["parent"].unique():
        mask = df_stocks["parent"] == sector; sector_rows.append({"id": sector, "label": sector, "parent": "", "value": df_stocks.loc[mask, "value"].sum(), "color": df_stocks.loc[mask, "color"].mean(), "hover_ticker": sector, "hover_ret": df_stocks.loc[mask, "color"].mean(), "hover_sub": "Sector"})
    df = pd.concat([pd.DataFrame(sector_rows), df_stocks], ignore_index=True)
    customdata = np.column_stack([df["hover_ticker"].values, df["hover_ret"].values.astype(float), df["hover_sub"].values])
    fig = go.Figure(go.Treemap(ids=df["id"].tolist(), labels=df["label"].tolist(), parents=df["parent"].tolist(), values=df["value"].tolist(), customdata=customdata,
        hovertemplate="<b>%{customdata[0]}</b><br>Return: %{customdata[1]:+.2f}%<br>Industry: %{customdata[2]}<br>Market Cap: $%{value:,.0f}<extra></extra>",
        marker=dict(colors=df["color"].tolist(), colorscale=_COLORSCALE, cmin=-color_range, cmid=0, cmax=color_range, colorbar=dict(title="% Change", tickformat="+.1f", ticksuffix="%", len=0.6, thickness=15, tickfont=dict(color="white")), showscale=True),
        textfont=dict(size=11, color="white"), pathbar=dict(visible=True, thickness=20), tiling=dict(packing="squarify", pad=2), branchvalues="total"))
    fig.update_layout(title=dict(text=title, font=dict(size=16, color="white"), x=0.01), margin=dict(t=50, l=10, r=10, b=10), paper_bgcolor=_DARK_BG, plot_bgcolor=_DARK_BG, font_color="white", height=620)
    return fig

def build_sector_heatmap(returns, market_caps, title, color_range=10.0, stock_map=None):
    if stock_map is None: stock_map = SP500_STOCKS
    sector_data = {}
    for ticker, (sector, sub) in stock_map.items():
        if ticker not in returns.index: continue
        ret = float(returns[ticker]); cap = market_caps.get(ticker, 1e9) or 1e9
        if sector not in sector_data: sector_data[sector] = {"weighted_ret": 0.0, "total_cap": 0.0, "n": 0, "gainers": 0, "losers": 0, "tickers": []}
        sector_data[sector]["weighted_ret"] += ret * cap; sector_data[sector]["total_cap"] += cap; sector_data[sector]["n"] += 1
        sector_data[sector]["gainers"] += 1 if ret > 0 else 0; sector_data[sector]["losers"] += 1 if ret < 0 else 0; sector_data[sector]["tickers"].append((ticker, ret))
    if not sector_data:
        fig = go.Figure(); fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=18, color="white")); fig.update_layout(paper_bgcolor=_DARK_BG, height=620); return fig
    ids, labels, parents, values, colors, customdata = ["S&P 500"], ["S&P 500"], [""], [sum(d["total_cap"] for d in sector_data.values())], [0.0], [["S&P 500", 0.0, "", 0, 0]]
    for sector, d in sorted(sector_data.items(), key=lambda x: -x[1]["total_cap"]):
        cap = d["total_cap"]; wret = round(d["weighted_ret"] / cap if cap > 0 else 0.0, 2); ts = sorted(d["tickers"], key=lambda x: x[1])
        ids.append(sector); labels.append(f"<b>{sector}</b><br>{wret:+.2f}%"); parents.append("S&P 500"); values.append(cap); colors.append(wret)
        customdata.append([sector, wret, f"↑{ts[-1][0]} {ts[-1][1]:+.1f}%  ↓{ts[0][0]} {ts[0][1]:+.1f}%" if ts else "—", d["gainers"], d["losers"]])
    fig = go.Figure(go.Treemap(ids=ids, labels=labels, parents=parents, values=values, customdata=np.array(customdata, dtype=object),
        hovertemplate="<b>%{customdata[0]}</b><br>Wtd Avg Return: %{customdata[1]:+.2f}%<br>%{customdata[2]}<br>Gainers: %{customdata[3]}  Losers: %{customdata[4]}<br>Total Mkt Cap: $%{value:,.0f}<extra></extra>",
        marker=dict(colors=colors, colorscale=_COLORSCALE, cmin=-color_range, cmid=0, cmax=color_range, showscale=True, colorbar=dict(title="Wtd Avg %", tickformat="+.1f", ticksuffix="%", len=0.6, thickness=15, tickfont=dict(color="white"))),
        textfont=dict(size=14, color="white"), pathbar=dict(visible=False), tiling=dict(packing="squarify", pad=3), branchvalues="total", maxdepth=2))
    fig.update_layout(title=dict(text=title, font=dict(size=16, color="white"), x=0.01), margin=dict(t=50, l=10, r=10, b=10), paper_bgcolor=_DARK_BG, plot_bgcolor=_DARK_BG, font_color="white", height=620)
    return fig

def build_diff_heatmap(ra, rb, mc, title):
    common = ra.index.intersection(rb.index); return build_heatmap(rb[common] - ra[common], mc, title, color_range=10.0)

def build_sector_diff_heatmap(returns_a, returns_b, market_caps, title, color_range=10.0, stock_map=None):
    if stock_map is None: stock_map = SP500_STOCKS
    common = returns_a.index.intersection(returns_b.index); sector_a, sector_b = {}, {}
    for d_dict, rets in [(sector_a, returns_a), (sector_b, returns_b)]:
        for t, (s, _) in stock_map.items():
            if t not in common: continue
            cap = market_caps.get(t, 1e9) or 1e9; ret = float(rets[t])
            if s not in d_dict: d_dict[s] = {"weighted_ret": 0.0, "total_cap": 0.0}
            d_dict[s]["weighted_ret"] += ret * cap; d_dict[s]["total_cap"] += cap
    all_sectors = set(sector_a.keys()) | set(sector_b.keys())
    if not all_sectors:
        fig = go.Figure(); fig.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=18, color="white")); fig.update_layout(paper_bgcolor=_DARK_BG, height=620); return fig
    ids, labels, parents, values, colors, customdata = ["S&P 500"], ["S&P 500"], [""], [sum(d["total_cap"] for d in sector_a.values())], [0.0], [["S&P 500", 0, 0, 0, ""]]
    for sector in sorted(all_sectors, key=lambda s: -(sector_a.get(s, {}).get("total_cap", 0))):
        da = sector_a.get(sector, {"weighted_ret": 0, "total_cap": 1e9}); db = sector_b.get(sector, {"weighted_ret": 0, "total_cap": 1e9}); cap = da["total_cap"]
        ret_a = round(da["weighted_ret"] / cap if cap else 0, 2); ret_b = round(db["weighted_ret"] / cap if cap else 0, 2); diff = round(ret_b - ret_a, 2)
        st_list = sorted([(t, float(returns_b[t]) - float(returns_a[t])) for t, (s, _) in stock_map.items() if s == sector and t in common], key=lambda x: x[1])
        ids.append(sector); labels.append(f"<b>{sector}</b><br>Δ {diff:+.2f}%"); parents.append("S&P 500"); values.append(cap); colors.append(diff)
        customdata.append([sector, diff, ret_a, ret_b, f"↑{st_list[-1][0]} {st_list[-1][1]:+.1f}%  ↓{st_list[0][0]} {st_list[0][1]:+.1f}%" if st_list else "—"])
    fig = go.Figure(go.Treemap(ids=ids, labels=labels, parents=parents, values=values, customdata=np.array(customdata, dtype=object),
        hovertemplate="<b>%{customdata[0]}</b><br>Δ (B−A): %{customdata[1]:+.2f}%<br>A: %{customdata[2]:+.2f}%<br>B: %{customdata[3]:+.2f}%<br>%{customdata[4]}<br>Cap: $%{value:,.0f}<extra></extra>",
        marker=dict(colors=colors, colorscale=_COLORSCALE, cmin=-color_range, cmid=0, cmax=color_range, showscale=True, colorbar=dict(title="Δ %", tickformat="+.1f", ticksuffix="%", len=0.6, thickness=15, tickfont=dict(color="white"))),
        textfont=dict(size=14, color="white"), pathbar=dict(visible=False), tiling=dict(packing="squarify", pad=3), branchvalues="total", maxdepth=2))
    fig.update_layout(title=dict(text=title, font=dict(size=16, color="white"), x=0.01), margin=dict(t=50, l=10, r=10, b=10), paper_bgcolor=_DARK_BG, plot_bgcolor=_DARK_BG, font_color="white", height=620)
    return fig

def build_animated_heatmap(prices, market_caps, period, start_date, end_date, color_range=10.0, selected_sectors=None, stock_map=None):
    if stock_map is None: stock_map = SP500_STOCKS
    freq = PERIOD_TO_FRAME_INTERVAL.get(period, "W"); checkpoints = get_animation_checkpoints(prices, period, start_date, end_date)
    if len(checkpoints) < 2:
        fig = go.Figure(); fig.add_annotation(text="Not enough data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="white")); fig.update_layout(paper_bgcolor=_DARK_BG, height=620); return fig
    prices.index = pd.to_datetime(prices.index); anchor_prices = prices.loc[start_date:].iloc[0]
    stock_filter = {t: v for t, v in stock_map.items() if selected_sectors is None or v[0] in selected_sectors}
    frames = []
    for cp in checkpoints:
        snap = prices.loc[:cp].iloc[-1]; stock_rows, sector_agg = [], {}
        for t, (s, sub) in stock_filter.items():
            if t not in snap.index or t not in anchor_prices.index: continue
            base = anchor_prices[t]
            if base == 0 or pd.isna(base): continue
            ret = round(float((snap[t] - base) / base * 100), 2); cap = market_caps.get(t, 1e9) or 1e9
            stock_rows.append({"id": t, "label": f"{t}<br>{ret:+.2f}%", "parent": s, "value": cap, "color": ret, "cd0": t, "cd1": ret, "cd2": sub})
            if s not in sector_agg: sector_agg[s] = {"ret_sum": 0, "count": 0, "cap": 0}
            sector_agg[s]["ret_sum"] += ret; sector_agg[s]["count"] += 1; sector_agg[s]["cap"] += cap
        sr = [{"id": s, "label": s, "parent": "", "value": d["cap"], "color": d["ret_sum"]/d["count"] if d["count"] else 0, "cd0": s, "cd1": d["ret_sum"]/d["count"] if d["count"] else 0, "cd2": "Sector"} for s, d in sector_agg.items()]
        all_r = sr + stock_rows
        if not all_r: continue
        df = pd.DataFrame(all_r); label = format_checkpoint_label(cp, freq)
        cd = np.column_stack([df["cd0"].values, df["cd1"].values.astype(float), df["cd2"].values])
        frames.append(go.Frame(data=[go.Treemap(ids=df["id"].tolist(), labels=df["label"].tolist(), parents=df["parent"].tolist(), values=df["value"].tolist(), customdata=cd,
            hovertemplate="<b>%{customdata[0]}</b><br>Return: %{customdata[1]:+.2f}%<br>Industry: %{customdata[2]}<br>Cap: $%{value:,.0f}<extra></extra>",
            marker=dict(colors=df["color"].tolist(), colorscale=_COLORSCALE, cmin=-color_range, cmid=0, cmax=color_range, showscale=True, colorbar=dict(title=dict(text="% Change", font=dict(color="white")), tickformat="+.1f", ticksuffix="%", len=0.6, thickness=15, tickfont=dict(color="white"))),
            textfont=dict(size=11, color="white"), branchvalues="total")], name=label, layout=go.Layout(title_text=f"S&P 500 — {label}")))
    if not frames:
        fig = go.Figure(); fig.add_annotation(text="No frames", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="white")); fig.update_layout(paper_bgcolor=_DARK_BG, height=620); return fig
    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(title=dict(text=f"Animation — {period} · {freq_label(freq)} · {len(frames)} steps", font=dict(size=15, color="white"), x=0.01), margin=dict(t=60, l=10, r=10, b=120), paper_bgcolor=_DARK_BG, plot_bgcolor=_DARK_BG, font_color="white", height=700,
        sliders=[{"active": 0, "currentvalue": {"prefix": "📅 ", "font": {"size": 14, "color": "white"}, "visible": True}, "pad": {"t": 50, "b": 10}, "len": 0.88, "x": 0.06, "bgcolor": "#1a1d26", "bordercolor": "#2d3144", "font": {"color": "white", "size": 10},
            "steps": [{"args": [[f.name], {"frame": {"duration": 600, "redraw": True}, "mode": "immediate", "transition": {"duration": 300}}], "label": f.name, "method": "animate"} for f in frames]}],
        updatemenus=[{"type": "buttons", "showactive": False, "x": 0, "y": -0.05, "xanchor": "left", "yanchor": "top", "bgcolor": "#1a1d26", "bordercolor": "#2d3144", "font": {"color": "white"},
            "buttons": [{"label": "▶  Play", "method": "animate", "args": [None, {"frame": {"duration": 800, "redraw": True}, "fromcurrent": True, "transition": {"duration": 300, "easing": "cubic-in-out"}}]},
                {"label": "⏸  Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]}]}])
    return fig

def build_sector_trend_fig(sector, prices, start_date, sma_window=50, line_color="#00b4d8"):
    if sector not in prices.columns: return None
    prices.index = pd.to_datetime(prices.index); series = prices[sector].loc[start_date:]
    if series.empty or len(series) < 2: return None
    base = series.iloc[0]; pct = ((series - base) / base * 100).round(3); sma = pct.rolling(window=sma_window, min_periods=1).mean().round(3)
    day_ret = float(pct.iloc[-1] - pct.iloc[-2]) if len(pct) > 1 else 0.0; total_ret = float(pct.iloc[-1])
    r, g, b = int(line_color[1:3], 16), int(line_color[3:5], 16), int(line_color[5:7], 16)
    fig = go.Figure()
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.25)", line_width=1)
    fig.add_trace(go.Scatter(x=sma.index, y=sma.values, mode="lines", name=f"SMA {sma_window}", line=dict(color="#f5a623", width=1.8)))
    fig.add_trace(go.Scatter(x=pct.index, y=pct.values, mode="lines", name="% Return", line=dict(color=line_color, width=2), fill="tozeroy", fillcolor=f"rgba({r},{g},{b},0.15)"))
    fig.add_annotation(x=pct.index[-1], y=total_ret, text=f"<b>{total_ret:+.2f}%</b>", showarrow=False, xanchor="left", font=dict(color="#00cc44" if total_ret >= 0 else "#ff4444", size=12), xshift=6)
    fig.update_layout(title=dict(text=f"<b>{sector}</b><span style='font-size:11px;color:#888'>   SMA{sma_window} · {sma.iloc[-1]:+.2f}%</span>   <span style='color:{'#00cc44' if day_ret >= 0 else '#ff4444'};font-size:12px'>{day_ret:+.2f}% today</span>", font=dict(size=14, color="white"), x=0.01),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#aaa", size=10), tickformat="%b '%y"), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#aaa", size=10), ticksuffix="%", tickformat="+.1f", title=dict(text="% Return", font=dict(color="#888", size=10))),
        legend=dict(orientation="h", x=0.01, y=1.08, font=dict(color="#aaa", size=10), bgcolor="rgba(0,0,0,0)"), margin=dict(t=55, l=55, r=40, b=35), paper_bgcolor=_DARK_BG, plot_bgcolor="#131720", height=320, hovermode="x unified")
    return fig

def build_stock_chart(ticker, prices, start_date, end_date, stock_map=None):
    if stock_map is None: stock_map = SP500_STOCKS
    if ticker not in prices.columns: return None
    prices.index = pd.to_datetime(prices.index); all_s = prices[ticker].dropna()
    if all_s.empty: return None
    avail = all_s.index; st_ts = avail[avail <= pd.Timestamp(start_date)]; et_ts = avail[avail <= pd.Timestamp(end_date)]
    if st_ts.empty or et_ts.empty: return None
    display = all_s.loc[st_ts[-1]:et_ts[-1]]
    if display.empty or len(display) < 2: return None
    sma5 = all_s.rolling(5, min_periods=1).mean().loc[st_ts[-1]:et_ts[-1]]; sma20 = all_s.rolling(20, min_periods=1).mean().loc[st_ts[-1]:et_ts[-1]]
    ret_pct = (display.iloc[-1] - display.iloc[0]) / display.iloc[0] * 100
    av = pd.concat([display, sma5, sma20]).dropna(); y_min = av.min(); y_max = av.max(); y_pad = (y_max - y_min) * 0.05 if y_max != y_min else y_max * 0.05
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sma20.index, y=sma20.values, mode="lines", name="SMA 20", line=dict(color="#00b4d8", width=1.5)))
    fig.add_trace(go.Scatter(x=sma5.index, y=sma5.values, mode="lines", name="SMA 5", line=dict(color="#ffe066", width=1.2)))
    fig.add_trace(go.Scatter(x=display.index, y=display.values, mode="lines", name="Price", line=dict(color="#ffffff", width=2)))
    sector, sub = stock_map.get(ticker, get_all_stocks().get(ticker, ("", "")))
    fig.update_layout(title=dict(text=f"<b>{ticker}</b>  <span style='font-size:12px;color:#aaa'>{sub} · {sector}</span>  <span style='color:{'#00cc44' if ret_pct >= 0 else '#ff4444'};font-size:13px'>{ret_pct:+.2f}%</span>", font=dict(size=15, color="white"), x=0.01),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#aaa", size=10), tickformat="%b '%y", rangeslider=dict(visible=False)),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#aaa", size=10), tickprefix="$", range=[y_min-(y_max-y_min)*0.10, y_max+y_pad], title=dict(text="Price", font=dict(color="#888", size=10))),
        legend=dict(orientation="h", x=0.01, y=1.08, font=dict(color="#ccc", size=11), bgcolor="rgba(0,0,0,0)"), margin=dict(t=70, l=60, r=20, b=40), paper_bgcolor=_DARK_BG, plot_bgcolor="#131720", height=420, hovermode="x unified")
    return fig

def show_metrics(returns, label):
    if returns.empty: return
    g = (returns > 0).sum(); lo = (returns < 0).sum(); avg = returns.mean(); bt = returns.idxmax(); wt = returns.idxmin()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(f"📈 Gainers ({label})", g); c2.metric(f"📉 Losers ({label})", lo); c3.metric(f"〜 Avg ({label})", f"{avg:+.2f}%"); c4.metric(f"🏆 Best ({label})", f"{bt} {returns.max():+.1f}%"); c5.metric(f"💀 Worst ({label})", f"{wt} {returns.min():+.1f}%")


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — Navigation (Scanner is DEFAULT)
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🧭 Navigation")
    page = st.radio("Navigation", ["📡 Signal Scanner", "📊 Market Pulse"], label_visibility="collapsed")

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: SIGNAL SCANNER (default — no upfront data load)
# ═══════════════════════════════════════════════════════════════════════════════

if page == "📡 Signal Scanner":
    with st.sidebar:
        st.markdown("---"); st.markdown("### ⚙ Scanner Config"); 
        scan_mode = st.selectbox("Scan Universe", ["Custom Watchlist", "S&P 500", "NASDAQ 100"])
        custom_input = ""
        if scan_mode == "Custom Watchlist": custom_input = st.text_area("Tickers", value="AAPL, NVDA, MSFT, AMZN, META, TSLA, GOOGL, AMD, LRCX, MU", height=120)
        st.markdown("---"); st.markdown("### 📅 Daily Filters")
        d_rsi_min, d_rsi_max = st.slider("RSI14 range", 0, 100, (50, 80), 1); d_adx_min, d_adx_max = st.slider("ADX14 range", 0, 100, (22, 73), 1)
        d_di_spread = st.slider("Min DI Spread", 0, 40, 15, 1); d_sma50_slope = st.slider("Min SMA50 slope (%)", 0.0, 3.0, 1.50, 0.05, format="%.2f")
        st.markdown("---"); st.markdown("### 📆 Weekly Filters")
        w_rsi_min, w_rsi_max = st.slider("Weekly RSI14 range", 0, 100, (55, 80), 1); w_adx_min, w_adx_max = st.slider("Weekly ADX14 range", 0, 100, (15, 73), 1)
        w_pct52_min, w_pct52_max = st.slider("52-week high range", 0.50, 1.00, (0.90, 1.00), 0.01, format="%.2f")
        st.markdown("---"); st.markdown("### 🌍 Market Filters"); vix_min, vix_max = st.slider("VIX range", 0, 80, (0, 22), 1)
        st.markdown("---")
        run_scan = st.button("▶  RUN SCAN", width="stretch")
        if st.button("🔄 Force Reload", width="stretch"):
            st.cache_resource.clear(); st.cache_data.clear(); st.rerun()

    st.markdown("""<div class="scanner-header"><div class="scanner-title">📡 SIGNAL SCANNER</div><div class="scanner-subtitle">Earnings blackout ±10d (BLOCKED) · SMA50 slope >= 1.50% · v2 exit logic</div></div>""", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Market Conditions</div>', unsafe_allow_html=True)
    cfg = {"d_rsi_min": d_rsi_min, "d_rsi_max": d_rsi_max, "d_adx_min": d_adx_min, "d_adx_max": d_adx_max, "d_di_spread": d_di_spread, "d_sma50_slope": d_sma50_slope,
        "w_rsi_min": w_rsi_min, "w_rsi_max": w_rsi_max, "w_adx_min": w_adx_min, "w_adx_max": w_adx_max, "w_pct52": w_pct52_min, "w_pct52_min": w_pct52_min, "w_pct52_max": w_pct52_max, "vix_min": vix_min, "vix_max": vix_max}

    # ── Stale filter detection: show hint when filters changed since last scan ──
    if "scan_results" in st.session_state:
        last_cfg = st.session_state.get("scan_cfg", {})
        if last_cfg and last_cfg != cfg:
            st.warning("⚠️ Filter settings have changed since the last scan. Press **▶ RUN SCAN** to apply the new filters.", icon="🔄")

    with st.spinner("Loading market data..."): mkt = compute_market_checks(cfg)
    _et = pytz.timezone("America/New_York"); _now_et = datetime.now(_et); _wd = _now_et.weekday(); _hm = _now_et.hour * 100 + _now_et.minute
    _sl = "🟢 OPEN" if _wd < 5 and 930 <= _hm <= 1600 else ("🟡 PRE-MKT" if _wd < 5 and 400 <= _hm < 930 else ("🟡 AFTER-HRS" if _wd < 5 and 1600 < _hm <= 2000 else "🔴 CLOSED"))
    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    with mc1: st.metric("Session", _sl)
    with mc2: st.metric("SPY", f"${mkt['values'].get('spy_price', '—')}")
    with mc3: st.metric("SPY/200", f"{'🟢' if mkt['checks'].get('spy_above_200') else '🔴'} {'▲' if mkt['checks'].get('spy_above_200') else '▼'}")
    with mc4: st.metric("VIX", f"{'🟢' if mkt['checks'].get('vix_below_threshold') else '🔴'} {mkt['values'].get('vix', '—')}")
    with mc5: st.metric("Gate", "✅" if mkt["pass"] else "⛔")
    st.markdown("---")

    if run_scan:
        raw_tickers = ([t.strip().upper() for t in custom_input.replace("\n", ",").split(",") if t.strip()] if scan_mode == "Custom Watchlist"
            else get_ticker_list("S&P 500") if scan_mode == "S&P 500" else get_ticker_list("NASDAQ 100") if scan_mode == "NASDAQ 100" else [])
        all_stock_map = get_all_stocks(); total = len(raw_tickers)
        st.markdown(f'<div class="section-label">Scanning {total} tickers</div>', unsafe_allow_html=True)
        prog = st.progress(0, text="📡 Batch downloading OHLCV data...")
        batch_data = batch_fetch_ohlcv(tuple(raw_tickers), period_days=420)
        prog.progress(0.3, text="📊 Processing signals...")
        results = []
        for i, ticker in enumerate(raw_tickers):
            prog.progress(0.3 + 0.7 * (i + 1) / total, text=f"Analyzing {ticker}  [{i + 1}/{total}]")
            df = extract_ticker_df(batch_data, ticker, min_rows=60)
            if df is None: df = fetch_ticker_single(ticker, 420)
            if df is None or len(df) < 60: continue
            daily = compute_daily_checks(df, cfg); weekly = compute_weekly_checks(df, cfg)
            earn_date, earn_days = fetch_earnings_date(ticker); earn_blocked = is_earnings_blocked(earn_days)
            signal = score_to_signal(daily, weekly, earnings_blocked=earn_blocked)
            dv = daily["values"]; wv = weekly["values"]; dc = daily["checks"]; wc = weekly["checks"]; close_price = dv.get("close") or 0.0
            # Sector lookup: static dict first, then yfinance fallback
            if ticker in all_stock_map:
                sector_name = all_stock_map[ticker][0]
            else:
                try:
                    info = yf.Ticker(ticker).info
                    sector_name = info.get("sector", "Unknown")
                except Exception:
                    sector_name = "Unknown"

            # Earnings display with better handling
            if earn_date and earn_days is not None:
                earn_display = f"{earn_date} ({earn_days}d)" if earn_days >= 0 else f"{earn_date} ({earn_days}d ago)"
            else:
                earn_display = "N/A"
            results.append({"Ticker": ticker, "Sector": sector_name, "Signal": signal, "Price": close_price, "Entry": round(close_price, 2), "Target": round(close_price * 1.10, 2), "Stop": round(close_price * 0.915, 2),
                "Earnings": earn_display, "Earn ⛔": "⛔" if earn_blocked else "✓", "D.Pass": f"{daily['score']}/{daily['total']}", "W.Pass": f"{weekly['score']}/{weekly['total']}",
                ">SMA50": "✓" if dc.get("above_sma50") else "✗", ">SMA200": "✓" if dc.get("above_sma200") else "✗", "D.RSI14": dv.get("rsi14"), "D.ADX14": dv.get("adx14"),
                "SMA50↑": "✓" if dc.get("sma50_rising") else "✗", "+DI>-DI": "✓" if dc.get("di_bull") else "✗", "DI≥15": "✓" if dc.get("di_spread_ok") else "✗",
                ">SMA10W": "✓" if wc.get("above_sma10w") else "✗", ">SMA20W": "✓" if wc.get("above_sma20w") else "✗", "W.RSI14": wv.get("w_rsi14"), "W.ADX14": wv.get("w_adx14"),
                "W.Pct52H": f"{wv.get('w_pct52', 0) * 100:.1f}%" if wv.get("w_pct52") else "—"})
        prog.empty()
        if not results: st.warning("No data returned."); st.stop()
        st.session_state["scan_results"] = pd.DataFrame(results); st.session_state["scan_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state["scan_batch_data"] = batch_data
        st.session_state["scan_cfg"] = cfg.copy()  # store config for stale-filter detection

    if "scan_results" in st.session_state:
        df_r = st.session_state["scan_results"].copy()
        buys = df_r[df_r["Signal"] == "BUY"]; holds = df_r[df_r["Signal"] == "HOLD"]; sells = df_r[df_r["Signal"] == "SELL"]; blocked = df_r[df_r["Signal"] == "BLOCKED"]
        st.markdown(f'<div class="status-bar">🕐 Last scan: {st.session_state.get("scan_time", "—")} | {len(df_r)} tickers</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="metric-row"><div class="metric-card buy-card"><div class="metric-value buy-val">{len(buys)}</div><div class="metric-label">🟢 BUY</div></div>
            <div class="metric-card hold-card"><div class="metric-value hold-val">{len(holds)}</div><div class="metric-label">🟡 HOLD</div></div>
            <div class="metric-card sell-card"><div class="metric-value sell-val">{len(sells)}</div><div class="metric-label">🔴 SELL</div></div>
            <div class="metric-card" style="border-color:#ab47bc;"><div class="metric-value" style="color:#ce93d8;">{len(blocked)}</div><div class="metric-label">🚫 BLOCKED</div></div>
            <div class="metric-card total-card"><div class="metric-value total-val">{len(df_r)}</div><div class="metric-label">📊 Total</div></div></div>""", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 All Results", "🟢 BUY", "🟡 HOLD", "🔴 SELL", "🚫 BLOCKED"])
        def style_signal(v):
            if v == "BUY": return "background-color:#003320;color:#00e676;font-weight:bold;"
            if v == "SELL": return "background-color:#2a0010;color:#ff4569;font-weight:bold;"
            if v == "HOLD": return "background-color:#2a1a00;color:#ffd740;font-weight:bold;"
            if v == "BLOCKED": return "background-color:#1a0033;color:#ce93d8;font-weight:bold;"
            return ""
        def style_check(v):
            if v == "✓": return "color:#00e676;font-weight:bold;text-align:center;"
            if v in ("✗", "⛔"): return "color:#ff4569;font-weight:bold;text-align:center;"
            return ""
        check_cols = [c for c in df_r.columns if c in [">SMA50", ">SMA200", "SMA50↑", "+DI>-DI", "DI≥15", ">SMA10W", ">SMA20W", "Earn ⛔"]]

        def _render_chart_for_selection(sel_obj, src_df, tab_key=""):
            """If a row is selected, render the daily+weekly chart drill-down."""
            if sel_obj is None or not sel_obj.selection or not sel_obj.selection.rows:
                return
            row_idx = sel_obj.selection.rows[0]
            src_reset = src_df.reset_index(drop=True)
            if row_idx >= len(src_reset):
                return
            selected_ticker = src_reset.iloc[row_idx]["Ticker"]

            st.markdown("---")
            st.markdown(f'<div class="section-label">📈 {selected_ticker} — Technical Analysis</div>', unsafe_allow_html=True)

            batch_data = st.session_state.get("scan_batch_data", pd.DataFrame())
            df_chart = extract_ticker_df(batch_data, selected_ticker, min_rows=20) if not batch_data.empty else None
            if df_chart is None:
                with st.spinner(f"Fetching {selected_ticker} data..."):
                    df_chart = fetch_ticker_single(selected_ticker, 220, min_rows=20)

            if df_chart is not None and len(df_chart) >= 20:
                df_weekly = df_chart.resample("W").agg({
                    "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
                }).dropna()
                col_d, col_w = st.columns(2)
                with col_d:
                    fig_daily = build_scanner_chart(selected_ticker, df_chart, title_suffix="Daily")
                    if fig_daily: st.plotly_chart(fig_daily, width="stretch", key=f"chart_daily_{tab_key}_{selected_ticker}")
                    else: st.warning("Insufficient daily data.")
                with col_w:
                    fig_weekly = build_scanner_chart(selected_ticker, df_weekly, title_suffix="Weekly")
                    if fig_weekly: st.plotly_chart(fig_weekly, width="stretch", key=f"chart_weekly_{tab_key}_{selected_ticker}")
                    else: st.warning("Insufficient weekly data.")
            else:
                st.warning(f"No chart data available for {selected_ticker}.")

        def render_table(data, key_suffix=""):
            if data.empty: st.info("No signals."); return None
            styled = (data.style.map(style_signal, subset=["Signal"]).map(style_check, subset=check_cols)
                .set_properties(**{"font-family": "IBM Plex Mono,monospace", "font-size": "13px"})
                .format({"Price": "${:.2f}", "Entry": "${:.2f}", "Target": "${:.2f}", "Stop": "${:.2f}", "D.RSI14": "{:.1f}", "D.ADX14": "{:.1f}", "W.RSI14": "{:.1f}", "W.ADX14": "{:.1f}"}, na_rep="—"))
            sel = st.dataframe(styled, width="stretch", height=min(600, 50 + len(data) * 36),
                               on_select="rerun", selection_mode="single-row", key=f"scanner_table_{key_suffix}")
            return sel

        with tab1:
            sel1 = render_table(df_r.reset_index(drop=True), "all")
            _render_chart_for_selection(sel1, df_r, "all")
        with tab2:
            sel2 = render_table(buys.reset_index(drop=True), "buy")
            _render_chart_for_selection(sel2, buys, "buy")
        with tab3:
            sel3 = render_table(holds.reset_index(drop=True), "hold")
            _render_chart_for_selection(sel3, holds, "hold")
        with tab4:
            sel4 = render_table(sells.reset_index(drop=True), "sell")
            _render_chart_for_selection(sel4, sells, "sell")
        with tab5:
            sel5 = render_table(blocked.reset_index(drop=True), "blocked")
            _render_chart_for_selection(sel5, blocked, "blocked")
        st.markdown("---"); _, col_dl = st.columns([3, 1])
        with col_dl: st.download_button("⬇ CSV", df_r.to_csv(index=False), "scan_results.csv", "text/csv", width="stretch")
        st.markdown("---"); st.markdown('<div class="section-label">Signal Logic</div>', unsafe_allow_html=True)
        l1, l2, l3, l4 = st.columns(4)
        with l1: st.markdown("**🟢 BUY** — All daily + weekly gates pass AND NOT in earnings blackout (±10d)")
        with l2: st.markdown("**🟡 HOLD** — Partial daily or weekly breakdown")
        with l3: st.markdown("**🔴 SELL** — Weekly below BOTH SMAs + daily confirmed")
        with l4: st.markdown("**🚫 BLOCKED** — All gates pass but within earnings blackout (±10d)")
    else:
        st.markdown("""<div style="text-align:center;padding:60px 20px;color:#2a4a6a;"><div style="font-size:3rem;">📡</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:1rem;color:#2a5a8a;">Press RUN SCAN</div>
        <div style="font-size:0.8rem;margin-top:12px;color:#1e3a5f;">Earnings ±10d · Slope ≥ 1.50%</div></div>""", unsafe_allow_html=True)
    st.markdown("---"); st.caption("⚠️ Data provided by Yahoo Finance for informational purposes only. Not financial advice.")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: MARKET PULSE (lazy-loaded)
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📊 Market Pulse":
    st.markdown("# 📊 Market Pulse"); st.markdown("*Real-time data via Yahoo Finance · Compare periods · Treemap by market cap*"); st.markdown("---")
    with st.spinner("📡 Loading 1.5 years of market data…"): _data = load_market_pulse_data()
    all_prices = _data["prices"]; sector_prices = _data["sector_prices"]; market_caps = _data["market_caps"]; fetched_at = _data["fetched_at"]
    elapsed = datetime.now() - fetched_at; st.caption(f"⏱ Data loaded {int(elapsed.total_seconds()//3600)}h {int((elapsed.total_seconds()%3600)//60)}m ago · {len(all_prices.columns)} tickers")
    if all_prices.empty: st.error("Could not load price data."); st.stop()

    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        view_mode = st.radio("View Mode", ["Sector Overview", "Single Period", "Compare Two Periods", "Period-over-Period Diff", "▶ Play Animation", "📈 Sector Trends"])
        st.markdown("---"); st.markdown("#### Period A")
        period_a = st.selectbox("Preset", ["1W", "2W", "1M", "3M", "6M", "YTD", "1Y", "1.5Y", "Custom"], index=0, key="period_a")
        if period_a == "Custom":
            start_a = st.date_input("Start", value=date.today()-timedelta(days=3), min_value=date.today()-timedelta(days=548), max_value=date.today(), key="start_a")
            end_a = st.date_input("End", value=date.today(), min_value=start_a, max_value=date.today(), key="end_a")
            date_start_a, date_end_a = start_a.strftime("%Y-%m-%d"), end_a.strftime("%Y-%m-%d")
        else: date_start_a, date_end_a = get_period_dates(period_a)
        returns_b = pd.Series(dtype=float); date_start_b = date_end_b = ""; period_b = "1M"
        if view_mode not in ["Single Period", "▶ Play Animation", "Sector Overview", "📈 Sector Trends"]:
            st.markdown("#### Period B")
            period_b = st.selectbox("Preset", ["1W", "2W", "1M", "3M", "6M", "YTD", "1Y", "1.5Y", "Custom"], index=2, key="period_b")
            if period_b == "Custom":
                start_b = st.date_input("Start", value=date.today()-timedelta(days=3), min_value=date.today()-timedelta(days=548), max_value=date.today(), key="start_b")
                end_b = st.date_input("End", value=date.today(), min_value=start_b, max_value=date.today(), key="end_b")
                date_start_b, date_end_b = start_b.strftime("%Y-%m-%d"), end_b.strftime("%Y-%m-%d")
            else: date_start_b, date_end_b = get_period_dates(period_b)
        st.markdown("---"); color_range = st.slider("Color Scale ± %", 5, 30, 5, 1)
        if view_mode == "📈 Sector Trends":
            st.markdown("---"); st.markdown("#### Trend Settings"); sma_window = st.slider("SMA Window", 10, 200, 50, 5); trend_color = st.color_picker("Line color", value="#00b4d8")
        else: sma_window = 50; trend_color = "#00b4d8"
        st.markdown("---"); st.markdown("#### Sector Filter")
        all_sectors = sorted(set(v[0] for v in SP500_STOCKS.values())); selected_sectors = st.multiselect("Show sectors", all_sectors, default=all_sectors)

    sector_tickers = [t for t, (sec, _) in SP500_STOCKS.items() if sec in selected_sectors]
    prices = all_prices[[c for c in sector_tickers if c in all_prices.columns]]
    returns_a = compute_returns(prices, date_start_a, date_end_a)
    if view_mode not in ("Single Period", "▶ Play Animation", "Sector Overview", "📈 Sector Trends"): returns_b = compute_returns(prices, date_start_b, date_end_b)

    if view_mode == "Sector Overview":
        label_a = period_a if period_a != "Custom" else f"{date_start_a} → {date_end_a}"; show_metrics(returns_a, label_a); st.markdown("---")
        st.plotly_chart(build_sector_heatmap(returns_a, market_caps, title=f"S&P 500 Sector Overview — {label_a}", color_range=color_range), width="stretch")
        st.markdown("#### Sector Breakdown"); rows = []
        for sector in sorted(set(v[0] for v in SP500_STOCKS.values())):
            tks = [t for t, (s, _) in SP500_STOCKS.items() if s == sector and t in returns_a.index]
            if not tks: continue
            rets = returns_a[tks]; caps = [market_caps.get(t, 1e9) for t in tks]; tc = sum(caps); wr = sum(r*c for r, c in zip(rets, caps))/tc if tc else 0
            rows.append({"Sector": sector, "Stocks": len(tks), "Gainers": int((rets>0).sum()), "Losers": int((rets<0).sum()), "Wtd Avg Return": f"{wr:+.2f}%", "Best": f"{rets.idxmax()} ({rets.max():+.1f}%)", "Worst": f"{rets.idxmin()} ({rets.min():+.1f}%)"})
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        st.markdown("---"); st.markdown("#### 🔍 Drill Into a Sector")
        drill = st.selectbox("Select sector", ["— select —"] + sorted(set(v[0] for v in SP500_STOCKS.values())))
        if drill != "— select —":
            dt = {t: v for t, v in SP500_STOCKS.items() if v[0] == drill and t in returns_a.index}
            st.plotly_chart(build_heatmap(returns_a[[t for t in dt]], market_caps, title=f"{drill} — {label_a}", color_range=color_range), width="stretch")
    elif view_mode == "Single Period":
        label_a = period_a if period_a != "Custom" else f"{date_start_a} → {date_end_a}"; show_metrics(returns_a, label_a); st.markdown("---")
        st.plotly_chart(build_heatmap(returns_a, market_caps, title=f"S&P 500 — {label_a}", color_range=color_range), width="stretch")
    elif view_mode == "Compare Two Periods":
        label_a = period_a if period_a != "Custom" else f"{date_start_a}→{date_end_a}"; label_b = period_b if period_b != "Custom" else f"{date_start_b}→{date_end_b}"
        cl = st.radio("View Level", ["Sector", "Stock"], horizontal=True); fn = build_sector_heatmap if cl == "Sector" else build_heatmap
        ca, cb = st.columns(2)
        with ca: st.markdown(f"#### A — {label_a}"); show_metrics(returns_a, label_a); st.plotly_chart(fn(returns_a, market_caps, title=f"A — {label_a}", color_range=color_range), width="stretch")
        with cb: st.markdown(f"#### B — {label_b}"); show_metrics(returns_b, label_b); st.plotly_chart(fn(returns_b, market_caps, title=f"B — {label_b}", color_range=color_range), width="stretch")
    elif view_mode == "Period-over-Period Diff":
        label_a = period_a if period_a != "Custom" else f"{date_start_a}→{date_end_a}"; label_b = period_b if period_b != "Custom" else f"{date_start_b}→{date_end_b}"
        dl = st.radio("View Level", ["Sector", "Stock"], horizontal=True)
        st.markdown(f"#### Δ {label_b} minus {label_a}"); show_metrics(returns_a, f"A: {label_a}"); show_metrics(returns_b, f"B: {label_b}"); st.markdown("---")
        if dl == "Sector":
            st.plotly_chart(build_sector_diff_heatmap(returns_a, returns_b, market_caps, title=f"Sector Δ: {label_b} vs {label_a}", color_range=color_range), width="stretch")
            common = returns_a.index.intersection(returns_b.index); sdrows = []
            for sector in sorted(set(v[0] for v in SP500_STOCKS.values())):
                tks = [t for t, (s, _) in SP500_STOCKS.items() if s == sector and t in common]
                if not tks: continue
                caps = np.array([market_caps.get(t, 1e9) for t in tks]); ra = np.array([float(returns_a[t]) for t in tks]); rb = np.array([float(returns_b[t]) for t in tks]); tc = caps.sum()
                wa = float((ra*caps).sum()/tc) if tc else 0; wb = float((rb*caps).sum()/tc) if tc else 0; diffs = rb - ra
                sdrows.append({"Sector": sector, f"A ({label_a})": f"{wa:+.2f}%", f"B ({label_b})": f"{wb:+.2f}%", "Δ": f"{wb-wa:+.2f}%", "Best Δ": f"{tks[int(np.argmax(diffs))]} ({diffs.max():+.1f}%)", "Worst Δ": f"{tks[int(np.argmin(diffs))]} ({diffs.min():+.1f}%)"})
            st.dataframe(pd.DataFrame(sdrows), width="stretch", hide_index=True)
        else: st.plotly_chart(build_diff_heatmap(returns_a, returns_b, market_caps, title=f"Stock Δ: {label_b} vs {label_a}"), width="stretch")
    elif view_mode == "▶ Play Animation":
        label_a = period_a if period_a != "Custom" else f"{date_start_a} → {date_end_a}"; freq = PERIOD_TO_FRAME_INTERVAL.get(period_a if period_a != "Custom" else "Custom", "W")
        st.markdown(f"#### ▶ Animating **{label_a}** — {freq_label(freq)} frames"); show_metrics(returns_a, label_a); st.markdown("---")
        with st.spinner("⚙️ Pre-computing..."): st.plotly_chart(build_animated_heatmap(prices=prices, market_caps=market_caps, period=period_a if period_a != "Custom" else "Custom", start_date=date_start_a, end_date=date_end_a, color_range=color_range, selected_sectors=selected_sectors), width="stretch")
    elif view_mode == "📈 Sector Trends":
        label_a = period_a if period_a != "Custom" else f"{date_start_a} → {date_end_a}"; st.markdown(f"#### 📈 Sector Trends — {label_a}"); st.markdown("---")
        sectors_to_show = [s for s in selected_sectors if s in sector_prices.columns]
        for i in range(0, len(sectors_to_show), 4):
            cols = st.columns(4)
            for j, sector in enumerate(sectors_to_show[i:i+4]):
                fig = build_sector_trend_fig(sector, sector_prices, date_start_a, sma_window, trend_color)
                if fig: cols[j].plotly_chart(fig, width="stretch")
                else: cols[j].warning(f"No data for {sector}")

    with st.expander("📋 Raw Returns Table", expanded=False):
        if not returns_a.empty:
            rows = [{"Ticker": t, "Sector": SP500_STOCKS.get(t, ("?","?"))[0], "Sub-Industry": SP500_STOCKS.get(t, ("?","?"))[1], f"Return ({period_a})": f"{returns_a.get(t,0):+.2f}%"} for t in returns_a.index]
            df_t = pd.DataFrame(rows).sort_values("Sector")
            if view_mode == "Single Period":
                sel = st.dataframe(df_t, width="stretch", height=300, hide_index=True, on_select="rerun", selection_mode="single-row")
                if sel and sel.selection and sel.selection.rows:
                    tk = df_t.iloc[sel.selection.rows[0]]["Ticker"]; fig = build_stock_chart(tk, all_prices, date_start_a, date_end_a)
                    if fig: st.plotly_chart(fig, width="stretch")
            else: st.dataframe(df_t, width="stretch", height=300, hide_index=True)
    st.markdown("---"); st.caption("⚠️ Data provided by Yahoo Finance for informational purposes only. Not financial advice.")