"""
src/analytics/cagr.py

N100 Financial Intelligence Platform
Sprint 2 - Day 10

CAGR Engine
- Revenue CAGR
- PAT CAGR
- EPS CAGR
- 3-year, 5-year and 10-year windows
- Edge-case handling
"""


class CAGREngine:
    """
    Compound Annual Growth Rate calculation engine.
    """

    # =====================================================
    # Core CAGR Calculation
    # =====================================================

    @staticmethod
    def calculate_cagr(
        beginning_value,
        ending_value,
        years
    ):
        """
        Calculate standard CAGR.

        Formula:
            ((ending / beginning) ** (1 / years) - 1) * 100

        Returns None for unsupported edge cases.
        """

        if beginning_value is None:
            return None

        if ending_value is None:
            return None

        if years is None or years <= 0:
            return None

        if beginning_value <= 0:
            return None

        if ending_value < 0:
            return None

        result = (
            (
                ending_value / beginning_value
            ) ** (1 / years)
            - 1
        ) * 100

        return round(result, 2)

    # =====================================================
    # CAGR With Edge-Case Flag
    # =====================================================

    @classmethod
    def calculate_with_flag(
        cls,
        beginning_value,
        ending_value,
        years,
        available_years=None
    ):
        """
        Calculate CAGR and return a status flag.

        Edge cases:

        Positive -> Positive:
            NORMAL

        Positive -> Negative:
            DECLINE_TO_LOSS

        Negative -> Positive:
            TURNAROUND

        Negative -> Negative:
            BOTH_NEGATIVE

        Zero beginning value:
            ZERO_BASE

        Insufficient historical data:
            INSUFFICIENT
        """

        if beginning_value is None or ending_value is None:
            return {
                "value": None,
                "flag": "INSUFFICIENT"
            }

        if years is None or years <= 0:
            return {
                "value": None,
                "flag": "INSUFFICIENT"
            }

        if (
            available_years is not None
            and available_years < years
        ):
            return {
                "value": None,
                "flag": "INSUFFICIENT"
            }

        if beginning_value == 0:
            return {
                "value": None,
                "flag": "ZERO_BASE"
            }

        if (
            beginning_value > 0
            and ending_value < 0
        ):
            return {
                "value": None,
                "flag": "DECLINE_TO_LOSS"
            }

        if (
            beginning_value < 0
            and ending_value > 0
        ):
            return {
                "value": None,
                "flag": "TURNAROUND"
            }

        if (
            beginning_value < 0
            and ending_value < 0
        ):
            return {
                "value": None,
                "flag": "BOTH_NEGATIVE"
            }

        value = cls.calculate_cagr(
            beginning_value,
            ending_value,
            years
        )

        return {
            "value": value,
            "flag": "NORMAL"
        }

    # =====================================================
    # Revenue CAGR
    # =====================================================

    @classmethod
    def revenue_cagr(
        cls,
        beginning_sales,
        ending_sales,
        years,
        available_years=None
    ):
        """
        Calculate Revenue CAGR.
        """

        return cls.calculate_with_flag(
            beginning_sales,
            ending_sales,
            years,
            available_years
        )

    # =====================================================
    # PAT CAGR
    # =====================================================

    @classmethod
    def pat_cagr(
        cls,
        beginning_pat,
        ending_pat,
        years,
        available_years=None
    ):
        """
        Calculate Profit After Tax CAGR.
        """

        return cls.calculate_with_flag(
            beginning_pat,
            ending_pat,
            years,
            available_years
        )

    # =====================================================
    # EPS CAGR
    # =====================================================

    @classmethod
    def eps_cagr(
        cls,
        beginning_eps,
        ending_eps,
        years,
        available_years=None
    ):
        """
        Calculate EPS CAGR.
        """

        return cls.calculate_with_flag(
            beginning_eps,
            ending_eps,
            years,
            available_years
        )

    # =====================================================
    # Calculate Standard Growth Windows
    # =====================================================

    @classmethod
    def calculate_growth_windows(
        cls,
        beginning_value,
        ending_value,
        available_years
    ):
        """
        Calculate CAGR for standard windows:
        - 3 years
        - 5 years
        - 10 years

        Note:
        This helper uses the supplied beginning and ending
        values for each requested window. For production
        historical-series calculations, each window should
        use its own corresponding historical start value.
        """

        output = {}

        for years in (3, 5, 10):

            result = cls.calculate_with_flag(
                beginning_value,
                ending_value,
                years,
                available_years
            )

            output[f"cagr_{years}yr"] = result["value"]

            output[
                f"cagr_{years}yr_flag"
            ] = result["flag"]

        return output


# =========================================================
# Backward-Compatible Function
# =========================================================

def calculate_cagr(
    beginning_value,
    ending_value,
    years
):
    """
    Backward-compatible CAGR function.

    Existing project tests may import:
        from src.analytics.cagr import calculate_cagr
    """

    return CAGREngine.calculate_cagr(
        beginning_value,
        ending_value,
        years
    )


# =========================================================
# Local Test
# =========================================================

if __name__ == "__main__":

    print(
        "Normal CAGR:",
        CAGREngine.calculate_with_flag(
            100,
            200,
            5
        )
    )

    print(
        "Turnaround:",
        CAGREngine.calculate_with_flag(
            -100,
            200,
            5
        )
    )

    print(
        "Decline to Loss:",
        CAGREngine.calculate_with_flag(
            100,
            -50,
            5
        )
    )

    print(
        "Zero Base:",
        CAGREngine.calculate_with_flag(
            0,
            100,
            5
        )
    )