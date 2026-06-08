# dump_sqlite_all.py
import sqlite3, csv, json, os
db = "cyber_defense.db"
conn = sqlite3.connect(db)
cur = conn.cursor()

os.makedirs("db_exports", exist_ok=True)
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]

full = {}
for t in tables:
    cur.execute(f"PRAGMA table_info('{t}')")
    cols = [r[1] for r in cur.fetchall()]
    cur.execute(f"SELECT * FROM '{t}'")
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    full[t] = {"columns": cols, "rows_count": len(rows)}
    # write CSV
    with open(f"db_exports/{t}.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        for r in rows:
            writer.writerow([str(x) if x is not None else "" for x in r])
    # small JSON per table
    with open(f"db_exports/{t}.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, default=str)

with open("db_dump_summary.json", "w", encoding="utf-8") as f:
    json.dump({"tables": full}, f, indent=2)

print("Wrote per-table CSV/JSON to db_exports/ and summary db_dump_summary.json")
conn.close()
