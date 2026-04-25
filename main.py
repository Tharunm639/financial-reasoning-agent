import os, json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.graph import run_agent

# ── Config ────────────────────────────────────────────────────────────────────
HISTORY_FILE = Path(__file__).parent / "data" / "history.json"
HISTORY_FILE.parent.mkdir(exist_ok=True)

st.set_page_config(page_title="FinSight AI", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# ── History helpers ───────────────────────────────────────────────────────────
def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            return []
    return []

def save_history(entry: dict):
    history = load_history()
    history.insert(0, entry)
    history = history[:30]          # keep last 30
    HISTORY_FILE.write_text(json.dumps(history, indent=2))

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*{font-family:'Inter',sans-serif!important;box-sizing:border-box;}
.stApp{background:#060e1c;color:#dde6f0;}
header,footer,#MainMenu{visibility:hidden;}
[data-testid="stDecoration"]{display:none;}
hr{border-color:#162033!important;margin:1.8rem 0!important;}

/* Sidebar */
[data-testid="stSidebar"]{background:#070f1e;border-right:1px solid #162033;}
[data-testid="stSidebar"] .stMarkdown p{color:#8aa0b8;font-size:.82rem;}

/* Navbar */
.navbar{display:flex;align-items:center;justify-content:space-between;
  padding:.8rem 0 1.4rem;border-bottom:1px solid #162033;margin-bottom:2rem;}
.nav-logo{font-size:1.25rem;font-weight:900;color:#fff;letter-spacing:-.3px;}
.nav-logo em{background:linear-gradient(90deg,#00d2ff,#7b2ff7);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-style:normal;}
.nav-right{font-size:.78rem;color:#3a5a7a;font-weight:500;}

/* Search box */
.search-box{background:linear-gradient(135deg,#0c1829,#09131f);border:1px solid #1e3350;
  border-radius:16px;padding:2rem 2.4rem;text-align:center;max-width:700px;margin:0 auto 2.4rem;}
.search-title{font-size:1.85rem;font-weight:800;color:#fff;margin-bottom:.3rem;}
.search-sub{font-size:.87rem;color:#5a7a9e;margin-bottom:1.4rem;}

/* Inputs */
[data-testid="stTextInput"] input{background:#0c1829!important;border:1.5px solid #1e3350!important;
  border-radius:10px!important;color:#dde6f0!important;font-size:1rem!important;padding:.7rem 1rem!important;}
[data-testid="stTextInput"] input:focus{border-color:#00d2ff!important;
  box-shadow:0 0 0 3px rgba(0,210,255,.1)!important;}
[data-testid="stTextInput"] input::placeholder{color:#2e4a62!important;}

/* Button */
.stButton>button{background:linear-gradient(135deg,#00d2ff,#7b2ff7)!important;
  border:none!important;border-radius:10px!important;color:#fff!important;
  font-weight:700!important;font-size:.95rem!important;padding:.65rem 0!important;
  width:100%!important;transition:opacity .2s!important;}
.stButton>button:hover{opacity:.82!important;}

/* Company header */
.co-header{background:linear-gradient(135deg,#0c1829,#09131f);border:1px solid #1e3350;
  border-radius:16px;padding:1.8rem 2.2rem;margin-bottom:1.4rem;
  position:relative;overflow:hidden;}
.co-header::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,#00d2ff,#7b2ff7);background-size:200%;
  animation:shine 3s linear infinite;}
@keyframes shine{to{background-position:200% center;}}
.co-name{font-size:1.7rem;font-weight:800;color:#fff;}
.co-meta{font-size:.8rem;color:#5a7a9e;margin-top:.2rem;}
.co-tick{display:inline-block;background:rgba(0,210,255,.07);border:1px solid rgba(0,210,255,.2);
  border-radius:6px;padding:.2rem .7rem;font-size:.78rem;font-weight:700;color:#00d2ff;margin-top:.55rem;}
.co-price{font-size:2.8rem;font-weight:900;color:#fff;line-height:1;}
.up{color:#00e676;font-size:1rem;font-weight:700;}
.dn{color:#ff5252;font-size:1rem;font-weight:700;}
.co-prev{font-size:.75rem;color:#5a7a9e;margin-top:.2rem;}

/* Metric card */
.mcard{background:#0c1829;border:1px solid #1e3350;border-radius:12px;
  padding:1rem 1.15rem;transition:border-color .2s,transform .15s;}
.mcard:hover{border-color:rgba(0,210,255,.3);transform:translateY(-2px);}
.ml{font-size:.64rem;font-weight:600;color:#2e4a62;text-transform:uppercase;
  letter-spacing:.09em;margin-bottom:.35rem;}
.mv{font-size:1.28rem;font-weight:700;color:#dde6f0;}
.ms{font-size:.7rem;color:#2e4a62;margin-top:.15rem;}

/* Section label */
.slabel{font-size:.68rem;font-weight:700;color:#2e4a62;text-transform:uppercase;
  letter-spacing:.1em;padding-bottom:.4rem;border-bottom:1px solid #162033;margin-bottom:.9rem;}

/* AI card */
.acard{background:#0c1829;border:1px solid #1e3350;border-left:3px solid #00d2ff;
  border-radius:12px;padding:1.4rem 1.6rem;line-height:1.8;color:#b8cfe6;font-size:.9rem;}

/* Sentiment */
.s-bull{background:#0b2e1e;border:1px solid #00c853;color:#00e676;padding:.38rem 1rem;
  border-radius:50px;font-weight:700;font-size:.82rem;display:inline-block;letter-spacing:.03em;}
.s-bear{background:#2e0b0b;border:1px solid #d50000;color:#ff5252;padding:.38rem 1rem;
  border-radius:50px;font-weight:700;font-size:.82rem;display:inline-block;letter-spacing:.03em;}
.s-neut{background:#1e1a0b;border:1px solid #ffd600;color:#ffd740;padding:.38rem 1rem;
  border-radius:50px;font-weight:700;font-size:.82rem;display:inline-block;letter-spacing:.03em;}

/* News card */
.ncard{background:#0c1829;border:1px solid #1e3350;border-radius:12px;
  padding:.9rem 1.1rem;margin-bottom:.6rem;transition:border-color .2s,transform .15s;}
.ncard:hover{border-color:rgba(0,210,255,.25);transform:translateY(-2px);}
.nsrc{font-size:.62rem;font-weight:700;color:#00d2ff;text-transform:uppercase;
  letter-spacing:.07em;margin-bottom:.25rem;}
.ntit{font-size:.87rem;font-weight:600;color:#dde6f0;line-height:1.4;margin-bottom:.28rem;}
.nsnip{font-size:.77rem;color:#3a5a7a;line-height:1.5;}

/* History item */
.hitem{background:#0a1522;border:1px solid #162033;border-radius:10px;
  padding:.7rem .9rem;margin-bottom:.5rem;cursor:pointer;transition:border-color .2s;}
.hitem:hover{border-color:rgba(0,210,255,.25);}
.htick{font-size:.85rem;font-weight:700;color:#dde6f0;}
.hco{font-size:.72rem;color:#5a7a9e;margin-top:.1rem;}
.htime{font-size:.65rem;color:#2e4a62;margin-top:.2rem;}
.hpill{font-size:.65rem;font-weight:600;float:right;padding:.15rem .5rem;
  border-radius:20px;margin-top:.1rem;}
.hp-bull{background:#0b2e1e;color:#00e676;border:1px solid #00c85355;}
.hp-bear{background:#2e0b0b;color:#ff5252;border:1px solid #d5000055;}
.hp-neut{background:#1e1a0b;color:#ffd740;border:1px solid #ffd60055;}

/* Tabs */
[data-testid="stTabs"] button{color:#3a5a7a!important;font-weight:500!important;font-size:.84rem!important;}
[data-testid="stTabs"] button[aria-selected="true"]{color:#00d2ff!important;border-bottom-color:#00d2ff!important;}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden;}
</style>
""", unsafe_allow_html=True)

# ── Chart helpers ─────────────────────────────────────────────────────────────
BG = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#dde6f0", size=11),
    margin=dict(l=8, r=8, t=24, b=8),
    xaxis=dict(gridcolor="#162033", zeroline=False, color="#3a5a7a"),
    yaxis=dict(gridcolor="#162033", zeroline=False, color="#3a5a7a"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#3a5a7a", size=10)),
)

def fig_candle(ohlcv):
    df = pd.DataFrame(ohlcv)
    if df.empty: return None
    vc = ["rgba(0,230,118,0.45)" if c>=o else "rgba(255,82,82,0.45)" for c,o in zip(df["close"],df["open"])]
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing=dict(line=dict(color="#00e676",width=1), fillcolor="rgba(0,230,118,0.2)"),
        decreasing=dict(line=dict(color="#ff5252",width=1), fillcolor="rgba(255,82,82,0.2)"),
        name="Price"))
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"], marker_color=vc, yaxis="y2", showlegend=False))
    fig.update_layout(**BG, height=400, xaxis_rangeslider_visible=False,
                      yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#3a5a7a", tickformat=".2s"))
    return fig

def fig_area(c1y, ticker):
    df = pd.DataFrame(c1y)
    if df.empty: return None
    up = df["close"].iloc[-1] >= df["close"].iloc[0]
    rgb = "0,230,118" if up else "255,82,82"
    fig = go.Figure(go.Scatter(
        x=df["date"], y=df["close"], mode="lines", name=ticker,
        line=dict(color=f"rgb({rgb})", width=2),
        fill="tozeroy", fillcolor=f"rgba({rgb},0.07)"))
    fig.update_layout(**BG, height=340)
    return fig

def fig_volume(ohlcv):
    df = pd.DataFrame(ohlcv)
    if df.empty: return None
    colors = ["rgba(0,230,118,0.65)" if c>=o else "rgba(255,82,82,0.65)" for c,o in zip(df["close"],df["open"])]
    fig = go.Figure(go.Bar(x=df["date"], y=df["volume"], marker_color=colors))
    fig.update_layout(**BG, height=280, showlegend=False)
    return fig

def fig_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number=dict(font=dict(color="#dde6f0", size=30, family="Inter")),
        title=dict(text="Market Sentiment Score", font=dict(color="#3a5a7a", size=11)),
        gauge=dict(
            axis=dict(range=[-10,10], tickcolor="#3a5a7a", tickfont=dict(color="#3a5a7a", size=9)),
            bar=dict(color="#00d2ff", thickness=0.2),
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
            steps=[
                dict(range=[-10,-3], color="rgba(255,82,82,0.12)"),
                dict(range=[-3, 3],  color="rgba(255,215,64,0.09)"),
                dict(range=[ 3,10],  color="rgba(0,230,118,0.12)"),
            ])))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter"), height=210, margin=dict(l=16,r=16,t=28,b=0))
    return fig

# ── Utilities ─────────────────────────────────────────────────────────────────
def fmt_cap(n):
    if n is None: return "—"
    if n>=1e12: return f"${n/1e12:.2f}T"
    if n>=1e9:  return f"${n/1e9:.2f}B"
    if n>=1e6:  return f"${n/1e6:.2f}M"
    return f"${n:,.0f}"

def fmt_pct(n): return "—" if n is None else f"{n*100:.2f}%"
def flt(n, pre="", suf="", dp=2): return "—" if n is None else f"{pre}{n:.{dp}f}{suf}"

def sent_label(text):
    t = (text or "").upper()
    if "BULLISH" in t: return "Positive", "bull"
    if "BEARISH"  in t: return "Negative", "bear"
    return "Neutral", "neut"

def pill_html(text):
    label, kind = sent_label(text)
    icons = {"bull":"▲", "bear":"▼", "neut":"●"}
    return f'<span class="s-{kind}">{icons[kind]} {label}</span>'

def mcard(col, label, val, sub=""):
    col.markdown(
        f'<div class="mcard"><div class="ml">{label}</div><div class="mv">{val}</div>'
        +(f'<div class="ms">{sub}</div>' if sub else "")+'</div>',
        unsafe_allow_html=True)

def hpill(text):
    _, kind = sent_label(text)
    labels = {"bull":"Positive","bear":"Negative","neut":"Neutral"}
    return f'<span class="hpill hp-{kind}">{labels[kind]}</span>'

# ── SIDEBAR — Search History ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Search History")
    st.markdown("---")
    history = load_history()
    if not history:
        st.markdown('<p style="color:#2e4a62;font-size:.82rem">No searches yet.<br>Analyse a ticker to get started.</p>',
                    unsafe_allow_html=True)
    else:
        for item in history:
            label, kind = sent_label(item.get("sentiment",""))
            icons = {"bull":"▲","bear":"▼","neut":"●"}
            st.markdown(f"""
<div class="hitem">
  {hpill(item.get("sentiment",""))}
  <div class="htick">{item.get("ticker","")}</div>
  <div class="hco">{item.get("company","")}</div>
  <div class="htime">{item.get("time","")}</div>
</div>""", unsafe_allow_html=True)

    if history:
        st.markdown("---")
        if st.button("Clear History", use_container_width=True):
            HISTORY_FILE.write_text("[]")
            st.rerun()

# ── NAVBAR ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="nav-logo">📈 <em>FinSight</em> AI</div>
  <div class="nav-right">Financial Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

# ── API KEY CHECK ─────────────────────────────────────────────────────────────
api_key = os.environ.get("GOOGLE_API_KEY", "")
if not api_key or api_key.startswith("your_"):
    st.error("**Configuration Required** — Add `GOOGLE_API_KEY=...` to your `.env` file and save.")
    st.stop()

# ── SEARCH ────────────────────────────────────────────────────────────────────
_, mid, _ = st.columns([1, 2.4, 1])
with mid:
    st.markdown("""
<div class="search-box">
  <div class="search-title">Market Analysis</div>
  <div class="search-sub">Enter a stock ticker to generate an AI-powered investment report</div>
</div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1.1])
    with c1:
        ticker = st.text_input("", placeholder="Ticker symbol — AAPL · MSFT · TSLA · GOOGL",
                               label_visibility="collapsed").upper().strip()
    with c2:
        go_btn = st.button("Analyse", use_container_width=True)

# ── MAIN ANALYSIS ─────────────────────────────────────────────────────────────
if go_btn and ticker:
    with st.spinner(f"Retrieving data and generating analysis for **{ticker}**…"):
        result = run_agent(ticker)

    fund  = result.get("fundamentals", {})
    ohlcv = result.get("ohlcv_3m", [])
    c1y   = result.get("close_1y", [])
    news  = result.get("news", [])
    sent  = result.get("sentiment", "")
    smry  = result.get("summary", "")
    score = result.get("sentiment_score", 0)
    err   = result.get("error", "")

    if err and not fund:
        st.error(f"Unable to retrieve data: {err}")
        st.stop()

    # Save to history
    sent_lbl, _ = sent_label(sent)
    save_history({
        "ticker":  ticker,
        "company": fund.get("company_name", ticker),
        "sentiment": sent,
        "price":   fund.get("current_price"),
        "time":    datetime.now().strftime("%d %b %Y, %H:%M"),
    })
    st.rerun() if False else None   # keep running

    # ── Company Header ──────────────────────────────────────────────────────
    curr = fund.get("current_price")
    prev = fund.get("previous_close")
    chg  = (curr - prev) if curr and prev else None
    chgp = (chg / prev * 100) if chg and prev else None
    sign = "+" if chg and chg >= 0 else ""
    chg_cls = ("up" if chg and chg >= 0 else "dn") if chg else ""
    price_blk = (
        f'<div style="text-align:right">'
        f'<div class="co-price">${curr:,.2f}</div>'
        f'<div class="{chg_cls}">{sign}{chg:.2f} &nbsp; {sign}{chgp:.2f}%</div>'
        f'<div class="co-prev">Previous close &nbsp; ${prev:,.2f}</div></div>'
    ) if curr and prev else ""

    st.markdown(f"""
<div class="co-header">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem">
    <div>
      <div class="co-name">{fund.get("company_name", ticker)}</div>
      <div class="co-meta">{fund.get("exchange","")} &ensp;·&ensp; {fund.get("sector","")} &ensp;·&ensp; {fund.get("industry","")}</div>
      <div class="co-tick">{ticker} &nbsp;·&nbsp; {fund.get("currency","USD")}</div>
    </div>
    {price_blk}
  </div>
</div>""", unsafe_allow_html=True)

    # ── Metrics ─────────────────────────────────────────────────────────────
    st.markdown('<div class="slabel">Fundamentals</div>', unsafe_allow_html=True)
    r1 = st.columns(5)
    mcard(r1[0], "Market Capitalisation", fmt_cap(fund.get("market_cap")))
    mcard(r1[1], "P/E Ratio (Trailing)",  flt(fund.get("pe_ratio")), f"Forward {flt(fund.get('forward_pe'))}")
    mcard(r1[2], "Earnings Per Share",    flt(fund.get("eps"), "$"))
    mcard(r1[3], "52-Week High",          flt(fund.get("52w_high"), "$"))
    mcard(r1[4], "52-Week Low",           flt(fund.get("52w_low"),  "$"))
    r2 = st.columns(5)
    mcard(r2[0], "Beta",                  flt(fund.get("beta")), "Relative to S&P 500")
    mcard(r2[1], "Dividend Yield",        fmt_pct(fund.get("dividend_yield")))
    mcard(r2[2], "Annual Revenue",        fmt_cap(fund.get("revenue")))
    mcard(r2[3], "Profit Margin",         fmt_pct(fund.get("profit_margin")))
    mcard(r2[4], "Average Volume",        f"{fund.get('avg_volume'):,}" if fund.get("avg_volume") else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ──────────────────────────────────────────────────────────────
    st.markdown('<div class="slabel">Price Charts</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Candlestick  ·  3 Months", "Price Trend  ·  1 Year", "Trading Volume  ·  3 Months"])
    with t1:
        f = fig_candle(ohlcv)
        if f: st.plotly_chart(f, use_container_width=True, config={"displayModeBar": False})
    with t2:
        f = fig_area(c1y, ticker)
        if f: st.plotly_chart(f, use_container_width=True, config={"displayModeBar": False})
    with t3:
        f = fig_volume(ohlcv)
        if f: st.plotly_chart(f, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Sentiment + Summary ─────────────────────────────────────────────────
    lc, rc = st.columns([2, 3])
    with lc:
        st.markdown('<div class="slabel">Sentiment Analysis</div>', unsafe_allow_html=True)
        st.markdown(pill_html(sent), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(fig_gauge(score), use_container_width=True, config={"displayModeBar": False})
        for line in (sent or "").split("\n"):
            if "EXPLANATION:" in line.upper():
                expl = line.split(":", 1)[-1].strip()
                st.markdown(f'<div class="acard" style="font-size:.82rem;margin-top:.5rem">{expl}</div>',
                            unsafe_allow_html=True)
                break
    with rc:
        st.markdown('<div class="slabel">Investment Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="acard">{smry}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── News + Table ────────────────────────────────────────────────────────
    nc, tc = st.columns([3, 2])
    with nc:
        st.markdown('<div class="slabel">Latest News</div>', unsafe_allow_html=True)
        for item in news:
            url   = item.get("url", "#")
            src   = item.get("source", "")
            title = item.get("title", "")
            snip  = item.get("snippet", "")
            snip  = (snip[:220]+"…") if len(snip)>220 else snip
            st.markdown(f"""
<div class="ncard">
  <div class="nsrc">{src}</div>
  <div class="ntit"><a href="{url}" target="_blank" style="color:#dde6f0;text-decoration:none">{title}</a></div>
  <div class="nsnip">{snip}</div>
</div>""", unsafe_allow_html=True)
    with tc:
        st.markdown('<div class="slabel">Price History</div>', unsafe_allow_html=True)
        if ohlcv:
            df_t = (pd.DataFrame(ohlcv[-25:])
                    .rename(columns={"date":"Date","open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"})
                    .iloc[::-1].reset_index(drop=True))
            st.dataframe(
                df_t.style.format({"Open":"${:.2f}","High":"${:.2f}","Low":"${:.2f}","Close":"${:.2f}","Volume":"{:,}"}),
                use_container_width=True, height=400, hide_index=True)

    # ── About ───────────────────────────────────────────────────────────────
    if fund.get("description"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="slabel">Company Overview</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="acard" style="font-size:.85rem">{fund["description"]}</div>',
                    unsafe_allow_html=True)
        if fund.get("website"):
            st.markdown(f'[{fund["website"]}]({fund["website"]})')

elif go_btn:
    st.warning("Please enter a ticker symbol.")
