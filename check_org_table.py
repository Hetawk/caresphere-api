#!/usr/bin/env python3
"""
Check organization table structure
"""
import pymysql

DB_CONFIG = {
    'host': '31.97.41.230',
    'port': 9909,
    'user': 'hetawk',
    'password': 'Kwatehekd7!',
    'database': 'church_connect'
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
