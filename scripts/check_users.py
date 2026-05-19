# check_users.py
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="FileTrackDB"
)
cursor = db.cursor()

cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

print("Current users in database:")
print("-" * 50)
for user in users:
    print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[5]}")

db.close()