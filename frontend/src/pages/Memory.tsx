import React from "react";
import PageHeader from "../components/common/PageHeader";

const Memory: React.FC = () => {
  return (
    <div className="p-1">
      <PageHeader
        title="Agentic Memory"
        description="Inspect short-term session context and long-term user profile schemas."
      />
      <div className="bg-white rounded-3xl p-8 border border-pastel-slate-100 shadow-soft text-center max-w-2xl mx-auto mt-10">
        <div className="w-16 h-16 bg-pastel-rose-50 rounded-2xl flex items-center justify-center mx-auto mb-6 text-pastel-rose-500">
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
              d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-pastel-slate-800 mb-2">
          Memory Store
        </h2>
        <p className="text-pastel-slate-500 mb-6 max-w-md mx-auto text-sm">
          Semantic memory search, user personalization vectors, session checkpoints, and state backups will be integrated in subsequent phases.
        </p>
        <button
          disabled
          className="px-5 py-2.5 bg-pastel-rose-500 text-white rounded-full text-sm font-medium opacity-50 cursor-not-allowed"
        >
          View Profile
        </button>
      </div>
    </div>
  );
};

export default Memory;
