import React from "react";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "primary" | "success" | "warning" | "danger" | "neutral";
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "neutral",
  className = "",
  ...props
}) => {
  const baseStyle =
    "inline-flex items-center px-3 py-1 text-[11px] font-semibold rounded-full tracking-wide uppercase select-none";

  const variants = {
    primary: "bg-pastel-blue-50 text-pastel-blue-500 border border-pastel-blue-100",
    success: "bg-pastel-green-50 text-pastel-green-500 border border-pastel-green-100",
    warning: "bg-pastel-amber-50 text-pastel-amber-500 border border-pastel-amber-100",
    danger: "bg-pastel-rose-50 text-pastel-rose-500 border border-pastel-rose-100",
    neutral: "bg-pastel-slate-100 text-pastel-slate-600 border border-pastel-slate-200",
  };

  return (
    <span
      className={`${baseStyle} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;
