import React from "react";
import { Link } from "react-router-dom";

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen bg-brand-bg flex flex-col items-center justify-center p-6 text-center">
      <div className="bg-white rounded-3xl p-10 max-w-md shadow-card border border-pastel-slate-100 flex flex-col items-center">
        {/* SVG illustration representing a soft, non-intrusive error search concept */}
        <svg
          className="w-24 h-24 text-pastel-purple-300 mb-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h1 className="text-4xl font-bold text-pastel-slate-800 mb-2">404</h1>
        <p className="text-pastel-slate-500 mb-6">
          Oops! The page you are looking for does not exist or has been moved.
        </p>
        <Link
          to="/"
          className="px-6 py-3 bg-brand-primary text-white font-medium rounded-full hover:bg-opacity-90 transition-all text-sm"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
