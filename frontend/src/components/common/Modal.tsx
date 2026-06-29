import React, { useEffect } from "react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg";
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = "md",
}) => {
  // Prevent background scrolling when modal is active
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  // Handle escape key to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  if (!isOpen) return null;

  const sizes = {
    sm: "max-w-md",
    md: "max-w-lg",
    lg: "max-w-2xl",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Dark backdrop element */}
      <div
        className="fixed inset-0 bg-pastel-slate-900 bg-opacity-20 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog Card */}
      <div
        className={`bg-white rounded-3xl w-full ${sizes[size]} shadow-card border border-pastel-slate-100 flex flex-col max-h-[90vh] z-10 overflow-hidden transform transition-all animate-in fade-in zoom-in-95 duration-200`}
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-pastel-slate-100">
          <h2 className="text-base md:text-lg font-semibold text-pastel-slate-800 tracking-tight">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-pastel-slate-50 text-pastel-slate-400 hover:text-pastel-slate-600 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 px-6 py-5 overflow-y-auto text-xs md:text-sm text-pastel-slate-600 leading-relaxed">
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-pastel-slate-100 bg-pastel-slate-50 bg-opacity-50 flex justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

export default Modal;
