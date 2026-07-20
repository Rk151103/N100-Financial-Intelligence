"""
src/analytics/cashflow_kpis.py

N100 Financial Intelligence Platform
Sprint 2 - Day 11

Cash Flow KPIs & Capital Allocation
"""

import pandas as pd


class CashFlowKPI:

    # =====================================================
    # Free Cash Flow
    # =====================================================

    @staticmethod
    def free_cash_flow(
        operating_activity,
        investing_activity
    ):
        """
        FCF = Operating Cash Flow + Investing Cash Flow

        Negative FCF is allowed.
        """

        if pd.isna(operating_activity):
            return None

        if pd.isna(investing_activity):
            return None

        return round(
            operating_activity + investing_activity,
            4
        )

    # =====================================================
    # CFO / PAT Ratio
    # =====================================================

    @staticmethod
    def cfo_pat_ratio(
        operating_activity,
        net_profit
    ):
        """
        CFO / PAT Ratio.

        Returns None when PAT is zero or values are missing.
        """

        if pd.isna(operating_activity):
            return None

        if pd.isna(net_profit):
            return None

        if net_profit == 0:
            return None

        return round(
            operating_activity / net_profit,
            4
        )

    # =====================================================
    # CFO Quality Label
    # =====================================================

    @staticmethod
    def cfo_quality_label(ratio):
        """
        CFO Quality classification:

        > 1.0       = High Quality
        0.5 - 1.0  = Moderate
        < 0.5       = Accrual Risk
        """

        if ratio is None or pd.isna(ratio):
            return None

        if ratio > 1.0:
            return "High Quality"

        if ratio >= 0.5:
            return "Moderate"

        return "Accrual Risk"

    # =====================================================
    # 5-Year CFO Quality Score
    # =====================================================

    @classmethod
    def cfo_quality_score_5yr(
        cls,
        operating_activities,
        net_profits
    ):
        """
        Calculate average CFO/PAT ratio over available
        observations, intended for a 5-year window.

        Years where PAT = 0 or values are missing are skipped.
        """

        if operating_activities is None:
            return {
                "ratio": None,
                "label": None
            }

        if net_profits is None:
            return {
                "ratio": None,
                "label": None
            }

        ratios = []

        for cfo, pat in zip(
            operating_activities,
            net_profits
        ):
            ratio = cls.cfo_pat_ratio(cfo, pat)

            if ratio is not None:
                ratios.append(ratio)

        if not ratios:
            return {
                "ratio": None,
                "label": None
            }

        average_ratio = round(
            sum(ratios) / len(ratios),
            4
        )

        return {
            "ratio": average_ratio,
            "label": cls.cfo_quality_label(
                average_ratio
            )
        }

    # =====================================================
    # CapEx Intensity
    # =====================================================

    @staticmethod
    def capex_intensity(
        investing_activity,
        sales
    ):
        """
        CapEx Intensity =
            abs(investing_activity) / sales * 100

        Classification:
        < 3%    = Asset Light
        3%-8%   = Moderate
        > 8%    = Capital Intensive
        """

        if pd.isna(investing_activity):
            return {
                "value": None,
                "label": None
            }

        if pd.isna(sales) or sales == 0:
            return {
                "value": None,
                "label": None
            }

        value = round(
            abs(investing_activity) / sales * 100,
            4
        )

        if value < 3:
            label = "Asset Light"

        elif value <= 8:
            label = "Moderate"

        else:
            label = "Capital Intensive"

        return {
            "value": value,
            "label": label
        }

    # =====================================================
    # FCF Conversion Rate
    # =====================================================

    @classmethod
    def fcf_conversion_rate(
        cls,
        operating_activity,
        investing_activity,
        operating_profit
    ):
        """
        FCF Conversion Rate =
            FCF / Operating Profit * 100
        """

        if pd.isna(operating_profit):
            return None

        if operating_profit == 0:
            return None

        fcf = cls.free_cash_flow(
            operating_activity,
            investing_activity
        )

        if fcf is None:
            return None

        return round(
            fcf / operating_profit * 100,
            4
        )

    # =====================================================
    # Cash Flow Sign
    # =====================================================

    @staticmethod
    def cashflow_sign(value):
        """
        Convert a cash flow value to:
        +, -, or 0
        """

        if value is None or pd.isna(value):
            return None

        if value > 0:
            return "+"

        if value < 0:
            return "-"

        return "0"

    # =====================================================
    # Capital Allocation Pattern
    # =====================================================

    @classmethod
    def capital_allocation_pattern(
        cls,
        operating_activity,
        investing_activity,
        financing_activity,
        cfo_pat_ratio=None
    ):
        """
        Classify company cash-flow behaviour.

        Patterns:

        (+,-,-) = Reinvestor

        (+,-,-) with high CFO/PAT
                = Shareholder Returns

        (+,+,-) = Liquidating Assets

        (-,+,+) = Distress Signal

        (-,-,+) = Growth Funded by Debt

        (+,+,+) = Cash Accumulator

        (-,-,-) = Pre-Revenue

        (+,-,+) = Mixed
        """

        cfo_sign = cls.cashflow_sign(
            operating_activity
        )

        cfi_sign = cls.cashflow_sign(
            investing_activity
        )

        cff_sign = cls.cashflow_sign(
            financing_activity
        )

        if None in (
            cfo_sign,
            cfi_sign,
            cff_sign
        ):
            return "Unknown"

        pattern = (
            cfo_sign,
            cfi_sign,
            cff_sign
        )

        if pattern == ("+", "-", "-"):

            if (
                cfo_pat_ratio is not None
                and cfo_pat_ratio > 1.0
            ):
                return "Shareholder Returns"

            return "Reinvestor"

        if pattern == ("+", "+", "-"):
            return "Liquidating Assets"

        if pattern == ("-", "+", "+"):
            return "Distress Signal"

        if pattern == ("-", "-", "+"):
            return "Growth Funded by Debt"

        if pattern == ("+", "+", "+"):
            return "Cash Accumulator"

        if pattern == ("-", "-", "-"):
            return "Pre-Revenue"

        if pattern == ("+", "-", "+"):
            return "Mixed"

        return "Other"

    # =====================================================
    # Complete KPI Summary
    # =====================================================

    @classmethod
    def calculate_summary(
        cls,
        operating_activity,
        investing_activity,
        financing_activity,
        net_profit,
        sales,
        operating_profit
    ):
        """
        Calculate all Day 11 cash-flow KPIs
        for one company-year.
        """

        fcf = cls.free_cash_flow(
            operating_activity,
            investing_activity
        )

        cfo_pat = cls.cfo_pat_ratio(
            operating_activity,
            net_profit
        )

        capex = cls.capex_intensity(
            investing_activity,
            sales
        )

        conversion = cls.fcf_conversion_rate(
            operating_activity,
            investing_activity,
            operating_profit
        )

        pattern = cls.capital_allocation_pattern(
            operating_activity,
            investing_activity,
            financing_activity,
            cfo_pat
        )

        return {
            "free_cash_flow": fcf,
            "cfo_pat_ratio": cfo_pat,
            "cfo_quality_label":
                cls.cfo_quality_label(cfo_pat),
            "capex_intensity_pct":
                capex["value"],
            "capex_intensity_label":
                capex["label"],
            "fcf_conversion_rate_pct":
                conversion,
            "cfo_sign":
                cls.cashflow_sign(
                    operating_activity
                ),
            "cfi_sign":
                cls.cashflow_sign(
                    investing_activity
                ),
            "cff_sign":
                cls.cashflow_sign(
                    financing_activity
                ),
            "pattern_label":
                pattern
        }


# =========================================================
# Backward-Compatible Helper Functions
# =========================================================

def free_cash_flow(
    operating_activity,
    investing_activity
):
    return CashFlowKPI.free_cash_flow(
        operating_activity,
        investing_activity
    )


def cfo_pat_ratio(
    operating_activity,
    net_profit
):
    return CashFlowKPI.cfo_pat_ratio(
        operating_activity,
        net_profit
    )


# =========================================================
# Local Test
# =========================================================

if __name__ == "__main__":

    result = CashFlowKPI.calculate_summary(
        operating_activity=150,
        investing_activity=-50,
        financing_activity=-30,
        net_profit=100,
        sales=1000,
        operating_profit=200
    )

    print("\nCash Flow KPI Summary")

    for key, value in result.items():
        print(f"{key}: {value}")