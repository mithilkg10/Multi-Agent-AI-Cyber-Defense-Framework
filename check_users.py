import sqlite3

conn = sqlite3.connect("cyber_defense.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users;")
rows = cursor.fetchall()

print("👤 Users in DB:")
for row in rows:
    print(row)

conn.close()
