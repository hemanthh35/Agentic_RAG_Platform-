import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  hoverable = false,
  className = "",
  ...props
}) => {
  return (
    <div
      className={`bg-white border border-pastel-slate-100 rounded-3xl p-6 shadow-soft ${
        hoverable
          ? "hover:shadow-card hover:-translate-y-0.5 transition-all duration-300"
          : ""
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
