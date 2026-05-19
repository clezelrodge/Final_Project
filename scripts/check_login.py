"""
Diagnostic script: Check why login returns "Invalid credentials"
Run: python check_login.py
"""
import mysql.connector
import os

# Same config as app.py
config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "12345"),
    "database": os.getenv("DB_NAME", "FileTrackDB")
}

print("=" * 50)
print("FileTrack Login Diagnostic")
print("=" * 50)

try:
    db = mysql.connector.connect(**config)
    print("\n✅ Database connection: OK")
except mysql.connector.Error as err:
    print(f"\n❌ Database connection FAILED: {err}")
    print("\nFix: Check your MySQL password in app.py line 55")
    exit(1)

cursor = db.cursor(dictionary=True)

# Check Users table
cursor.execute("SELECT COUNT(*) as count FROM Users")
count = cursor.fetchone()["count"]
print(f"   Users in database: {count}")

if count == 0:
    print("\n❌ No users found! Run: python setup_db.py")
else:
    print("\n   User accounts:")
    cursor.execute("SELECT username, role, password FROM Users")
    for user in cursor.fetchall():
        pw_hint = user['password'][:20] + "..." if len(user['password']) > 20 else user['password']
        hashed = "(hashed)" if len(user['password']) > 20 else "(plain text)"
        print(f"     - {user['username']} | role: {user['role']} | password: {pw_hint} {hashed}")

    # Test login
cursor.execute("SELECT * FROM Users WHERE username = %s AND role = %s", ("admin", "admin"))
admin = cursor.fetchone()
if admin:
    print("\n✅ Admin user lookup: OK")
    from werkzeug.security import check_password_hash
    try:
        if check_password_hash(admin['password'], "12345"):
            print("   Password '12345' matches (hashed)")
        else:
            print("   Password '12345' does NOT match hash")
    except:
        if admin['password'] == "12345":
            print("   Password '12345' matches (plain text)")
        else:
            print(f"   Password '12345' does NOT match (stored: {admin['password']})")
else:
    print("\n❌ Admin user not found with role='admin'")

db.close()
print("\n" + "=" * 50)
