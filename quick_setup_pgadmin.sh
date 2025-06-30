#!/bin/bash

# SkillSnap PostgreSQL Setup for pgAdmin 4
echo "🐘 Setting up PostgreSQL for SkillSnap + pgAdmin 4"

# Create database and user
echo "Creating SkillSnap database and user..."
psql -U postgres -c "CREATE DATABASE skillsnap;"
psql -U postgres -c "CREATE USER skillsnap_user WITH PASSWORD 'skillsnap_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE skillsnap TO skillsnap_user;"
psql -U postgres -c "ALTER USER skillsnap_user CREATEDB;"

# Connect to skillsnap database and set permissions
echo "Setting up permissions..."
psql -U postgres -d skillsnap -c "GRANT ALL ON SCHEMA public TO skillsnap_user;"
psql -U postgres -d skillsnap -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO skillsnap_user;"
psql -U postgres -d skillsnap -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO skillsnap_user;"

echo "✅ PostgreSQL setup complete!"
echo ""
echo "📋 pgAdmin 4 Connection Details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: skillsnap"
echo "   Username: skillsnap_user"
echo "   Password: skillsnap_password"
echo ""
echo "📚 Next steps:"
echo "   1. Install dependencies: pip install -r requirements.txt"
echo "   2. Open pgAdmin 4 and follow the guide in pgAdmin4_Setup_Guide.md"
echo "   3. Start SkillSnap backend: cd backend && python -m uvicorn main:app --reload" 