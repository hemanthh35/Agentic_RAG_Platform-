import React from "react";
import PageHeader from "../components/common/PageHeader";

const Evaluation: React.FC = () => {
  return (
    <div className="p-1">
      <PageHeader
        title="Pipeline Evaluation"
        description="Verify prompt configurations, model drift, and RAG faithfulness benchmarks."
      />
      <div className="bg-white rounded-3xl p-8 border border-pastel-slate-100 shadow-soft text-center max-w-2xl mx-auto mt-10">
        <div className="w-16 h-16 bg-pastel-amber-50 rounded-2xl flex items-center justify-center mx-auto mb-6 text-pastel-amber-500">
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
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-pastel-slate-800 mb-2">
          Ragas & Benchmarks
        </h2>
        <p className="text-pastel-slate-500 mb-6 max-w-md mx-auto text-sm">
          Ragas alignment scoring, test dataset generations, precision metrics, and LLM-as-a-judge scorecards will be integrated in subsequent phases.
        </p>
        <button
          disabled
          className="px-5 py-2.5 bg-pastel-amber-500 text-white rounded-full text-sm font-medium opacity-50 cursor-not-allowed"
        >
          Run Evaluation
        </button>
      </div>
    </div>
  );
};

export default Evaluation;
