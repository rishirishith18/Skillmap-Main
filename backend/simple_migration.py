#!/usr/bin/env python3
"""
Simple migration script to add hashed_password column to candidates table
"""

import sqlite3
import os

def migrate_sqlite():
    """Add hashed_password column to candidates table in SQLite"""
    
    # Path to SQLite database
    db_path = "skillsnap.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(candidates);")
        columns = cursor.fetchall()
        
        # Check if hashed_password column exists
        has_password_column = any('hashed_password' in str(column) for column in columns)
        
        if not has_password_column:
            print("🔄 Adding hashed_password column to candidates table...")
            
            # Add the column
            cursor.execute("""
                ALTER TABLE candidates 
                ADD COLUMN hashed_password VARCHAR(255);
            """)
            
            conn.commit()
            print("✅ Successfully added hashed_password column!")
        else:
            print("✅ hashed_password column already exists!")
        
        # Show current table structure
        cursor.execute("PRAGMA table_info(candidates);")
        columns = cursor.fetchall()
        print("\n📋 Current candidates table structure:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    success = migrate_sqlite()
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("❌ Migration failed!") 