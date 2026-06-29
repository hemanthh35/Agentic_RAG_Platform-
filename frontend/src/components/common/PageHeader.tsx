import React from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  actions,
}) => {
  return (
    <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 pb-5 border-b border-pastel-slate-100">
      <div>
        <h1 className="text-2xl font-semibold text-pastel-slate-900 tracking-tight">
          {title}
        </h1>
        {description && (
          <p className="text-sm text-pastel-slate-500 mt-1">{description}</p>
        )}
      </div>
      {actions && (
        <div className="mt-4 md:mt-0 flex items-center gap-3">{actions}</div>
      )}
    </div>
  );
};

export default PageHeader;
