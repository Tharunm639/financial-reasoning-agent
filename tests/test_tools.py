import pytest
from src.state import AgentState
from src.tools import fetch_stock_data_tool

def test_fetch_stock_data_tool():
    state = AgentState(ticker="AAPL", stock_data="", news=[], sentiment="", summary="", error="")
    result = fetch_stock_data_tool(state)
    
    assert "stock_data" in result
    assert "error" not in result
    assert "AAPL" in result.get("stock_data", "") or len(result.get("stock_data", "")) > 0
