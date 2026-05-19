"""
FileTrack MySQL Database Setup Script
Run this to create the MySQL database and tables automatically.
"""
import os
import sys
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_db_connection(no_db=False):
    try:
        config = {
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "autocommit": True,
        }

        if not no_db:
            config["database"] = os.getenv("DB_NAME", "filetrackdb")

        return mysql.connector.connect(**config)

    except mysql.connector.Error as err:
        print(f"MySQL connection failed: {err}")
        return None


def setup_database():
    print("=" * 50)
    print("FileTrack MySQL Database Setup")
    print("=" * 50)

    sql_path = os.path.join(os.path.dirname(__file__), "database_setup.sql")
    if not os.path.exists(sql_path):
        print(f"SQL file not found: {sql_path}")
        sys.exit(1)

    with open(sql_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    print("\n1. Connecting to MySQL/XAMPP...")
    db = get_db_connection(no_db=True)
    if not db:
        print("\nTroubleshooting:")
        print("- Open XAMPP Control Panel")
        print("- Start MySQL")
        print("- Check .env DB_HOST, DB_USER, DB_PASSWORD")
        sys.exit(1)

    cursor = db.cursor()

    print("2. Running MySQL setup script...")
    statements = [s.strip() for s in sql_script.split(";") if s.strip()]

    for statement in statements:
        try:
            cursor.execute(statement)
        except mysql.connector.Error as err:
            print(f"Warning while running SQL: {err}")
            print(f"Statement: {statement[:120]}...")

    db.commit()
    cursor.close()
    db.close()

    print("\nDatabase setup complete!")
    print("\nDefault logins:")
    print("Admin: admin / 12345")
    print("User:  user  / 123")
    print("\nYou can now start the app with:")
    print("python app.py")


if __name__ == "__main__":
    setup_database()
