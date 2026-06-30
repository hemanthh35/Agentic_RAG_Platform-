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
  created_at: string;
  updated_at: string;
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
