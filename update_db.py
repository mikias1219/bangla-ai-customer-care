#!/usr/bin/env python3
"""
Update database schema for new language support
"""
import sqlite3

def update_database():
    conn = sqlite3.connect('/root/bangla-ai-customer-care/backend/bangla.db')
    cursor = conn.cursor()

    # Add new columns to conversations table
    try:
        cursor.execute('ALTER TABLE conversations ADD COLUMN customer_name VARCHAR(255)')
        print('Added customer_name column')
    except sqlite3.OperationalError as e:
        print(f'customer_name column: {e}')

    try:
        cursor.execute('ALTER TABLE conversations ADD COLUMN customer_language VARCHAR(10) DEFAULT "bn"')
        print('Added customer_language column')
    except sqlite3.OperationalError as e:
        print(f'customer_language column: {e}')

    try:
        cursor.execute('ALTER TABLE conversations ADD COLUMN last_message_at DATETIME')
        print('Added last_message_at column')
    except sqlite3.OperationalError as e:
        print(f'last_message_at column: {e}')

    try:
        cursor.execute('ALTER TABLE conversations ADD COLUMN unread_count INTEGER DEFAULT 0')
        print('Added unread_count column')
    except sqlite3.OperationalError as e:
        print(f'unread_count column: {e}')

    # Add new column to turns table
    try:
        cursor.execute('ALTER TABLE turns ADD COLUMN text_language VARCHAR(10)')
        print('Added text_language column to turns')
    except sqlite3.OperationalError as e:
        print(f'text_language column: {e}')

    # Update existing records
    cursor.execute('UPDATE conversations SET customer_language = "bn" WHERE customer_language IS NULL')
    cursor.execute('UPDATE conversations SET unread_count = 0 WHERE unread_count IS NULL')
    cursor.execute('UPDATE conversations SET last_message_at = started_at WHERE last_message_at IS NULL')

    conn.commit()
    conn.close()
    print('Database schema updated successfully')

if __name__ == "__main__":
    update_database()
