"""
src/analytics/cagr.py

CAGR Calculator
N100 Financial Intelligence Platform
"""


def calculate_cagr(beginning_value, ending_value, years):
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Formula:
    CAGR = ((Ending Value / Beginning Value) ** (1 / Years) - 1) * 100
    """

    if beginning_value is None or ending_value is None:
        return None

    if beginning_value <= 0:
        return None

    if ending_value < 0:
        return None

    if years is None or years <= 0:
        return None

    cagr = (
        (ending_value / beginning_value)
        ** (1 / years)
        - 1
    ) * 100

    return round(cagr, 2)


if __name__ == "__main__":

    result = calculate_cagr(
        100,
        200,
        5
    )

    print(
        f"CAGR: {result}%"
    )