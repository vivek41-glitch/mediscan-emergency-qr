import sqlite3

conn = sqlite3.connect("medic_check.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

print(f"\nTotal registered users: {len(rows)}\n")
print("-" * 80)

for row in rows:
    print(f"ID:                {row[0]}")
    print(f"Name:              {row[1]}")
    print(f"Blood Group:       {row[2]}")
    print(f"Allergies:         {row[3]}")
    print(f"Conditions:        {row[4]}")
    print(f"Emergency Contact: {row[5]}")
    print(f"Registered On:     {row[6]}")
    print("-" * 80)

conn.close()
