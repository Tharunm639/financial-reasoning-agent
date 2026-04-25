import os
import yfinance as yf
from .state import AgentState


def _tavily_key():
    """Return Tavily key only if it's a real one."""
    key = os.environ.get("TAVILY_API_KEY", "")
    if key and not key.startswith("your_"):
        return key
    return None


def fetch_stock_data_tool(state: AgentState):
    ticker = state["ticker"]
    try:
        stock = yf.Ticker(ticker)
        hist_3m = stock.history(period="3mo")
        hist_1y = stock.history(period="1y")

        if hist_3m.empty:
            return {"stock_data": f"No data found for {ticker}.", "error": "Invalid ticker or no data found."}

        info = stock.info or {}

        # OHLCV for 3-month candlestick / volume charts
        ohlcv_3m = [
            {
                "date": d.strftime("%Y-%m-%d"),
                "open":  round(float(r["Open"]),   2),
                "high":  round(float(r["High"]),   2),
                "low":   round(float(r["Low"]),    2),
                "close": round(float(r["Close"]),  2),
                "volume": int(r["Volume"]),
            }
            for d, r in hist_3m.iterrows()
        ]

        # Close prices for 1-year trend line
        close_1y = [
            {"date": d.strftime("%Y-%m-%d"), "close": round(float(r["Close"]), 2)}
            for d, r in hist_1y.iterrows()
        ]

        fundamentals = {
            "company_name":  info.get("longName", ticker),
            "sector":        info.get("sector", "N/A"),
            "industry":      info.get("industry", "N/A"),
            "exchange":      info.get("exchange", ""),
            "currency":      info.get("currency", "USD"),
            "website":       info.get("website", ""),
            "description":   (info.get("longBusinessSummary") or "")[:500],
            "market_cap":    info.get("marketCap"),
            "pe_ratio":      info.get("trailingPE"),
            "forward_pe":    info.get("forwardPE"),
            "eps":           info.get("trailingEps"),
            "dividend_yield":info.get("dividendYield"),
            "52w_high":      info.get("fiftyTwoWeekHigh"),
            "52w_low":       info.get("fiftyTwoWeekLow"),
            "avg_volume":    info.get("averageVolume"),
            "beta":          info.get("beta"),
            "revenue":       info.get("totalRevenue"),
            "profit_margin": info.get("profitMargins"),
            "current_price": info.get("currentPrice") or (ohlcv_3m[-1]["close"] if ohlcv_3m else None),
            "previous_close":info.get("previousClose"),
            "day_high":      info.get("dayHigh"),
            "day_low":       info.get("dayLow"),
        }

        return {
            "stock_data":  hist_3m.tail(5).to_string(),
            "ohlcv_3m":    ohlcv_3m,
            "close_1y":    close_1y,
            "fundamentals": fundamentals,
        }
    except Exception as e:
        return {"error": f"Error fetching stock data: {str(e)}"}


def fetch_news_tool(state: AgentState):
    ticker = state["ticker"]
    fund   = state.get("fundamentals") or {}
    company = fund.get("company_name", ticker)
    query   = f"{company} {ticker} stock news earnings"

    try:
        key = _tavily_key()
        if key:
            from langchain_community.tools.tavily_search import TavilySearchResults
            results = TavilySearchResults(max_results=6).invoke({"query": query})
            news = [
                {
                    "title":   r.get("content", "")[:120],
                    "url":     r.get("url", ""),
                    "snippet": r.get("content", "")[:300],
                    "source":  (r.get("url", "").split("/")[2]).replace("www.", ""),
                }
                for r in results
            ]
        else:
            from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
            ddg = DuckDuckGoSearchAPIWrapper()
            results = ddg.results(query, max_results=6)
            news = [
                {
                    "title":   r.get("title", ""),
                    "url":     r.get("link", ""),
                    "snippet": r.get("snippet", ""),
                    "source":  (r.get("link", "").split("/")[2]).replace("www.", "") if r.get("link") else "",
                }
                for r in results
            ]
        return {"news": news}
    except Exception as e:
        return {"news": [], "error": f"News fetch failed: {str(e)}"}
