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
INSERT INTO documents (id, original_filename, stored_filename, bucket_name, storage_path, mime_type, file_size, upload_status, description, processing_status, processing_started_at, processing_completed_at, processing_duration, processing_error, parser_used, retry_count, page_count, character_count, word_count, line_count, extracted_text_version, extraction_completed, created_at, updated_at)
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
    'Completed',
    NOW() - INTERVAL '1 day 1 minute',
    NOW() - INTERVAL '1 day',
    0.85,
    NULL,
    'pypdf',
    0,
    5,
    7200,
    1200,
    120,
    1,
    TRUE,
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
    'Uploaded',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    0,
    NULL,
    NULL,
    NULL,
    NULL,
    1,
    FALSE,
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert mock test extracted text
INSERT INTO extracted_texts (id, document_id, text_content, parser_used, version_number, character_count, word_count, page_count, line_count, extraction_status, processing_duration)
VALUES (
    'd2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3a',
    'b2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3e',
    'This is the extracted text content of Introduction to Agentic RAG Systems.',
    'pypdf',
    1,
    7200,
    1200,
    5,
    120,
    'Completed',
    0.85
) ON CONFLICT (id) DO NOTHING;
