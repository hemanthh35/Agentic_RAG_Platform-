import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = "", id, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div className="flex flex-col w-full gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-xs font-semibold text-pastel-slate-600 select-none tracking-wide"
          >
            {label}
          </label>
        )}

        <input
          id={inputId}
          ref={ref}
          className={`w-full px-4 py-2.5 bg-white border ${
            error ? "border-pastel-rose-300 focus:ring-pastel-rose-200" : "border-pastel-slate-200 focus:ring-pastel-blue-200"
          } rounded-2xl text-xs md:text-sm font-medium text-pastel-slate-800 placeholder-pastel-slate-400 focus:outline-none focus:ring-2 focus:ring-offset-0 transition-all ${className}`}
          {...props}
        />

        {error ? (
          <span className="text-[11px] font-medium text-pastel-rose-500">
            {error}
          </span>
        ) : (
          helperText && (
            <span className="text-[11px] font-medium text-pastel-slate-400">
              {helperText}
            </span>
          )
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
