import React, { useState, useRef, useCallback } from "react";
import Button from "../common/Button";
import documentService from "@/services/documentService";
import type { DocumentUploadStatus } from "@/types/document";

interface DocumentUploadProps {
  onUploadComplete: () => void;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
  "text/markdown",
];

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploads, setUploads] = useState<DocumentUploadStatus[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (!['pdf', 'docx', 'txt', 'md'].includes(ext || '')) {
         return "Unsupported file type. Please upload PDF, DOCX, TXT, or MD.";
      }
    }
    if (file.size > MAX_FILE_SIZE) {
      return "File size exceeds 10MB limit.";
    }
    return null;
  };

  const processFiles = useCallback((files: FileList | File[]) => {
    const newUploads: DocumentUploadStatus[] = Array.from(files).map((file) => {
      const error = validateFile(file);
      return {
        id: Math.random().toString(36).substring(7),
        file,
        progress: 0,
        status: error ? 'error' : 'pending',
        error: error || undefined,
      };
    });

    setUploads((prev) => [...prev, ...newUploads]);

    // Start uploading valid files
    newUploads.forEach((upload) => {
      if (upload.status === 'pending') {
        startUpload(upload);
      }
    });
  }, []);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files);
    }
    // Reset input so the same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const startUpload = async (upload: DocumentUploadStatus) => {
    setUploads((prev) =>
      prev.map((u) => (u.id === upload.id ? { ...u, status: 'uploading' } : u))
    );

    try {
      await documentService.uploadDocument(
        upload.file,
        upload.file.name,
        undefined,
        (progressEvent) => {
          const percentCompleted = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
            
          setUploads((prev) =>
            prev.map((u) =>
              u.id === upload.id ? { ...u, progress: percentCompleted } : u
            )
          );
        }
      );

      setUploads((prev) =>
        prev.map((u) => (u.id === upload.id ? { ...u, status: 'completed', progress: 100 } : u))
      );
      
      onUploadComplete();
      
      // Optionally remove completed after a delay
      setTimeout(() => {
        setUploads((prev) => prev.filter((u) => u.id !== upload.id));
      }, 3000);

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Upload failed due to network error.";
      setUploads((prev) =>
        prev.map((u) =>
          u.id === upload.id ? { ...u, status: 'error', error: errorMessage } : u
        )
      );
    }
  };

  const removeUpload = (id: string) => {
    setUploads((prev) => prev.filter((u) => u.id !== id));
  };

  return (
    <div className="mb-8">
      <div
        className={`relative border-2 border-dashed rounded-3xl p-10 text-center transition-colors ${
          isDragging
            ? "border-pastel-blue-500 bg-pastel-blue-50"
            : "border-pastel-slate-200 bg-white hover:border-pastel-blue-300"
        }`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          className="hidden"
          multiple
          accept=".pdf,.docx,.txt,.md"
        />
        
        <div className="w-16 h-16 bg-pastel-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4 text-pastel-blue-500">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        
        <h3 className="text-lg font-semibold text-pastel-slate-800 mb-1">
          Drag & Drop your documents here
        </h3>
        <p className="text-pastel-slate-500 text-sm mb-6">
          Supported formats: PDF, DOCX, TXT, MD (Max 10MB)
        </p>
        
        <Button 
          variant="primary" 
          onClick={() => fileInputRef.current?.click()}
        >
          Browse Files
        </Button>
      </div>

      {uploads.length > 0 && (
        <div className="mt-6 space-y-3">
          <h4 className="text-sm font-semibold text-pastel-slate-700">Upload Queue</h4>
          {uploads.map((upload) => (
            <div key={upload.id} className="bg-white p-4 rounded-xl border border-pastel-slate-100 flex items-center gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-pastel-slate-800 truncate">
                    {upload.file.name}
                  </span>
                  <span className="text-xs text-pastel-slate-500">
                    {(upload.file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
                
                {upload.status === 'uploading' && (
                  <div className="w-full bg-pastel-slate-100 rounded-full h-1.5 mt-2">
                    <div
                      className="bg-pastel-blue-500 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${upload.progress}%` }}
                    ></div>
                  </div>
                )}
                
                {upload.status === 'error' && (
                  <p className="text-xs text-brand-error mt-1">{upload.error}</p>
                )}
                
                {upload.status === 'completed' && (
                  <p className="text-xs text-brand-success mt-1">Upload complete</p>
                )}
              </div>
              
              <button 
                onClick={() => removeUpload(upload.id)}
                className="p-1.5 text-pastel-slate-400 hover:bg-pastel-slate-50 hover:text-brand-error rounded-lg"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
