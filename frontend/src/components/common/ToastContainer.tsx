import React from "react";
import { useToast } from "../../contexts/ToastContext";
import type { ToastType } from "../../contexts/ToastContext";

const ToastIcon = ({ type }: { type: ToastType }) => {
  switch (type) {
    case "success":
      return (
        <svg className="w-5 h-5 text-pastel-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
        </svg>
      );
    case "error":
      return (
        <svg className="w-5 h-5 text-pastel-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
        </svg>
      );
    case "warning":
      return (
        <svg className="w-5 h-5 text-pastel-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      );
    case "info":
    default:
      return (
        <svg className="w-5 h-5 text-pastel-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
  }
};

const getToastClasses = (type: ToastType) => {
  switch (type) {
    case "success":
      return "bg-white border-pastel-green-100 text-pastel-slate-800";
    case "error":
      return "bg-white border-pastel-rose-100 text-pastel-slate-800";
    case "warning":
      return "bg-white border-pastel-amber-100 text-pastel-slate-800";
    case "info":
    default:
      return "bg-white border-pastel-blue-100 text-pastel-slate-800";
  }
};

const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useToast();

  return (
    <div className="fixed top-20 right-6 z-[9999] flex flex-col gap-3 w-full max-w-sm pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-start gap-3 p-4 rounded-2xl border bg-white pointer-events-auto shadow-lg ${getToastClasses(
            toast.type
          )}`}
          style={{
            animation: "slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards",
          }}
        >
          <div className="flex-shrink-0 mt-0.5">
            <ToastIcon type={toast.type} />
          </div>
          <div className="flex-1 text-sm font-medium leading-5">
            {toast.message}
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="flex-shrink-0 p-0.5 rounded-lg text-pastel-slate-400 hover:bg-pastel-slate-50 hover:text-pastel-slate-600 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateY(-1rem) scale(0.9);
            opacity: 0;
          }
          to {
            transform: translateY(0) scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default ToastContainer;
