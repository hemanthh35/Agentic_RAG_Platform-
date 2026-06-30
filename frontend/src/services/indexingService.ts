import apiClient from "@/api/apiClient";
import type { Document, PaginatedDocumentResponse } from "@/types/document";

export interface Chunk {
  chunk_id: string;
  document_id: string;
  chunk_index: number;
  text_content: string;
  character_count: number;
  word_count: number;
  page_number: number;
  section: string;
  chunk_size: number;
}

export interface PaginatedChunkResponse {
  items: Chunk[];
  total: number;
  skip: number;
  limit: number;
}

export interface IndexStats {
  total_documents: number;
  indexed_documents: number;
  documents_processing: number;
  failed_documents: number;
  total_chunks: number;
  total_embeddings: number;
  average_chunks_per_document: number;
  average_indexing_time: number;
  vector_collection_name: string;
}

export interface VectorDbStatus {
  collection_name: string;
  status: string;
  total_indexed_vectors: number;
  collection_health: string;
  upload_progress: number;
  connection_status: string;
  last_sync_time: string | null;
}

export interface TimelineEvent {
  timestamp: string | null;
  status: "Completed" | "Failed" | "Processing" | "Pending";
  duration: number;
  description: string;
}

export const indexingService = {
  /**
   * Retrieves all document indexing jobs.
   */
  async getIndexJobs(skip: number = 0, limit: number = 100): Promise<PaginatedDocumentResponse> {
    const response = await apiClient.get<PaginatedDocumentResponse>("/api/v1/documents", {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Retrieves aggregated indexing statistics.
   */
  async getIndexStats(): Promise<IndexStats> {
    const response = await apiClient.get<IndexStats>("/api/v1/documents/indexing/stats");
    return response.data;
  },

  /**
   * Retrieves current status and health of the Vector Database.
   */
  async getVectorDbStatus(): Promise<VectorDbStatus> {
    const response = await apiClient.get<VectorDbStatus>("/api/v1/documents/indexing/vector-db/status");
    return response.data;
  },

  /**
   * Retrieves a single document's metadata.
   */
  async getDocumentDetails(documentId: string): Promise<Document> {
    const response = await apiClient.get<Document>(`/api/v1/documents/${documentId}`);
    return response.data;
  },

  /**
   * Retrieves paginated and searchable text chunks of a document.
   */
  async getDocumentChunks(
    documentId: string,
    skip: number = 0,
    limit: number = 20,
    search?: string
  ): Promise<PaginatedChunkResponse> {
    const response = await apiClient.get<PaginatedChunkResponse>(`/api/v1/documents/${documentId}/chunks`, {
      params: { skip, limit, search },
    });
    return response.data;
  },

  /**
   * Retrieves the chronological indexing timeline for a document.
   */
  async getTimeline(documentId: string): Promise<TimelineEvent[]> {
    const response = await apiClient.get<TimelineEvent[]>(`/api/v1/documents/${documentId}/indexing/timeline`);
    return response.data;
  },

  /**
   * Retrieves the detailed stdout/stderr indexing logs for a document.
   */
  async getLogs(documentId: string): Promise<string[]> {
    const response = await apiClient.get<string[]>(`/api/v1/documents/${documentId}/indexing/logs`);
    return response.data;
  },

  /**
   * Triggers a manual retry for document processing and indexing.
   */
  async retryIndexing(documentId: string): Promise<{ message: string; document_id: string }> {
    const response = await apiClient.post<{ message: string; document_id: string }>(
      `/api/v1/documents/${documentId}/process`
    );
    return response.data;
  },
};

export default indexingService;
