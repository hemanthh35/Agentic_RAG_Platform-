import apiClient from "@/api/apiClient";
import type { Document, PaginatedDocumentResponse } from "@/types/document";

export const processingService = {
  /**
   * Retrieves all document processing jobs (proxied via listing documents).
   */
  async getProcessingJobs(skip: number = 0, limit: number = 100): Promise<PaginatedDocumentResponse> {
    const response = await apiClient.get<PaginatedDocumentResponse>("/api/v1/documents", {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Retrieves specific document processing job details.
   */
  async getJobDetails(id: string): Promise<Document> {
    const response = await apiClient.get<Document>(`/api/v1/documents/${id}`);
    return response.data;
  },

  /**
   * Triggers background processing retry or manual run for a document.
   */
  async retryJob(id: string): Promise<{ message: string; document_id: string }> {
    const response = await apiClient.post<{ message: string; document_id: string }>(
      `/api/v1/documents/${id}/process`
    );
    return response.data;
  },
};

export default processingService;
