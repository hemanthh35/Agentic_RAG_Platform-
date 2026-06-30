import apiClient from "@/api/apiClient";
import type { Document, PaginatedDocumentResponse } from "@/types/document";
import type { AxiosRequestConfig } from "axios";

export const documentService = {
  /**
   * Uploads a document to the server.
   *
   * @param file - The file to upload.
   * @param title - Optional title.
   * @param description - Optional description.
   * @param onUploadProgress - Callback for upload progress.
   * @returns The created document metadata.
   */
  async uploadDocument(
    file: File,
    title?: string,
    description?: string,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<Document> {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);
    if (description) formData.append("description", description);

    const config: AxiosRequestConfig = {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    };

    const response = await apiClient.post<Document>("/api/v1/documents/upload", formData, config);
    return response.data;
  },

  /**
   * Retrieves a paginated list of documents.
   *
   * @param skip - Number of records to skip.
   * @param limit - Maximum number of records to return.
   * @returns Paginated documents.
   */
  async listDocuments(skip: number = 0, limit: number = 100): Promise<PaginatedDocumentResponse> {
    const response = await apiClient.get<PaginatedDocumentResponse>("/api/v1/documents", {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Gets document metadata by ID.
   *
   * @param id - Document ID.
   * @returns Document metadata.
   */
  async getDocument(id: string): Promise<Document> {
    const response = await apiClient.get<Document>(`/api/v1/documents/${id}`);
    return response.data;
  },

  /**
   * Gets a signed download URL for a document.
   *
   * @param id - Document ID.
   * @returns Download URL object.
   */
  async getDownloadUrl(id: string): Promise<{ download_url: string }> {
    const response = await apiClient.get<{ download_url: string }>(`/api/v1/documents/${id}/download`);
    return response.data;
  },

  /**
   * Deletes a document.
   *
   * @param id - Document ID.
   * @returns Void on success.
   */
  async deleteDocument(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/documents/${id}`);
  },
};

export default documentService;
