import sqlite3

conn = sqlite3.connect("neuro_biosensors.db")

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM papers")

count = cursor.fetchone()[0]

print("Total papers:", count)

conn.close()
