import React from "react";
import Button from "./Button";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Connection Failure",
  message,
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-white border border-pastel-rose-100 rounded-3xl shadow-soft py-12 max-w-md mx-auto">
      <div className="w-14 h-14 bg-pastel-rose-50 text-pastel-rose-500 rounded-2xl flex items-center justify-center mb-5 border border-pastel-rose-100">
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
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <h3 className="text-base font-semibold text-pastel-slate-800 mb-1.5">
        {title}
      </h3>
      <p className="text-xs md:text-sm text-pastel-slate-500 mb-6 max-w-xs leading-relaxed">
        {message}
      </p>
      {onRetry && (
        <Button variant="danger" size="sm" onClick={onRetry}>
          Retry Connection
        </Button>
      )}
    </div>
  );
};

export default ErrorState;
