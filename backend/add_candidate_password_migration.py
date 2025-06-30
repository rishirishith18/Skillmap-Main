#!/usr/bin/env python3
"""
Migration script to add hashed_password column to candidates table
Run this script to update your database schema for candidate authentication
"""

import asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings

async def migrate_database():
    """Add hashed_password column to candidates table"""
    
    # Create async engine
    if settings.DATABASE_URL.startswith("postgresql"):
        # PostgreSQL
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
    else:
        # SQLite
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            # Check if column already exists
            if settings.DATABASE_URL.startswith("postgresql"):
                check_column_sql = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='candidates' AND column_name='hashed_password';
                """
            else:
                check_column_sql = """
                PRAGMA table_info(candidates);
                """
            
            result = await conn.execute(sa.text(check_column_sql))
            columns = result.fetchall()
            
            # Check if hashed_password column exists
            has_password_column = False
            if settings.DATABASE_URL.startswith("postgresql"):
                has_password_column = len(columns) > 0
            else:
                # For SQLite, check in the column info
                for column in columns:
                    if 'hashed_password' in str(column):
                        has_password_column = True
                        break
            
            if not has_password_column:
                print("🔄 Adding hashed_password column to candidates table...")
                
                # Add the column
                add_column_sql = """
                ALTER TABLE candidates 
                ADD COLUMN hashed_password VARCHAR(255);
                """
                
                await conn.execute(sa.text(add_column_sql))
                print("✅ Successfully added hashed_password column!")
            else:
                print("✅ hashed_password column already exists!")
                
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    asyncio.run(migrate_database())
    print("🎉 Migration completed!") 