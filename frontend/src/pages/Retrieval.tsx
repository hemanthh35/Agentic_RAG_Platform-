import React from "react";
import PageHeader from "../components/common/PageHeader";

const Retrieval: React.FC = () => {
  return (
    <div className="p-1">
      <PageHeader
        title="Retrieval Testing"
        description="Run semantic search queries and test retrieval performance."
      />
      <div className="bg-white rounded-3xl p-8 border border-pastel-slate-100 shadow-soft text-center max-w-2xl mx-auto mt-10">
        <div className="w-16 h-16 bg-pastel-purple-50 rounded-2xl flex items-center justify-center mx-auto mb-6 text-pastel-purple-500">
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
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-pastel-slate-800 mb-2">
          Retrieval Playground
        </h2>
        <p className="text-pastel-slate-500 mb-6 max-w-md mx-auto text-sm">
          Embedding configurations, vector search queries, hybrid retrieval
          pipelines, and reranking modules will be implemented in subsequent phases.
        </p>
        <button
          disabled
          className="px-5 py-2.5 bg-pastel-purple-500 text-white rounded-full text-sm font-medium opacity-50 cursor-not-allowed"
        >
          Execute Search
        </button>
      </div>
    </div>
  );
};

export default Retrieval;
