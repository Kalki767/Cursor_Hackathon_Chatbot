#!/usr/bin/env python3
"""
Database setup script for the Mental Health Support Chatbot
This script helps initialize the PostgreSQL database and create necessary tables.
"""

import os
import sys
from sqlalchemy import create_engine, text
from models import create_tables, DATABASE_URL
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def test_database_connection():
    """Test the database connection"""
    try:
        # Try to connect using DATABASE_URL first
        if 'DATABASE_URL' in os.environ:
            engine = create_engine(os.environ['DATABASE_URL'])
        else:
            # Fall back to individual parameters
            connection_string = f"{DATABASE_URL}"
            engine = create_engine(connection_string)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (without specifying database)
        if 'DATABASE_URL' in os.environ:
            # Extract connection info from DATABASE_URL
            url = os.environ['DATABASE_URL']
            # Remove database name from URL
            base_url = url.rsplit('/', 1)[0]
            engine = create_engine(base_url)
        else:
            connection_string = f"{DATABASE_URL}"
            engine = create_engine(connection_string)
        
        # Check if database exists
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'"))
            if not result.fetchone():
                # Create database
                conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
                conn.commit()
                print(f"✅ Database '{DB_NAME}' created successfully!")
            else:
                print(f"✅ Database '{DB_NAME}' already exists!")
                
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False
    
    return True

def setup_tables():
    """Create all necessary tables"""
    try:
        create_tables()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Mental Health Support Chatbot Database...")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Checking environment variables...")
    if 'GEMINI_API_KEY' not in os.environ:
        print("⚠️  Warning: GEMINI_API_KEY not found in environment variables")
    else:
        print("✅ GEMINI_API_KEY found")
    
    # Test database connection
    print("\n🔌 Testing database connection...")
    if not test_database_connection():
        print("\n📝 Database connection failed. Please check your configuration:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your database credentials in .env file")
        print("3. Ensure the database exists or set up automatic creation")
        return False
    
    # Create database if needed
    print("\n🗄️  Setting up database...")
    if not create_database_if_not_exists():
        return False
    
    # Create tables
    print("\n📊 Creating database tables...")
    if not setup_tables():
        return False
    
    print("\n🎉 Database setup completed successfully!")
    print("=" * 50)
    print("Next steps:")
    print("1. Start the application: python main.py")
    print("2. Test the API endpoints")
    print("3. Monitor logs for any issues")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 