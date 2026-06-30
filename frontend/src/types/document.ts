export interface Document {
  id: string;
  original_filename: string;
  stored_filename: string;
  bucket_name: string;
  storage_path: string;
  mime_type: string;
  file_size: number;
  upload_status: string;
  description: string | null;
  
  // Document Processing Pipeline Fields
  processing_status: string;
  processing_started_at: string | null;
  processing_completed_at: string | null;
  processing_duration: number | null;
  processing_error: string | null;
  parser_used: string | null;
  retry_count: number;
  page_count: number | null;
  character_count: number | null;
  word_count: number | null;
  line_count: number | null;
  extracted_text_version: number;
  extraction_completed: boolean;

  created_at: string;
  updated_at: string;

  // Document Semantic Indexing Pipeline Fields
  chunk_count: number | null;
  embedding_model: string | null;
  embedding_dimension: number | null;
  embedding_status: string | null;
  index_status: string | null;
  indexed_at: string | null;
  vector_collection: string | null;
  indexing_duration: number | null;
  failed_chunk_count: number;
}

export interface PaginatedDocumentResponse {
  items: Document[];
  total: number;
  skip: number;
  limit: number;
}

export interface UploadDocumentRequest {
  file: File;
  title?: string;
  description?: string;
}

export interface DocumentUploadStatus {
  id: string;
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
}
