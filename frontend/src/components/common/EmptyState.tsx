import React from "react";

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-white border border-pastel-slate-100 rounded-3xl shadow-soft py-12 max-w-md mx-auto">
      {icon ? (
        <div className="mb-5">{icon}</div>
      ) : (
        <div className="w-14 h-14 bg-pastel-slate-50 text-pastel-slate-400 rounded-2xl flex items-center justify-center mb-5">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0a2 2 0 01-2 2H6a2 2 0 01-2-2m16 0V9a2 2 0 00-2-2H6a2 2 0 00-2 2v2"
            />
          </svg>
        </div>
      )}
      <h3 className="text-base font-semibold text-pastel-slate-800 mb-1.5">
        {title}
      </h3>
      <p className="text-xs md:text-sm text-pastel-slate-500 mb-6 max-w-xs leading-relaxed">
        {description}
      </p>
      {action && <div>{action}</div>}
    </div>
  );
};

export default EmptyState;
