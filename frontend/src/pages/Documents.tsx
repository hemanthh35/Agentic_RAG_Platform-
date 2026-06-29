import React from "react";
import PageHeader from "../components/common/PageHeader";

const Documents: React.FC = () => {
  return (
    <div className="p-1">
      <PageHeader
        title="Document Management"
        description="Upload, parse, and partition files for retrieval pipelines."
      />
      <div className="bg-white rounded-3xl p-8 border border-pastel-slate-100 shadow-soft text-center max-w-2xl mx-auto mt-10">
        <div className="w-16 h-16 bg-pastel-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-6 text-pastel-blue-500">
          <svg
            className="w-8 h-8"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-pastel-slate-800 mb-2">
          No Documents Uploaded
        </h2>
        <p className="text-pastel-slate-500 mb-6 max-w-md mx-auto text-sm">
          Document ingestion, parsing, chunking, and file management services
          will be implemented in subsequent phases.
        </p>
        <button
          disabled
          className="px-5 py-2.5 bg-pastel-blue-500 text-white rounded-full text-sm font-medium opacity-50 cursor-not-allowed"
        >
          Upload Document
        </button>
      </div>
    </div>
  );
};

export default Documents;
