import os
from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.graph import run_agent

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinSight AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
* { font-family:'Inter',sans-serif !important; box-sizing:border-box; }

/* ── Base ── */
.stApp            { background:#060e1c; color:#dde6f0; }
header, footer, #MainMenu { visibility:hidden; }
[data-testid="stDecoration"] { display:none; }
[data-testid="stSidebar"]    { display:none; }
hr { border-color:#162033 !important; margin:2rem 0 !important; }

/* ── Nav bar ── */
.navbar {
  display:flex; align-items:center; justify-content:space-between;
  padding:1rem 0 1.4rem; border-bottom:1px solid #162033; margin-bottom:2.2rem;
}
.nav-logo { font-size:1.3rem; font-weight:900; color:#fff; letter-spacing:-0.5px; }
.nav-logo span { background:linear-gradient(90deg,#00d2ff,#7b2ff7);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.nav-tag { font-size:0.75rem; background:rgba(0,210,255,0.1);
  border:1px solid rgba(0,210,255,0.25); border-radius:20px;
  padding:0.25rem 0.8rem; color:#00d2ff; font-weight:600; }

/* ── Search bar ── */
.search-wrap {
  max-width:720px; margin:0 auto 2.4rem;
  background:linear-gradient(135deg,#0c1829,#09131f);
  border:1px solid #1e3350;
  border-radius:16px; padding:2rem 2.4rem;
  text-align:center;
}
.search-title { font-size:1.9rem; font-weight:800; color:#fff; margin-bottom:0.3rem; }
.search-sub   { font-size:0.88rem; color:#5a7a9e; margin-bottom:1.4rem; }

/* ── Inputs ── */
[data-testid="stTextInput"] input {
  background:#0c1829 !important; border:1.5px solid #1e3350 !important;
  border-radius:10px !important; color:#dde6f0 !important;
  font-size:1rem !important; padding:0.7rem 1rem !important;
}
[data-testid="stTextInput"] input:focus {
  border-color:#00d2ff !important; box-shadow:0 0 0 3px rgba(0,210,255,0.12) !important;
}
[data-testid="stTextInput"] input::placeholder { color:#3a5570 !important; }

/* ── Button ── */
.stButton>button {
  background:linear-gradient(135deg,#00d2ff,#7b2ff7) !important;
  border:none !important; border-radius:10px !important;
  color:#fff !important; font-weight:700 !important;
  font-size:0.95rem !important; padding:0.65rem 0 !important;
  width:100% !important; transition:opacity .2s !important;
}
.stButton>button:hover { opacity:.82 !important; }

/* ── Company header ── */
.co-header {
  background:linear-gradient(135deg,#0c1829 0%,#09131f 100%);
  border:1px solid #1e3350; border-radius:16px;
  padding:1.8rem 2.2rem; margin-bottom:1.6rem;
  position:relative; overflow:hidden;
}
.co-header::after {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg,#00d2ff,#7b2ff7,#00d2ff);
  background-size:200%; animation:shine 3s linear infinite;
}
@keyframes shine { to { background-position:200% center; } }
.co-name  { font-size:1.75rem; font-weight:800; color:#fff; }
.co-meta  { font-size:0.8rem; color:#5a7a9e; margin-top:0.25rem; }
.co-tick  { display:inline-block; background:rgba(0,210,255,0.08);
  border:1px solid rgba(0,210,255,0.22); border-radius:6px;
  padding:0.2rem 0.7rem; font-size:0.78rem; font-weight:700;
  color:#00d2ff; margin-top:0.6rem; }
.co-price { font-size:2.8rem; font-weight:900; color:#fff; line-height:1; }
.chg-up   { color:#00e676; font-size:1rem; font-weight:700; }
.chg-dn   { color:#ff5252; font-size:1rem; font-weight:700; }
.co-prev  { font-size:0.75rem; color:#5a7a9e; margin-top:0.25rem; }

/* ── Metric card ── */
.mcard {
  background:#0c1829; border:1px solid #1e3350; border-radius:12px;
  padding:1rem 1.2rem; margin-bottom:0.6rem;
  transition:border-color .2s, transform .15s;
}
.mcard:hover { border-color:#00d2ff44; transform:translateY(-2px); }
.ml { font-size:0.65rem; font-weight:600; color:#3a6080;
  text-transform:uppercase; letter-spacing:.09em; margin-bottom:.35rem; }
.mv { font-size:1.3rem; font-weight:700; color:#dde6f0; }
.ms { font-size:0.72rem; color:#3a6080; margin-top:.18rem; }

/* ── Section label ── */
.slabel {
  font-size:0.72rem; font-weight:700; color:#3a6080;
  text-transform:uppercase; letter-spacing:.1em;
  padding-bottom:.45rem; border-bottom:1px solid #162033; margin-bottom:1rem;
}

/* ── AI cards ── */
.ai-card {
  background:#0c1829; border:1px solid #1e3350;
  border-left:3px solid #00d2ff; border-radius:12px;
  padding:1.4rem 1.6rem; line-height:1.8; color:#b8cfe6; font-size:.9rem;
}

/* ── Sentiment pill ── */
.s-bull{background:#0b2e1e;border:1px solid #00c853;color:#00e676;padding:.4rem 1.1rem;border-radius:50px;font-weight:700;font-size:.85rem;display:inline-block;}
.s-bear{background:#2e0b0b;border:1px solid #d50000;color:#ff5252;padding:.4rem 1.1rem;border-radius:50px;font-weight:700;font-size:.85rem;display:inline-block;}
.s-neut{background:#1e1e0b;border:1px solid #ffd600;color:#ffd740;padding:.4rem 1.1rem;border-radius:50px;font-weight:700;font-size:.85rem;display:inline-block;}

/* ── News card ── */
.ncard {
  background:#0c1829; border:1px solid #1e3350; border-radius:12px;
  padding:.95rem 1.1rem; margin-bottom:.65rem;
  transition:border-color .2s, transform .15s;
}
.ncard:hover { border-color:#00d2ff44; transform:translateY(-2px); }
.nsrc  { font-size:.65rem; font-weight:700; color:#00d2ff;
  text-transform:uppercase; letter-spacing:.07em; margin-bottom:.28rem; }
.ntit  { font-size:.88rem; font-weight:600; color:#dde6f0; line-height:1.4; margin-bottom:.3rem; }
.nsnip { font-size:.78rem; color:#3a6080; line-height:1.5; }

/* ── Tabs ── */
[data-testid="stTabs"] button { color:#3a6080 !important; font-weight:500 !important; font-size:.85rem !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#00d2ff !important; border-bottom-color:#00d2ff !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# ─── CHART HELPERS ────────────────────────────────────────────────────────────
BG = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#dde6f0", size=11),
    margin=dict(l=8, r=8, t=28, b=8),
    xaxis=dict(gridcolor="#162033", zeroline=False, color="#3a6080"),
    yaxis=dict(gridcolor="#162033", zeroline=False, color="#3a6080"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#3a6080", size=10)),
)

def fig_candle(ohlcv):
    df = pd.DataFrame(ohlcv)
    if df.empty: return None
    vol_colors = [
        "rgba(0,230,118,0.45)" if c >= o else "rgba(255,82,82,0.45)"
        for c, o in zip(df["close"], df["open"])
    ]
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing=dict(line=dict(color="#00e676", width=1), fillcolor="rgba(0,230,118,0.22)"),
        decreasing=dict(line=dict(color="#ff5252", width=1), fillcolor="rgba(255,82,82,0.22)"),
        name="Price",
    ))
    fig.add_trace(go.Bar(
        x=df["date"], y=df["volume"], marker_color=vol_colors,
        yaxis="y2", showlegend=False, name="Volume"
    ))
    fig.update_layout(
        **BG, height=420, xaxis_rangeslider_visible=False,
        yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#3a6080", tickformat=".2s"),
    )
    return fig

def fig_area(close_1y, ticker):
    df = pd.DataFrame(close_1y)
    if df.empty: return None
    up = df["close"].iloc[-1] >= df["close"].iloc[0]
    c  = ("0,230,118" if up else "255,82,82")
    fig = go.Figure(go.Scatter(
        x=df["date"], y=df["close"], mode="lines", name=ticker,
        line=dict(color=f"rgb({c})", width=2),
        fill="tozeroy", fillcolor=f"rgba({c},0.07)",
    ))
    fig.update_layout(**BG, height=350)
    return fig

def fig_volume(ohlcv):
    df = pd.DataFrame(ohlcv)
    if df.empty: return None
    colors = [
        "rgba(0,230,118,0.65)" if c >= o else "rgba(255,82,82,0.65)"
        for c, o in zip(df["close"], df["open"])
    ]
    fig = go.Figure(go.Bar(x=df["date"], y=df["volume"], marker_color=colors))
    fig.update_layout(**BG, height=280, showlegend=False)
    return fig

def fig_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number=dict(font=dict(color="#dde6f0", size=30, family="Inter")),
        title=dict(text="Sentiment Score", font=dict(color="#3a6080", size=12)),
        gauge=dict(
            axis=dict(range=[-10,10], tickcolor="#3a6080", tickfont=dict(color="#3a6080", size=10)),
            bar=dict(color="#00d2ff", thickness=0.22),
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
            steps=[
                dict(range=[-10,-3], color="rgba(255,82,82,0.13)"),
                dict(range=[-3, 3],  color="rgba(255,215,64,0.10)"),
                dict(range=[ 3,10],  color="rgba(0,230,118,0.13)"),
            ],
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"), height=210, margin=dict(l=16,r=16,t=28,b=0),
    )
    return fig

# ─── UTIL ─────────────────────────────────────────────────────────────────────
def fmt_cap(n):
    if n is None: return "N/A"
    if n>=1e12: return f"${n/1e12:.2f}T"
    if n>=1e9:  return f"${n/1e9:.2f}B"
    if n>=1e6:  return f"${n/1e6:.2f}M"
    return f"${n:,.0f}"

def fmt_pct(n):
    return "N/A" if n is None else f"{n*100:.2f}%"

def flt(n, pre="", suf="", dp=2):
    return "N/A" if n is None else f"{pre}{n:.{dp}f}{suf}"

def pill(text):
    t = (text or "").upper()
    if "BULLISH" in t: return '<span class="s-bull">▲ Bullish</span>'
    if "BEARISH"  in t: return '<span class="s-bear">▼ Bearish</span>'
    return '<span class="s-neut">● Neutral</span>'

def mcard(col, label, val, sub=""):
    col.markdown(
        f'<div class="mcard"><div class="ml">{label}</div>'
        f'<div class="mv">{val}</div>'
        + (f'<div class="ms">{sub}</div>' if sub else "")
        + '</div>',
        unsafe_allow_html=True,
    )

# ─── NAVBAR ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div class="nav-logo">📈 <span>FinSight</span> AI</div>
  <div class="nav-tag">⚡ Powered by Gemini 1.5 Pro</div>
</div>
""", unsafe_allow_html=True)

# ─── CHECK API KEY ─────────────────────────────────────────────────────────────
api_key = os.environ.get("GOOGLE_API_KEY", "")
if not api_key or api_key.startswith("your_"):
    st.error("⚠️ **API key missing.** Add `GOOGLE_API_KEY=...` to your `.env` file and restart the app.")
    st.stop()

# ─── SEARCH ───────────────────────────────────────────────────────────────────
_, mid, _ = st.columns([1, 2.5, 1])
with mid:
    st.markdown("""
<div class="search-wrap">
  <div class="search-title">Financial Reasoning Agent</div>
  <div class="search-sub">Enter any stock ticker to get AI-powered analysis, charts, sentiment & news</div>
</div>
""", unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1.1])
    with c1:
        ticker = st.text_input("", placeholder="e.g. AAPL  MSFT  TSLA  GOOGL  AMZN",
                               label_visibility="collapsed").upper().strip()
    with c2:
        go_btn = st.button("Analyze →", use_container_width=True)

# ─── ANALYSIS ─────────────────────────────────────────────────────────────────
if go_btn and ticker:
    with st.spinner(f"Analyzing **{ticker}** — fetching data, news & running AI…"):
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
        st.error(f"❌ {err}")
        st.stop()

    # ── Company header ─────────────────────────────────────────────────────────
    curr = fund.get("current_price")
    prev = fund.get("previous_close")
    chg  = (curr - prev)         if curr and prev else None
    chgp = (chg / prev * 100)    if chg and prev else None

    sign     = ("+" if chg and chg >= 0 else "")
    chg_cls  = ("chg-up" if chg and chg >= 0 else "chg-dn") if chg else ""
    price_blk = (
        f'<div style="text-align:right">'
        f'  <div class="co-price">${curr:,.2f}</div>'
        f'  <div class="{chg_cls}">{sign}{chg:.2f}&nbsp;&nbsp;{sign}{chgp:.2f}%</div>'
        f'  <div class="co-prev">prev. close ${prev:,.2f}</div>'
        f'</div>'
    ) if curr and prev else ""

    st.markdown(f"""
<div class="co-header">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem">
    <div>
      <div class="co-name">{fund.get("company_name", ticker)}</div>
      <div class="co-meta">
        {fund.get("exchange","")}&ensp;·&ensp;{fund.get("sector","")}&ensp;·&ensp;{fund.get("industry","")}
      </div>
      <div class="co-tick">{ticker} · {fund.get("currency","USD")}</div>
    </div>
    {price_blk}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Metrics ────────────────────────────────────────────────────────────────
    st.markdown('<div class="slabel">Key Metrics</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    mcard(cols[0], "Market Cap",      fmt_cap(fund.get("market_cap")))
    mcard(cols[1], "P/E Ratio (TTM)", flt(fund.get("pe_ratio")),
          f"Fwd {flt(fund.get('forward_pe'))}")
    mcard(cols[2], "EPS (TTM)",       flt(fund.get("eps"), "$"))
    mcard(cols[3], "52-Week High",    flt(fund.get("52w_high"), "$"))
    mcard(cols[4], "52-Week Low",     flt(fund.get("52w_low"),  "$"))

    cols2 = st.columns(5)
    mcard(cols2[0], "Beta",           flt(fund.get("beta")), "vs S&P 500")
    mcard(cols2[1], "Dividend Yield", fmt_pct(fund.get("dividend_yield")))
    mcard(cols2[2], "Revenue (TTM)",  fmt_cap(fund.get("revenue")))
    mcard(cols2[3], "Profit Margin",  fmt_pct(fund.get("profit_margin")))
    mcard(cols2[4], "Avg Volume",     f"{fund.get('avg_volume'):,}" if fund.get("avg_volume") else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="slabel">Price Charts</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🕯 Candlestick · 3 Months", "📈 Price Trend · 1 Year", "📊 Volume · 3 Months"])
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

    # ── Sentiment + Summary ────────────────────────────────────────────────────
    lc, rc = st.columns([2, 3])

    with lc:
        st.markdown('<div class="slabel">🧠 Sentiment Analysis</div>', unsafe_allow_html=True)
        st.markdown(pill(sent), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(fig_gauge(score), use_container_width=True, config={"displayModeBar": False})
        # Explanation text
        for line in (sent or "").split("\n"):
            if "EXPLANATION:" in line.upper():
                expl = line.split(":", 1)[-1].strip()
                st.markdown(
                    f'<div class="ai-card" style="font-size:.82rem;margin-top:.5rem">{expl}</div>',
                    unsafe_allow_html=True,
                )
                break

    with rc:
        st.markdown('<div class="slabel">🤖 AI Investment Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ai-card">{smry}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── News + History Table ────────────────────────────────────────────────────
    nc, tc = st.columns([3, 2])

    with nc:
        st.markdown('<div class="slabel">📰 Latest News</div>', unsafe_allow_html=True)
        if news:
            for item in news:
                url   = item.get("url", "#")
                src   = item.get("source", "")
                title = item.get("title", "No title")
                snip  = item.get("snippet", "")
                snip  = (snip[:220] + "…") if len(snip) > 220 else snip
                st.markdown(f"""
<div class="ncard">
  <div class="nsrc">{src}</div>
  <div class="ntit">
    <a href="{url}" target="_blank" style="color:#dde6f0;text-decoration:none">{title}</a>
  </div>
  <div class="nsnip">{snip}</div>
</div>""", unsafe_allow_html=True)
        else:
            st.info("No news articles found.")

    with tc:
        st.markdown('<div class="slabel">📋 Recent Price History</div>', unsafe_allow_html=True)
        if ohlcv:
            df_t = (
                pd.DataFrame(ohlcv[-25:])
                .rename(columns={"date":"Date","open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"})
                .iloc[::-1].reset_index(drop=True)
            )
            st.dataframe(
                df_t.style.format({
                    "Open":"${:.2f}", "High":"${:.2f}", "Low":"${:.2f}",
                    "Close":"${:.2f}", "Volume":"{:,}"
                }),
                use_container_width=True, height=400, hide_index=True,
            )

    # ── About ──────────────────────────────────────────────────────────────────
    if fund.get("description"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="slabel">🏢 About the Company</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ai-card" style="font-size:.85rem">{fund["description"]}</div>',
            unsafe_allow_html=True,
        )
        if fund.get("website"):
            st.markdown(f'🌐 [{fund["website"]}]({fund["website"]})')

elif go_btn:
    st.warning("Please enter a ticker symbol.")
