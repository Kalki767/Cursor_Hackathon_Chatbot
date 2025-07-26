#!/usr/bin/env python3
"""
Database migration script for the Mental Health Support Chatbot
This script updates the existing database schema to match the new models.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from models import DATABASE_URL, Base
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_engine():
    """Get database engine"""
    if 'DATABASE_URL' in os.environ:
        return create_engine(os.environ['DATABASE_URL'])
    else:
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        return create_engine(connection_string)

def check_table_exists(engine, table_name):
    """Check if a table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)

def migrate_database():
    """Migrate the database to the new schema"""
    print("🔄 Starting database migration...")
    
    try:
        engine = get_engine()
        
        # Check if tables exist
        if not check_table_exists(engine, 'conversations'):
            print("❌ Conversations table does not exist. Creating new tables...")
            Base.metadata.create_all(bind=engine)
            print("✅ New tables created successfully!")
            return True
        
        # Check current schema
        print("📋 Checking current database schema...")
        
        # Check if user_id column exists in conversations table
        if not check_column_exists(engine, 'conversations', 'user_id'):
            print("🔄 Adding user_id column to conversations table...")
            with engine.connect() as conn:
                # Add user_id column
                conn.execute(text("ALTER TABLE conversations ADD COLUMN user_id VARCHAR"))
                conn.execute(text("CREATE INDEX ix_conversations_user_id ON conversations (user_id)"))
                conn.execute(text("ALTER TABLE conversations ADD CONSTRAINT conversations_user_id_key UNIQUE (user_id)"))
                conn.commit()
            print("✅ user_id column added to conversations table")
        
        # Check if chat_id column exists and remove it
        if check_column_exists(engine, 'conversations', 'chat_id'):
            print("🔄 Removing chat_id column from conversations table...")
            with engine.connect() as conn:
                # Drop any indexes on chat_id first
                try:
                    conn.execute(text("DROP INDEX IF EXISTS ix_conversations_chat_id"))
                    conn.execute(text("DROP INDEX IF EXISTS idx_user_chat"))
                except:
                    pass
                # Remove chat_id column
                conn.execute(text("ALTER TABLE conversations DROP COLUMN IF EXISTS chat_id"))
                conn.commit()
            print("✅ chat_id column removed from conversations table")
        
        # Check if user_id column exists in messages table
        if not check_column_exists(engine, 'messages', 'user_id'):
            print("🔄 Adding user_id column to messages table...")
            with engine.connect() as conn:
                # Add user_id column
                conn.execute(text("ALTER TABLE messages ADD COLUMN user_id VARCHAR"))
                conn.execute(text("CREATE INDEX ix_messages_user_id ON messages (user_id)"))
                conn.execute(text("CREATE INDEX idx_user_timestamp ON messages (user_id, timestamp)"))
                conn.commit()
            print("✅ user_id column added to messages table")
        
        # Update existing records to have a default user_id if needed
        print("🔄 Updating existing records...")
        with engine.connect() as conn:
            # Check if there are any conversations without user_id
            result = conn.execute(text("SELECT COUNT(*) FROM conversations WHERE user_id IS NULL"))
            null_user_count = result.scalar()
            
            if null_user_count > 0:
                print(f"⚠️  Found {null_user_count} conversations without user_id. Adding default user_id...")
                conn.execute(text("UPDATE conversations SET user_id = 'legacy_user_' || id WHERE user_id IS NULL"))
                conn.commit()
                print("✅ Updated legacy conversations with default user_id")
            
            # Check if there are any messages without user_id
            result = conn.execute(text("SELECT COUNT(*) FROM messages WHERE user_id IS NULL"))
            null_user_count = result.scalar()
            
            if null_user_count > 0:
                print(f"⚠️  Found {null_user_count} messages without user_id. Adding default user_id...")
                conn.execute(text("UPDATE messages SET user_id = 'legacy_user_' || conversation_id WHERE user_id IS NULL"))
                conn.commit()
                print("✅ Updated legacy messages with default user_id")
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        engine = get_engine()
        
        # Check if required columns exist
        required_columns = {
            'conversations': ['id', 'user_id', 'created_at', 'updated_at'],
            'messages': ['id', 'user_id', 'conversation_id', 'role', 'content', 'timestamp']
        }
        
        for table, columns in required_columns.items():
            for column in columns:
                if not check_column_exists(engine, table, column):
                    print(f"❌ Column {column} missing from {table} table")
                    return False
        
        # Check if chat_id column is removed
        if check_column_exists(engine, 'conversations', 'chat_id'):
            print("❌ chat_id column still exists in conversations table")
            return False
        
        print("✅ Migration verification successful!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Database Migration for Mental Health Support Chatbot")
    print("=" * 60)
    
    # Run migration
    if not migrate_database():
        print("❌ Migration failed!")
        return False
    
    # Verify migration
    if not verify_migration():
        print("❌ Migration verification failed!")
        return False
    
    print("\n🎉 Database migration completed successfully!")
    print("=" * 60)
    print("Next steps:")
    print("1. Restart your FastAPI application")
    print("2. Test the /chat endpoint")
    print("3. Run the test suite: python test_api.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 