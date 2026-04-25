import os
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from .state import AgentState
from .tools import fetch_stock_data_tool, fetch_news_tool


def get_llm():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is missing.")
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key, temperature=0.2)


def analyze_sentiment(state: AgentState):
    news = state.get("news", [])
    if not news:
        return {"sentiment": "No news available for sentiment analysis.", "sentiment_score": 0}

    llm = get_llm()
    news_text = "\n".join([f"- {n['title']}: {n['snippet']}" for n in news])

    prompt = f"""Analyze the sentiment of the following recent news for the stock ticker {state['ticker']}.
Respond in this exact format:
SENTIMENT: [Bullish/Bearish/Neutral]
SCORE: [a number from -10 (most bearish) to +10 (most bullish)]
EXPLANATION: [2-3 sentence explanation of the overall sentiment and key factors]

News:
{news_text}"""

    try:
        response = llm.invoke([
            SystemMessage(content="You are a financial sentiment analysis expert. Be precise and concise."),
            HumanMessage(content=prompt)
        ])
        content = response.content

        # Parse score
        score = 0
        for line in content.split("\n"):
            if line.startswith("SCORE:"):
                try:
                    score = float(line.replace("SCORE:", "").strip())
                except Exception:
                    pass

        return {"sentiment": content, "sentiment_score": score}
    except Exception as e:
        return {"error": f"Error in sentiment analysis: {str(e)}", "sentiment": "N/A"}


def generate_summary(state: AgentState):
    llm = get_llm()
    fundamentals = state.get("fundamentals", {})
    company = fundamentals.get("company_name", state["ticker"])

    prompt = f"""You are a senior financial analyst. Write a professional investment summary for {company} ({state['ticker']}).

Stock Data (Recent 5 days):
{state.get('stock_data', 'N/A')}

Key Fundamentals:
- Market Cap: {fundamentals.get('market_cap')}
- P/E Ratio: {fundamentals.get('pe_ratio')}
- EPS: {fundamentals.get('eps')}
- 52W High/Low: {fundamentals.get('52w_high')} / {fundamentals.get('52w_low')}
- Beta: {fundamentals.get('beta')}
- Sector: {fundamentals.get('sector')}

Sentiment Analysis Result:
{state.get('sentiment', 'N/A')}

Write a concise 3-paragraph investment summary covering:
1. Recent performance and price action
2. Fundamental valuation and key risks
3. Overall outlook (include: This is not financial advice.)

Use clear, professional language. Be direct and insightful."""

    try:
        response = llm.invoke([
            SystemMessage(content="You are a senior financial analyst at a top investment bank. Provide concise, professional insights."),
            HumanMessage(content=prompt)
        ])
        return {"summary": response.content}
    except Exception as e:
        return {"error": f"Error generating summary: {str(e)}"}


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("fetch_stock_data", fetch_stock_data_tool)
    workflow.add_node("fetch_news", fetch_news_tool)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("generate_summary", generate_summary)

    workflow.set_entry_point("fetch_stock_data")
    workflow.add_edge("fetch_stock_data", "fetch_news")
    workflow.add_edge("fetch_news", "analyze_sentiment")
    workflow.add_edge("analyze_sentiment", "generate_summary")
    workflow.add_edge("generate_summary", END)

    return workflow.compile()


def run_agent(ticker: str):
    app = build_graph()
    initial_state = {
        "ticker": ticker.upper(),
        "stock_data": "",
        "ohlcv_3m": [],
        "close_1y": [],
        "fundamentals": {},
        "news": [],
        "sentiment": "",
        "sentiment_score": 0,
        "summary": "",
        "error": "",
    }
    return app.invoke(initial_state)
