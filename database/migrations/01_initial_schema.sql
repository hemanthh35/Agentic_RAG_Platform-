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
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    bucket_name VARCHAR(100) NOT NULL,
    storage_path VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    description TEXT,
    processing_status VARCHAR(50) NOT NULL DEFAULT 'Uploaded',
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    processing_duration FLOAT,
    processing_error TEXT,
    parser_used VARCHAR(100),
    retry_count INTEGER NOT NULL DEFAULT 0,
    page_count INTEGER,
    character_count INTEGER,
    word_count INTEGER,
    line_count INTEGER,
    extracted_text_version INTEGER NOT NULL DEFAULT 1,
    extraction_completed BOOLEAN NOT NULL DEFAULT FALSE,
    chunk_count INTEGER,
    embedding_model VARCHAR(100),
    embedding_dimension INTEGER,
    embedding_status VARCHAR(50) DEFAULT 'Pending',
    index_status VARCHAR(50) DEFAULT 'Unindexed',
    indexed_at TIMESTAMPTZ,
    vector_collection VARCHAR(100),
    indexing_duration FLOAT,
    failed_chunk_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index document status for filtering
CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON documents(processing_status);

-- Create Extracted Texts table
CREATE TABLE IF NOT EXISTS extracted_texts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID UNIQUE NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    text_content TEXT NOT NULL,
    extraction_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    parser_used VARCHAR(100) NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1,
    character_count INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    page_count INTEGER NOT NULL,
    line_count INTEGER NOT NULL,
    extraction_status VARCHAR(50) NOT NULL,
    processing_duration FLOAT NOT NULL
);
