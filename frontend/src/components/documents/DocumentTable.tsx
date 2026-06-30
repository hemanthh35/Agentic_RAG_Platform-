import React, { useState } from "react";
import type { Document } from "@/types/document";
import Button from "../common/Button";
import Badge from "../common/Badge";
import Modal from "../common/Modal";
import EmptyState from "../common/EmptyState";
import documentService from "@/services/documentService";
import Skeleton from "../common/Skeleton";

interface DocumentTableProps {
  documents: Document[];
  loading: boolean;
  onRefresh: () => void;
}

const formatBytes = (bytes: number, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

const DocumentTable: React.FC<DocumentTableProps> = ({ documents, loading, onRefresh }) => {
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDownloading, setIsDownloading] = useState<string | null>(null);

  const handleDelete = async () => {
    if (!deleteId) return;
    setIsDeleting(true);
    try {
      await documentService.deleteDocument(deleteId);
      onRefresh();
    } catch (error) {
      console.error("Failed to delete document:", error);
      alert("Failed to delete document."); // Fallback since no toast library is specified
    } finally {
      setIsDeleting(false);
      setDeleteId(null);
    }
  };

  const handleDownload = async (id: string, filename: string) => {
    setIsDownloading(id);
    try {
      const response = await documentService.getDownloadUrl(id);
      
      // Create a temporary link to download
      const link = document.createElement("a");
      link.href = response.download_url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Failed to get download URL:", error);
      alert("Failed to download document.");
    } finally {
      setIsDownloading(null);
    }
  };

  if (loading && documents.length === 0) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-12 w-full rounded-xl" />
        <Skeleton className="h-12 w-full rounded-xl" />
        <Skeleton className="h-12 w-full rounded-xl" />
      </div>
    );
  }

  if (!loading && documents.length === 0) {
    return (
      <EmptyState
        title="No Documents Uploaded"
        description="Your uploaded documents will appear here. Start by uploading a file above."
        icon={
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        }
      />
    );
  }

  return (
    <>
      <div className="overflow-x-auto bg-white border border-pastel-slate-100 rounded-2xl shadow-soft">
        <table className="w-full text-sm text-left text-pastel-slate-600">
          <thead className="text-xs uppercase bg-pastel-slate-50 text-pastel-slate-500 border-b border-pastel-slate-100">
            <tr>
              <th scope="col" className="px-6 py-4 font-semibold">Document Name</th>
              <th scope="col" className="px-6 py-4 font-semibold">File Type</th>
              <th scope="col" className="px-6 py-4 font-semibold">File Size</th>
              <th scope="col" className="px-6 py-4 font-semibold">Status</th>
              <th scope="col" className="px-6 py-4 font-semibold">Upload Date</th>
              <th scope="col" className="px-6 py-4 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id} className="border-b border-pastel-slate-50 hover:bg-pastel-slate-50/50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex flex-col">
                    <span className="font-medium text-pastel-slate-800">{doc.original_filename}</span>
                    <span className="text-xs text-pastel-slate-400 mt-0.5 truncate max-w-[200px] lg:max-w-md">
                      {doc.description || doc.id}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-pastel-slate-500">
                  {doc.mime_type.split("/")[1]?.toUpperCase() || doc.mime_type}
                </td>
                <td className="px-6 py-4 text-pastel-slate-500">
                  {formatBytes(doc.file_size)}
                </td>
                <td className="px-6 py-4">
                  <Badge 
                    variant={doc.upload_status === 'ready' ? 'success' : doc.upload_status === 'error' ? 'error' : 'warning'}
                  >
                    {doc.upload_status}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-pastel-slate-500">
                  {new Date(doc.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex justify-end gap-2">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      isLoading={isDownloading === doc.id}
                      onClick={() => handleDownload(doc.id, doc.original_filename)}
                      className="text-pastel-blue-600 hover:text-pastel-blue-700 hover:bg-pastel-blue-50"
                    >
                      Download
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => setDeleteId(doc.id)}
                      className="text-brand-error hover:bg-red-50"
                    >
                      Delete
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        title="Confirm Deletion"
      >
        <div className="mt-2">
          <p className="text-sm text-pastel-slate-500">
            Are you sure you want to delete this document? This action cannot be undone.
          </p>
        </div>
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="outline" onClick={() => setDeleteId(null)} disabled={isDeleting}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} isLoading={isDeleting}>
            Delete
          </Button>
        </div>
      </Modal>
    </>
  );
};

export default DocumentTable;
