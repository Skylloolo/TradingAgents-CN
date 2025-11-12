"""单测：验证估值指标利用 Tushare 基础信息补全"""
import pytest

from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider


@pytest.fixture
def provider():
    return OptimizedChinaDataProvider()


@pytest.fixture
def sample_financial_data():
    return {
        'balance_sheet': [
            {
                'total_assets': 800000.0,
                'total_liab': 300000.0,
                'total_hldr_eqy_exc_min_int': 500000.0,
            }
        ],
        'income_statement': [
            {
                'total_revenue': 400000.0,
                'n_income': 80000.0,
            }
        ],
        'cash_flow': [{}],
    }


def test_parse_financial_data_uses_total_share(provider, sample_financial_data):
    stock_info = {
        'code': '000001',
        'total_share': 200000.0,  # 万股
        'float_share': 150000.0,
        'total_mv': 240.0,
        'ps': 3.5,
    }

    metrics = provider._parse_financial_data(sample_financial_data, stock_info, price_value=12.0)

    assert metrics['ps'] != "N/A（无总股本数据）"
    assert metrics['pb'] != "N/A（无总股本数据）"
    assert metrics['pe'] != "N/A（无总股本数据）"
    assert metrics['total_mv'].startswith("240.00")


def test_parse_financial_data_fallback_total_mv(provider, sample_financial_data):
    stock_info = {
        'code': '000001',
        'total_share': None,
        'total_mv': 240.0,  # 亿元
        'pe': 15.0,
        'pb': 1.5,
        'ps': 3.5,
    }

    metrics = provider._parse_financial_data(sample_financial_data, stock_info, price_value=12.0)

    assert metrics['total_mv'].startswith("240.00")
    assert metrics['ps'] != "N/A（无总股本数据）"
    assert metrics['pb'] != "N/A（无总股本数据）"
    assert metrics['pe'] != "N/A（无总股本数据）"
