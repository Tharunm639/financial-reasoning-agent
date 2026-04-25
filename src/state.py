from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    ticker: str
    stock_data: str
    ohlcv_3m: List[Dict[str, Any]]
    close_1y: List[Dict[str, Any]]
    fundamentals: Dict[str, Any]
    news: List[Dict[str, str]]
    sentiment: str
    summary: str
    error: str
