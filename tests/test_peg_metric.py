import sys
import os
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.agents.utils.agent_utils import Toolkit
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
from tradingagents.dataflows.utils import extract_growth_rate


def test_get_stock_fundamentals_includes_peg():
    config = DEFAULT_CONFIG.copy()
    config["online_tools"] = True
    toolkit = Toolkit(config)

    fake_price_data = """股票名称: 测试公司\n当前价格: ¥100.00\n"""

    fake_financials = {
        "total_mv": "100.00亿元",
        "pe": "20.0倍",
        "pe_ttm": "18.0倍",
        "peg": "1.25",
        "pb": "3.0倍",
        "ps": "5.0倍",
        "dividend_yield": "2.0%",
        "roe": "15.0%",
        "roa": "8.0%",
        "gross_margin": "35.0%",
        "net_margin": "12.0%",
        "debt_ratio": "40.0%",
        "current_ratio": "1.50",
        "quick_ratio": "1.20",
        "cash_ratio": "0.80",
        "fundamental_score": 7.5,
        "valuation_score": 6.5,
        "growth_score": 7.0,
        "risk_level": "中等",
        "data_source": "Tushare",
    }

    industry_info = {
        "industry": "新能源",
        "market": "创业板",
        "analysis": "示例行业分析",
        "market_share": "示例份额",
        "brand_value": "示例品牌",
        "tech_advantage": "示例技术优势",
        "type": "高科技",
    }

    with patch(
        "tradingagents.dataflows.interface.get_china_stock_data_unified",
        return_value=fake_price_data,
    ), patch(
        "tradingagents.dataflows.interface.get_china_stock_info_unified",
        return_value="股票代码: 300750\n股票名称: 测试公司",
    ), patch.object(
        OptimizedChinaDataProvider,
        "_estimate_financial_metrics",
        return_value=fake_financials,
    ), patch.object(
        OptimizedChinaDataProvider,
        "_get_industry_info",
        return_value=industry_info,
    ):
        result = toolkit.get_stock_fundamentals_unified.invoke(
            {
                "ticker": "300750",
                "start_date": "2025-06-01",
                "end_date": "2025-06-10",
                "curr_date": "2025-06-10",
            }
        )

    assert "市盈增长比(PEG)" in result
    assert "1.25" in result


def test_extract_growth_rate_normalizes_decimal_percentage():
    growth = extract_growth_rate({"netprofit_yoy": "0.25"})
    assert growth == 25.0
