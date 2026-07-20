from src.analytics.ratios import FinancialRatioCalculator


def test_safe_divide():
    assert FinancialRatioCalculator.safe_divide(100, 20) == 5.0


def test_safe_divide_zero():
    assert FinancialRatioCalculator.safe_divide(100, 0) is None


def test_net_profit_margin():
    result = FinancialRatioCalculator.net_profit_margin(
        20,
        100
    )

    assert result == 20.0


def test_operating_profit_margin():
    result = FinancialRatioCalculator.operating_profit_margin(
        30,
        100
    )

    assert result == 30.0


def test_debt_to_equity():
    result = FinancialRatioCalculator.debt_to_equity(
        50,
        50,
        50
    )

    assert result == 0.5