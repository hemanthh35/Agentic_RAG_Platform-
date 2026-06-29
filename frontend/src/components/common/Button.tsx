import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "success" | "danger" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  className = "",
  disabled,
  ...props
}) => {
  const baseStyle =
    "inline-flex items-center justify-center font-medium rounded-full transition-all duration-200 outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none tracking-wide text-xs md:text-sm";

  const variants = {
    primary:
      "bg-brand-primary text-white hover:bg-opacity-90 active:scale-[0.98] focus:ring-pastel-blue-300",
    secondary:
      "bg-pastel-purple-100 text-pastel-purple-500 hover:bg-pastel-purple-200 active:scale-[0.98] focus:ring-pastel-purple-200",
    success:
      "bg-pastel-green-100 text-pastel-green-500 hover:bg-pastel-green-200 active:scale-[0.98] focus:ring-pastel-green-200",
    danger:
      "bg-pastel-rose-100 text-pastel-rose-500 hover:bg-pastel-rose-200 active:scale-[0.98] focus:ring-pastel-rose-200",
    outline:
      "border border-pastel-slate-200 bg-white text-pastel-slate-600 hover:bg-pastel-slate-50 focus:ring-pastel-slate-200",
    ghost:
      "text-pastel-slate-500 hover:bg-pastel-slate-50 hover:text-pastel-slate-800 focus:ring-pastel-slate-200",
  };

  const sizes = {
    sm: "px-4 py-1.5 text-xs",
    md: "px-5 py-2.5",
    lg: "px-7 py-3 text-base",
  };

  return (
    <button
      className={`${baseStyle} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
          fill="none"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      )}
      {children}
    </button>
  );
};

export default Button;
