import React, { useEffect, useState, useCallback } from "react";
import PageHeader from "../components/common/PageHeader";
import StatCard from "../components/common/StatCard";
import DocumentUpload from "../components/documents/DocumentUpload";
import DocumentTable from "../components/documents/DocumentTable";
import documentService from "@/services/documentService";
import type { Document } from "@/types/document";

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalDocs, setTotalDocs] = useState(0);
  // Optional: keep track of sizes if the backend supported it, but we can fake it or ignore for now since backend doesn't send size
  const [totalSize, setTotalSize] = useState("0 MB"); 

  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const res = await documentService.listDocuments(0, 100);
      setDocuments(res.items);
      setTotalDocs(res.total);
      
      const totalBytes = res.items.reduce((acc, doc) => acc + doc.file_size, 0);
      const totalMB = (totalBytes / (1024 * 1024)).toFixed(2);
      setTotalSize(`${totalMB} MB`);
    } catch (error) {
      console.error("Failed to fetch documents", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleUploadComplete = () => {
    fetchDocuments();
  };

  return (
    <div className="p-1">
      <PageHeader
        title="Document Management"
        description="Upload, parse, and manage documents for your RAG pipelines."
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 mt-6">
        <StatCard
          title="Total Documents"
          value={totalDocs.toString()}
          icon={
            <svg className="w-5 h-5 text-pastel-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
          description={totalDocs > 0 ? "+1 since last week" : "No uploads yet"}
        />
        <StatCard
          title="Total Storage Used"
          value={totalSize}
          icon={
            <svg className="w-5 h-5 text-pastel-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
            </svg>
          }
        />
        <StatCard
          title="Storage Limit"
          value="10 GB"
          icon={
            <svg className="w-5 h-5 text-pastel-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          }
        />
      </div>

      <div className="bg-white rounded-3xl p-6 lg:p-8 border border-pastel-slate-100 shadow-soft mb-8">
        <h2 className="text-xl font-semibold text-pastel-slate-800 mb-6">Upload Documents</h2>
        <DocumentUpload onUploadComplete={handleUploadComplete} />
      </div>

      <div className="bg-white rounded-3xl p-6 lg:p-8 border border-pastel-slate-100 shadow-soft">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-pastel-slate-800">Your Documents</h2>
          <button 
            onClick={fetchDocuments}
            className="text-sm font-medium text-pastel-blue-600 hover:text-pastel-blue-700 hover:bg-pastel-blue-50 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-2"
          >
            <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
        <DocumentTable 
          documents={documents} 
          loading={loading} 
          onRefresh={fetchDocuments}
        />
      </div>
    </div>
  );
};

export default Documents;
