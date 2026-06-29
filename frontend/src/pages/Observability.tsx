import React from "react";
import PageHeader from "../components/common/PageHeader";

const Observability: React.FC = () => {
  return (
    <div className="p-1">
      <PageHeader
        title="Trace Observability"
        description="Monitor system latencies, costs, token loads, and agent call stacks."
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
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-pastel-slate-800 mb-2">
          Langfuse / Phoenix Traces
        </h2>
        <p className="text-pastel-slate-500 mb-6 max-w-md mx-auto text-sm">
          Call stack visualization, LLM token logging, cost calculators, and debug tracing integrations will be implemented in subsequent phases.
        </p>
        <button
          disabled
          className="px-5 py-2.5 bg-pastel-blue-500 text-white rounded-full text-sm font-medium opacity-50 cursor-not-allowed"
        >
          View System Logs
        </button>
      </div>
    </div>
  );
};

export default Observability;
