# create_admin.py
from werkzeug.security import generate_password_hash
import mysql.connector

def create_admin(username, password, full_name, email):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="FileTrackDB"
    )
    cursor = db.cursor()
    
    hashed_password = generate_password_hash(password)
    
    try:
        cursor.execute("""
            INSERT INTO users (username, password, full_name, email, role)
            VALUES (%s, %s, %s, %s, 'admin')
        """, (username, hashed_password, full_name, email))
        db.commit()
        print(f"Admin account created: {username}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    db.close()

# Usage
create_admin("admin", "12345", "New Admin", "newadmin@filetrack.com")