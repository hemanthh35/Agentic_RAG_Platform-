-- Seed testing database records

-- Insert mock test user
INSERT INTO users (id, email, created_at, updated_at)
VALUES (
    'a2b9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3d',
    'testuser@agenticrag.platform',
    NOW(),
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Insert mock test documents
INSERT INTO documents (id, original_filename, stored_filename, bucket_name, storage_path, mime_type, file_size, upload_status, description, created_at, updated_at)
VALUES 
(
    'b2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3e',
    'Introduction to Agentic RAG Systems.pdf',
    'b2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3e.pdf',
    'documents',
    'b2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3e.pdf',
    'application/pdf',
    1048576,
    'ready',
    'Comprehensive setup guide outlining chunking strategies and multi-agent flows.',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 day'
),
(
    'c2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3f',
    'LangGraph Architecture Specifications.md',
    'c2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3f.md',
    'documents',
    'c2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3f.md',
    'text/markdown',
    2048,
    'pending',
    'Trace guidelines mapping cyclical state-machine models.',
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;
