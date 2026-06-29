import React from "react";

interface SkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> & {
  Circle: React.FC<SkeletonProps>;
  Line: React.FC<SkeletonProps & { widthClass?: string }>;
  Block: React.FC<SkeletonProps>;
} = ({ className = "" }) => {
  return (
    <div
      className={`bg-pastel-slate-100 animate-pulse rounded-2xl ${className}`}
    />
  );
};

Skeleton.Circle = ({ className = "" }) => {
  return (
    <div
      className={`bg-pastel-slate-100 animate-pulse rounded-full ${className}`}
    />
  );
};

Skeleton.Line = ({ className = "", widthClass = "w-full" }) => {
  return (
    <div
      className={`bg-pastel-slate-100 animate-pulse rounded-full h-3 ${widthClass} ${className}`}
    />
  );
};

Skeleton.Block = ({ className = "" }) => {
  return (
    <div
      className={`bg-pastel-slate-100 animate-pulse rounded-3xl ${className}`}
    />
  );
};

export default Skeleton;
