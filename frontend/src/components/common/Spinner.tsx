import React from "react";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  color?: string;
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = "md",
  color = "text-brand-primary",
  className = "",
}) => {
  const sizes = {
    sm: "w-4 h-4 stroke-[3px]",
    md: "w-8 h-8 stroke-[2px]",
    lg: "w-12 h-12 stroke-[1.5px]",
  };

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <svg
        className={`animate-spin ${sizes[size]} ${color}`}
        fill="none"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          className="opacity-20"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-80"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
};

export default Spinner;
