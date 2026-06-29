-- Enable UUID extension for uuid_generate_v4() function
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index user emails for faster queries
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index document status for filtering
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
