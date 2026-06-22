-- Run this once in your Supabase SQL editor (or against any PostgreSQL instance)
-- This sets up a read-only role used for the sandboxed SQL execution environment.
-- The sandbox connection can only SELECT -- no INSERT, UPDATE, DELETE, DROP, or TRUNCATE.

-- Step 1: Create the read-only role
CREATE ROLE querypilot_readonly;

-- Step 2: Allow the role to connect to the database
GRANT CONNECT ON DATABASE postgres TO querypilot_readonly;

-- Step 3: Allow the role to use the public schema
GRANT USAGE ON SCHEMA public TO querypilot_readonly;

-- Step 4: Grant SELECT on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO querypilot_readonly;

-- Step 5: Make sure the role gets SELECT on any future tables too
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO querypilot_readonly;

-- Step 6: Create a login user that uses this role
-- Replace 'your_secure_password' with a real password and store it in .env as SANDBOX_DATABASE_URL
CREATE USER querypilot_sandbox WITH PASSWORD 'your_secure_password';
GRANT querypilot_readonly TO querypilot_sandbox;
