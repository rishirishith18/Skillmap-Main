#!/usr/bin/env python3
"""
PostgreSQL Setup Script for SkillSnap
Sets up PostgreSQL database for use with pgAdmin 4
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_header():
    print("🐘 PostgreSQL Setup for SkillSnap")
    print("=" * 40)
    print("This script helps you set up PostgreSQL for use with pgAdmin 4")
    print()

def check_postgresql_installed():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ PostgreSQL not found")
    return False

def install_postgresql_instructions():
    """Provide installation instructions for different platforms"""
    system = platform.system().lower()
    
    print("\n📦 PostgreSQL Installation Instructions:")
    print("-" * 40)
    
    if system == "darwin":  # macOS
        print("🍎 macOS:")
        print("1. Using Homebrew (recommended):")
        print("   brew install postgresql")
        print("   brew services start postgresql")
        print()
        print("2. Using PostgreSQL.app:")
        print("   Download from: https://postgresapp.com/")
        print()
        print("3. Using official installer:")
        print("   Download from: https://www.postgresql.org/download/macosx/")
        
    elif system == "linux":
        print("🐧 Linux (Ubuntu/Debian):")
        print("   sudo apt update")
        print("   sudo apt install postgresql postgresql-contrib")
        print("   sudo systemctl start postgresql")
        print("   sudo systemctl enable postgresql")
        print()
        print("🎩 Linux (RHEL/CentOS/Fedora):")
        print("   sudo dnf install postgresql postgresql-server")
        print("   sudo postgresql-setup --initdb")
        print("   sudo systemctl start postgresql")
        print("   sudo systemctl enable postgresql")
        
    elif system == "windows":
        print("🪟 Windows:")
        print("1. Download PostgreSQL installer:")
        print("   https://www.postgresql.org/download/windows/")
        print("2. Run the installer and follow the setup wizard")
        print("3. Remember the superuser password you set!")
    
    print("\n🔧 After installation, run this script again!")

def create_database_and_user():
    """Create SkillSnap database and user"""
    print("\n🔧 Setting up SkillSnap database...")
    
    commands = [
        "CREATE DATABASE skillsnap;",
        "CREATE USER skillsnap_user WITH PASSWORD 'skillsnap_password';",
        "GRANT ALL PRIVILEGES ON DATABASE skillsnap TO skillsnap_user;",
        "ALTER USER skillsnap_user CREATEDB;"
    ]
    
    try:
        for cmd in commands:
            print(f"Executing: {cmd}")
            result = subprocess.run([
                'psql', '-U', 'postgres', '-c', cmd
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                if "already exists" in result.stderr:
                    print(f"✅ Already exists, skipping...")
                else:
                    print(f"❌ Error: {result.stderr}")
                    return False
        
        print("✅ Database and user created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("\n💡 Try running manually:")
        print("psql -U postgres")
        print("Then execute these commands:")
        for cmd in commands:
            print(f"  {cmd}")
        return False

def test_connection():
    """Test connection to the SkillSnap database"""
    print("\n🧪 Testing database connection...")
    
    try:
        result = subprocess.run([
            'psql', '-U', 'skillsnap_user', '-d', 'skillsnap', '-c', 'SELECT 1;'
        ], capture_output=True, text=True, env={**os.environ, 'PGPASSWORD': 'skillsnap_password'})
        
        if result.returncode == 0:
            print("✅ Connection successful!")
            return True
        else:
            print(f"❌ Connection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def create_env_file():
    """Update .env file with PostgreSQL settings"""
    env_path = Path(".env")
    
    env_content = """# SkillSnap Backend Environment Variables
# PostgreSQL Database Configuration
DATABASE_URL=postgresql://skillsnap_user:skillsnap_password@localhost:5432/skillsnap

# OpenAI Configuration (Required for Whisper and GPT)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_WHISPER_MODEL=whisper-1

# Google Cloud Speech-to-Text (Alternative to Whisper)
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-service-account.json

# Omnidimension SDK (For voice interactions)
OMNIDIMENSION_API_KEY=your_omnidimension_api_key_here
OMNIDIMENSION_BASE_URL=https://api.omnidimension.com

# Security
SECRET_KEY=your_super_secret_key_here_change_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
ENVIRONMENT=development
DEBUG=true

# File Upload Settings
MAX_AUDIO_FILE_SIZE=26214400
UPLOAD_DIR=./uploads
AUDIO_DIR=./uploads/audio

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
"""
    
    if env_path.exists():
        backup_path = Path(".env.backup")
        env_path.rename(backup_path)
        print(f"✅ Backed up existing .env to {backup_path}")
    
    with open(env_path, "w") as f:
        f.write(env_content)
    print("✅ Created .env file with PostgreSQL configuration")

def pgadmin_setup_instructions():
    """Provide pgAdmin 4 setup instructions"""
    print("\n🔧 pgAdmin 4 Setup Instructions:")
    print("-" * 40)
    print("1. Open pgAdmin 4 (you mentioned you have it installed)")
    print("2. Right-click 'Servers' → 'Create' → 'Server'")
    print("3. Enter these connection details:")
    print("   📝 General Tab:")
    print("      Name: SkillSnap Local")
    print("   📝 Connection Tab:")
    print("      Host: localhost")
    print("      Port: 5432")
    print("      Database: skillsnap")
    print("      Username: skillsnap_user")
    print("      Password: skillsnap_password")
    print("4. Click 'Save'")
    print()
    print("✅ You can now manage your SkillSnap database through pgAdmin 4!")

def main():
    print_header()
    
    # Check if PostgreSQL is installed
    if not check_postgresql_installed():
        install_postgresql_instructions()
        return
    
    # Create database and user
    if not create_database_and_user():
        print("\n❌ Database setup failed. Please fix the errors above and try again.")
        return
    
    # Test connection
    if not test_connection():
        print("\n❌ Connection test failed. Please check your PostgreSQL installation.")
        return
    
    # Create .env file
    create_env_file()
    
    # Provide pgAdmin setup instructions
    pgadmin_setup_instructions()
    
    print("\n" + "=" * 50)
    print("🎉 PostgreSQL setup completed!")
    print("\n📝 Next steps:")
    print("1. Set up connection in pgAdmin 4 (instructions above)")
    print("2. Edit .env file with your API keys")
    print("3. Install Python dependencies: pip install -r requirements.txt")
    print("4. Start the server: python -m uvicorn main:app --reload")
    print("\n📚 Your SkillSnap database is ready for pgAdmin 4! 🐘")

if __name__ == "__main__":
    main() 