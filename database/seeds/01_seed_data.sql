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
INSERT INTO documents (id, title, description, status, created_at, updated_at)
VALUES 
(
    'b2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3e',
    'Introduction to Agentic RAG Systems',
    'Comprehensive setup guide outlining chunking strategies and multi-agent flows.',
    'processed',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '1 day'
),
(
    'c2c9c0d1-e2f3-4a5b-6c7d-8e9f0a1b2c3f',
    'LangGraph Architecture Specifications',
    'Trace guidelines mapping cyclical state-machine models.',
    'pending',
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;
