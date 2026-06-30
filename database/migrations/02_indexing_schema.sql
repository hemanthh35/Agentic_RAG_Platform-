-- Alter documents table to add new indexing fields if they don't exist
ALTER TABLE documents ADD COLUMN IF NOT EXISTS indexing_status VARCHAR(50) DEFAULT 'Unindexed';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS indexing_started_at TIMESTAMPTZ;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS indexing_completed_at TIMESTAMPTZ;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS indexing_duration FLOAT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS indexed_vector_count INTEGER DEFAULT 0;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS index_version INTEGER DEFAULT 1;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS last_indexed_at TIMESTAMPTZ;

-- Create chunks table
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    section_title VARCHAR(255),
    page_number INTEGER,
    character_count INTEGER NOT NULL,
    word_count INTEGER NOT NULL,
    start_position INTEGER,
    end_position INTEGER,
    chunk_size INTEGER NOT NULL,
    chunk_status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index chunks on document_id and status
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_status ON chunks(chunk_status);

-- Create embedding_metadata table
CREATE TABLE IF NOT EXISTS embedding_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id UUID UNIQUE NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    embedding_model VARCHAR(100) NOT NULL,
    embedding_dimension INTEGER NOT NULL,
    generation_time FLOAT,
    batch_number INTEGER,
    index_version INTEGER NOT NULL DEFAULT 1,
    generation_status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
