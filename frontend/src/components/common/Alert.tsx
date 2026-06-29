import React from "react";

interface AlertProps {
  variant?: "info" | "success" | "warning" | "error";
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  variant = "info",
  title,
  children,
  onClose,
  className = "",
}) => {
  const variants = {
    info: {
      bg: "bg-pastel-blue-50 border-pastel-blue-200 text-pastel-blue-800",
      icon: (
        <svg className="w-5 h-5 text-pastel-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    success: {
      bg: "bg-pastel-green-50 border-pastel-green-200 text-pastel-green-800",
      icon: (
        <svg className="w-5 h-5 text-pastel-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    warning: {
      bg: "bg-pastel-amber-50 border-pastel-amber-200 text-pastel-amber-800",
      icon: (
        <svg className="w-5 h-5 text-pastel-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
    },
    error: {
      bg: "bg-pastel-rose-50 border-pastel-rose-200 text-pastel-rose-800",
      icon: (
        <svg className="w-5 h-5 text-pastel-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
  };

  return (
    <div
      className={`flex items-start gap-3 p-4 border rounded-2xl ${variants[variant].bg} ${className}`}
      role="alert"
    >
      <div className="flex-shrink-0 mt-0.5">{variants[variant].icon}</div>
      <div className="flex-1">
        {title && <h3 className="font-semibold text-sm mb-1">{title}</h3>}
        <div className="text-xs md:text-sm leading-relaxed">{children}</div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 p-1 ml-auto rounded-lg hover:bg-black hover:bg-opacity-5 text-current"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
};

export default Alert;
