import React from "react";
import Card from "./Card";

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  description?: string;
  variant?: "blue" | "purple" | "green" | "rose" | "amber" | "slate";
  loading?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  description,
  variant = "slate",
  loading = false,
}) => {
  const colorVariants = {
    blue: "bg-pastel-blue-50 text-pastel-blue-500 border border-pastel-blue-100",
    purple: "bg-pastel-purple-50 text-pastel-purple-500 border border-pastel-purple-100",
    green: "bg-pastel-green-50 text-pastel-green-500 border border-pastel-green-100",
    rose: "bg-pastel-rose-50 text-pastel-rose-500 border border-pastel-rose-100",
    amber: "bg-pastel-amber-50 text-pastel-amber-500 border border-pastel-amber-100",
    slate: "bg-pastel-slate-50 text-pastel-slate-500 border border-pastel-slate-100",
  };

  return (
    <Card hoverable className="flex items-start justify-between min-h-[120px]">
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <span className="text-[10px] md:text-[11px] font-semibold text-pastel-slate-400 uppercase tracking-wider block">
            {title}
          </span>
          {loading ? (
            <div className="h-7 w-28 bg-pastel-slate-100 animate-pulse rounded-xl mt-2"></div>
          ) : (
            <span className="text-xl md:text-2xl font-bold text-pastel-slate-800 tracking-tight mt-1.5 block">
              {value}
            </span>
          )}
        </div>
        {description && (
          <span className="text-[10px] font-medium text-pastel-slate-400 mt-2 block">
            {description}
          </span>
        )}
      </div>
      {icon && (
        <div
          className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ml-4 ${colorVariants[variant]}`}
        >
          {icon}
        </div>
      )}
    </Card>
  );
};

export default StatCard;
