import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import { useHealth } from "@/contexts/HealthContext";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

const AppLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { backendStatus } = useHealth();

  return (
    <div className="min-h-screen bg-brand-bg flex">
      {/* Persistent Sidebar Panel */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Layout Body wrapper */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-64 transition-all duration-300">
        {/* Top Navbar */}
        <Navbar
          onMenuClick={() => setSidebarOpen(true)}
          backendStatus={backendStatus}
        />

        {/* Content Area */}
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>

        {/* Footer Placeholder */}
        <footer className="py-4 px-6 border-t border-pastel-slate-100 bg-white text-center text-[11px] font-medium text-pastel-slate-400">
          Agentic RAG Core Integration Platform &middot; Production Ready
        </footer>
      </div>
    </div>
  );
};

export default AppLayout;
