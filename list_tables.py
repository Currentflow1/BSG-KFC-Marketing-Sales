import sqlite3

con = sqlite3.connect("db.sqlite3")
tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    print(t[0])
con.close()