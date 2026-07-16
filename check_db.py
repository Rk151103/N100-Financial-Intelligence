import sqlite3

conn = sqlite3.connect("db/nifty100.db")

print("===== COMPANIES =====")
for row in conn.execute("PRAGMA table_info(companies)"):
    print(row)

print("\n===== ANALYSIS =====")
for row in conn.execute("PRAGMA table_info(analysis)"):
    print(row)

print("\n===== ANALYSIS FOREIGN KEYS =====")
for row in conn.execute("PRAGMA foreign_key_list(analysis)"):
    print(row)

conn.close()