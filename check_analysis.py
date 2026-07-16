import pandas as pd

companies = pd.read_excel(
    "data/raw/core/companies.xlsx",
    header=1
)

analysis = pd.read_excel(
    "data/raw/core/analysis.xlsx",
    header=1
)

company_ids = set(companies["id"])

missing = analysis[~analysis["company_id"].isin(company_ids)]

print("===== Missing Company IDs =====")
print(missing)

print("\nTotal Missing:", len(missing))