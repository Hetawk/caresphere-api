#!/usr/bin/env python3
"""
Check organization table structure
"""
import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}


def check_table():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = cursor.execute("SHOW CREATE TABLE organizations")
    result = cursor.fetchone()
    print(result[1])
    cursor.close()
    conn.close()


if __name__ == "__main__":
    check_table()
