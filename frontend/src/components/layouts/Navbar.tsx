import React from "react";

interface NavbarProps {
  onMenuClick: () => void;
  backendStatus: "connected" | "disconnected" | "loading";
}

const Navbar: React.FC<NavbarProps> = ({ onMenuClick, backendStatus }) => {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-6 bg-white border-b border-pastel-slate-100 shadow-soft">
      {/* Left section: Hamburger (mobile) + search */}
      <div className="flex items-center gap-4 flex-1">
        <button
          onClick={onMenuClick}
          className="p-1.5 rounded-lg hover:bg-pastel-slate-50 text-pastel-slate-500 lg:hidden focus:outline-none"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        {/* Global Search Bar Placeholder */}
        <div className="relative max-w-md w-full hidden md:block">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-pastel-slate-400">
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Search agents, documents, benchmarks..."
            disabled
            className="w-full pl-10 pr-4 py-2 border border-pastel-slate-100 bg-pastel-slate-50 bg-opacity-50 text-xs font-medium rounded-full cursor-not-allowed text-pastel-slate-400 focus:outline-none"
          />
        </div>
      </div>

      {/* Right section: System Status + Utility Actions + Avatar */}
      <div className="flex items-center gap-4">
        {/* System Health Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-pastel-slate-100 bg-pastel-slate-50 text-xs font-medium">
          <span className="relative flex h-2 w-2">
            {backendStatus === "connected" ? (
              <>
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pastel-green-500 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-pastel-green-500"></span>
              </>
            ) : backendStatus === "disconnected" ? (
              <>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-pastel-rose-500"></span>
              </>
            ) : (
              <>
                <span className="animate-pulse relative inline-flex rounded-full h-2 w-2 bg-pastel-amber-500"></span>
              </>
            )}
          </span>
          <span className="text-[11px] text-pastel-slate-500 tracking-wide">
            {backendStatus === "connected"
              ? "API Connected"
              : backendStatus === "disconnected"
              ? "API Disconnected"
              : "Checking API..."}
          </span>
        </div>

        {/* Theme switch indicator placeholder */}
        <button
          disabled
          className="p-2 rounded-full hover:bg-pastel-slate-50 text-pastel-slate-400 hover:text-pastel-slate-600 transition-colors cursor-not-allowed opacity-60"
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
              d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m2.828-9.9l-.707-.707m12.728 9.9l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z"
            />
          </svg>
        </button>

        {/* Notifications placeholder */}
        <button
          disabled
          className="relative p-2 rounded-full hover:bg-pastel-slate-50 text-pastel-slate-400 hover:text-pastel-slate-600 transition-colors cursor-not-allowed"
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
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
          {/* Notification dot badge */}
          <span className="absolute top-1.5 right-1.5 block h-2 w-2 rounded-full bg-pastel-purple-500 ring-2 ring-white"></span>
        </button>

        {/* User profile avatar */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-pastel-blue-100 text-pastel-blue-500 font-medium text-xs flex items-center justify-center select-none shadow-soft">
            AD
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
