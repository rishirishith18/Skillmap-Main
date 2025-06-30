-- SkillSnap Database Setup for pgAdmin 4
-- Run these commands in pgAdmin 4 Query Tool or terminal

-- Create database
CREATE DATABASE skillsnap;

-- Create user with password
CREATE USER skillsnap_user WITH PASSWORD 'skillsnap_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE skillsnap TO skillsnap_user;
ALTER USER skillsnap_user CREATEDB;

-- Connect to skillsnap database and grant schema privileges
\c skillsnap;
GRANT ALL ON SCHEMA public TO skillsnap_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO skillsnap_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO skillsnap_user;

-- Create tables will be handled by the FastAPI app when it starts 