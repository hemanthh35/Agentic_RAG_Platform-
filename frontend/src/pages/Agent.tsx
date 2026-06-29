import React from "react";
import PageHeader from "../components/common/PageHeader";

const Agent: React.FC = () => {
  return (
    <div className="p-1">
      <PageHeader
        title="Agentic Workflows"
        description="Design and monitor recursive LangGraph agent graphs."
      />
      <div className="bg-white rounded-3xl p-8 border border-pastel-slate-100 shadow-soft text-center max-w-2xl mx-auto mt-10">
        <div className="w-16 h-16 bg-pastel-green-50 rounded-2xl flex items-center justify-center mx-auto mb-6 text-pastel-green-500">
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
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-pastel-slate-800 mb-2">
          LangGraph Flows
        </h2>
        <p className="text-pastel-slate-500 mb-6 max-w-md mx-auto text-sm">
          Recursive agent flows, multi-agent coordination, human-in-the-loop states, and state-machine tools will be integrated in subsequent phases.
        </p>
        <button
          disabled
          className="px-5 py-2.5 bg-pastel-green-500 text-white rounded-full text-sm font-medium opacity-50 cursor-not-allowed"
        >
          Configure Agent
        </button>
      </div>
    </div>
  );
};

export default Agent;
