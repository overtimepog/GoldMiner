#!/usr/bin/env python3
"""Database migration script to add missing columns"""

import sqlite3
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def add_status_column():
    """Add status column to startup_ideas table if it doesn't exist"""
    
    # Get database path
    db_path = os.getenv("DATABASE_URL", "sqlite:///./goldminer.db").replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = db_path[2:]
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"Database {db_path} does not exist. Will be created on first run.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if status column exists
        cursor.execute("PRAGMA table_info(startup_ideas)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'status' not in column_names:
            print("Adding status column to startup_ideas table...")
            cursor.execute('''
                ALTER TABLE startup_ideas 
                ADD COLUMN status VARCHAR(20) DEFAULT 'pending'
            ''')
            conn.commit()
            print("✅ Status column added successfully!")
        else:
            print("Status column already exists.")
            
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print("Table startup_ideas does not exist yet. Will be created on first run.")
        else:
            print(f"Error during migration: {e}")
            raise
    finally:
        conn.close()

def add_pain_point_evidence_table():
    """Add pain_point_evidence table if it doesn't exist"""
    
    # Get database path
    db_path = os.getenv("DATABASE_URL", "sqlite:///./goldminer.db").replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = db_path[2:]
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"Database {db_path} does not exist. Will be created on first run.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if pain_point_evidence table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pain_point_evidence'")
        if cursor.fetchone() is None:
            print("Creating pain_point_evidence table...")
            
            # Import and run the migration
            from app.db.migrations.add_pain_point_evidence import migrate
            migrate(db_path)
            
            print("✅ pain_point_evidence table created successfully!")
        else:
            print("pain_point_evidence table already exists.")
            
            # Check if subreddit and comment_count columns exist
            cursor.execute("PRAGMA table_info(pain_point_evidence)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'subreddit' not in column_names:
                print("Adding subreddit column to pain_point_evidence table...")
                cursor.execute('''
                    ALTER TABLE pain_point_evidence 
                    ADD COLUMN subreddit VARCHAR(100)
                ''')
                conn.commit()
                print("✅ Subreddit column added successfully!")
            
            if 'comment_count' not in column_names:
                print("Adding comment_count column to pain_point_evidence table...")
                cursor.execute('''
                    ALTER TABLE pain_point_evidence 
                    ADD COLUMN comment_count INTEGER
                ''')
                conn.commit()
                print("✅ Comment_count column added successfully!")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

def run_migrations():
    """Run all migrations"""
    print("Running database migrations...")
    add_status_column()
    add_pain_point_evidence_table()
    print("Migrations complete!")

if __name__ == "__main__":
    run_migrations()