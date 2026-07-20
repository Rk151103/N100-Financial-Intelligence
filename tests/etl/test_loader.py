from pathlib import Path

from src.etl.loader import ExcelLoader


def test_loader_initialization():
    loader = ExcelLoader("data/raw")

    assert loader.data_dir == Path("data/raw")


def test_core_file_header():
    loader = ExcelLoader()

    assert loader.get_header_row("companies") == 1
    assert loader.get_header_row("profitandloss") == 1
    assert loader.get_header_row("balancesheet") == 1
    assert loader.get_header_row("cashflow") == 1


def test_supplementary_file_header():
    loader = ExcelLoader()

    assert loader.get_header_row("sectors") == 0
    assert loader.get_header_row("stock_prices") == 0
    assert loader.get_header_row("market_cap") == 0


def test_list_excel_files():
    loader = ExcelLoader("data/raw")

    files = loader.list_excel_files()

    assert isinstance(files, list)
    assert len(files) > 0


def test_companies_file_exists():
    loader = ExcelLoader("data/raw")

    files = loader.list_excel_files()

    filenames = [
        file.name
        for file in files
    ]

    assert "companies.xlsx" in filenames