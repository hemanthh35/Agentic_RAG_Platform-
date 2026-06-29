import React from "react";
import PageHeader from "../components/common/PageHeader";

const Settings: React.FC = () => {
  return (
    <div className="p-1">
      <PageHeader
        title="Settings"
        description="Configure API connections, models, prompting, and application bounds."
      />
      <div className="bg-white rounded-3xl p-8 border border-pastel-slate-100 shadow-soft text-center max-w-2xl mx-auto mt-10">
        <div className="w-16 h-16 bg-pastel-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-6 text-pastel-slate-500">
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
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-pastel-slate-800 mb-2">
          Configuration Panel
        </h2>
        <p className="text-pastel-slate-500 mb-6 max-w-md mx-auto text-sm">
          Model endpoint options, hyperparameter adjustments, prompt overrides,
          and security scopes will be configured in subsequent phases.
        </p>
        <button
          disabled
          className="px-5 py-2.5 bg-pastel-slate-500 text-white rounded-full text-sm font-medium opacity-50 cursor-not-allowed"
        >
          Save Configuration
        </button>
      </div>
    </div>
  );
};

export default Settings;
