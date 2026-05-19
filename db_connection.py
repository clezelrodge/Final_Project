"""
FileTrack MySQL database connection helper.
This file keeps the database settings in one place so app.py and setup scripts
use the same MySQL/XAMPP configuration.
"""
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def db_config(database=None, no_db=False):
    config = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "autocommit": False,
    }
    if not no_db:
        config["database"] = database or os.getenv("DB_NAME", "filetrackdb")
    return config


def get_db_connection(database=None, no_db=False):
    return mysql.connector.connect(**db_config(database=database, no_db=no_db))
