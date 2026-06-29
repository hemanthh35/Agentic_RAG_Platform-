import React from "react";
import { useHealth } from "@/contexts/HealthContext";
import PageHeader from "@/components/common/PageHeader";
import StatCard from "@/components/common/StatCard";
import Card from "@/components/common/Card";
import ErrorState from "@/components/common/ErrorState";
import Skeleton from "@/components/common/Skeleton";
import Button from "@/components/common/Button";

const Dashboard: React.FC = () => {
  const { backendStatus, healthData, loading, error, refreshHealth } =
    useHealth();

  // Helper to format uptime into a readable string
  const formatUptime = (seconds: number | undefined): string => {
    if (seconds === undefined) return "N/A";
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    if (minutes < 60) return `${minutes}m ${remainingSeconds}s`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  const handleRefreshClick = () => {
    refreshHealth();
  };

  // If loading for the first time or fetching active states
  const showSkeletons = loading && !healthData;

  // Render network connection error state if backend is completely down
  if (backendStatus === "disconnected" && !healthData) {
    return (
      <div className="py-12">
        <PageHeader
          title="System Dashboard"
          description="Real-time monitor overview of the Agentic RAG Platform."
        />
        <div className="mt-8 flex justify-center">
          <ErrorState
            title="Backend Integration Error"
            message={
              error ||
              "Could not establish a socket or HTTP connection to the backend server. Make sure your Python FastAPI application is running."
            }
            onRetry={refreshHealth}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="p-1">
      <PageHeader
        title="System Dashboard"
        description="Real-time monitor overview of the Agentic RAG Platform."
        actions={
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefreshClick}
            loading={loading}
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.0}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H17"
              />
            </svg>
            Refresh Status
          </Button>
        }
      />

      {/* Stats Cards Grid Layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {showSkeletons ? (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white border border-pastel-slate-100 rounded-3xl p-6 shadow-soft h-[120px] flex flex-col justify-between">
              <Skeleton.Line widthClass="w-1/3" />
              <Skeleton.Line widthClass="w-2/3" />
              <Skeleton.Line widthClass="w-1/2" />
            </div>
          ))
        ) : (
          <>
            {/* Backend status card */}
            <StatCard
              title="Backend Status"
              value={healthData?.status === "healthy" ? "HEALTHY" : "DEGRADED"}
              variant={healthData?.status === "healthy" ? "green" : "amber"}
              description={`API Version: ${healthData?.version || "N/A"}`}
              icon={
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
                    d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"
                  />
                </svg>
              }
            />

            {/* SQL database status card */}
            <StatCard
              title="Database Status"
              value={
                healthData?.services.database === "connected"
                  ? "Connected"
                  : "Disconnected"
              }
              variant={
                healthData?.services.database === "connected" ? "green" : "rose"
              }
              description="SQLAlchemy DB session pool"
              icon={
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
                    d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"
                  />
                </svg>
              }
            />

            {/* Supabase status card */}
            <StatCard
              title="Vector Database"
              value="Not Initialized"
              variant="slate"
              description="Supabase Client / Vector Store placeholders"
              icon={
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
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
              }
            />

            {/* Agent Status Card */}
            <StatCard
              title="Agent Engine"
              value="Inactive"
              variant="slate"
              description="LangGraph orchestrator placeholder"
              icon={
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
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              }
            />

            {/* Environment Stage */}
            <StatCard
              title="Environment"
              value={healthData?.environment.toUpperCase() || "DEVELOPMENT"}
              variant="purple"
              description="System runtime environment configuration"
              icon={
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
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                </svg>
              }
            />

            {/* Server Uptime Card */}
            <StatCard
              title="Server Uptime"
              value={formatUptime(healthData?.uptime_seconds)}
              variant="blue"
              description="Uptime calculated since API startup"
              icon={
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
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              }
            />
          </>
        )}
      </div>

      {/* Details Box Section */}
      <Card className="mb-6">
        <h3 className="text-sm font-semibold text-pastel-slate-700 tracking-tight mb-4 flex items-center gap-2">
          <svg
            className="w-4 h-4 text-brand-primary"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          Platform Gateway Specifications
        </h3>
        {showSkeletons ? (
          <div className="space-y-3">
            <Skeleton.Line widthClass="w-full" />
            <Skeleton.Line widthClass="w-5/6" />
            <Skeleton.Line widthClass="w-4/5" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs md:text-sm text-pastel-slate-600">
            <div className="space-y-2.5">
              <div className="flex items-center justify-between pb-2.5 border-b border-pastel-slate-50">
                <span className="font-medium text-pastel-slate-400">
                  Supabase Authentication
                </span>
                <span className="font-semibold px-2 py-0.5 rounded bg-pastel-slate-100 text-[10px] text-pastel-slate-500 uppercase">
                  Placeholder
                </span>
              </div>
              <div className="flex items-center justify-between pb-2.5 border-b border-pastel-slate-50">
                <span className="font-medium text-pastel-slate-400">
                  LangGraph Orchestration
                </span>
                <span className="font-semibold px-2 py-0.5 rounded bg-pastel-slate-100 text-[10px] text-pastel-slate-500 uppercase">
                  Pre-configured
                </span>
              </div>
              <div className="flex items-center justify-between pb-2.5 border-b border-pastel-slate-50">
                <span className="font-medium text-pastel-slate-400">
                  Vector Database Provider
                </span>
                <span className="font-semibold px-2 py-0.5 rounded bg-pastel-slate-100 text-[10px] text-pastel-slate-500 uppercase">
                  Supabase pgvector
                </span>
              </div>
              <div className="flex items-center justify-between pb-2.5 border-b border-pastel-slate-50">
                <span className="font-medium text-pastel-slate-400">
                  Database Query Latency
                </span>
                <span className="font-semibold text-pastel-slate-700">
                  {healthData?.response_time_ms !== undefined ? `${healthData.response_time_ms} ms` : "N/A"}
                </span>
              </div>
            </div>
            <div className="space-y-2.5">
              <div className="flex items-center justify-between pb-2.5 border-b border-pastel-slate-50">
                <span className="font-medium text-pastel-slate-400">
                  Backend API Base URL
                </span>
                <span className="font-semibold font-mono text-[11px] text-pastel-slate-700">
                  {import.meta.env.VITE_API_URL || "http://localhost:8000"}
                </span>
              </div>
              <div className="flex items-center justify-between pb-2.5 border-b border-pastel-slate-50">
                <span className="font-medium text-pastel-slate-400">
                  CORS Configuration status
                </span>
                <span className="font-semibold px-2 py-0.5 rounded bg-pastel-green-50 text-[10px] text-pastel-green-500 uppercase">
                  Enabled
                </span>
              </div>
              <div className="flex items-center justify-between pb-2.5 border-b border-pastel-slate-50">
                <span className="font-medium text-pastel-slate-400">
                  Environment stage check
                </span>
                <span className="font-semibold text-brand-primary">
                  {healthData?.environment || "development"}
                </span>
              </div>
              <div className="flex items-center justify-between pb-2.5 border-b border-pastel-slate-50">
                <span className="font-medium text-pastel-slate-400">
                  Last Health Check
                </span>
                <span className="font-semibold text-pastel-slate-700">
                  {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleTimeString() : "N/A"}
                </span>
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Dashboard;
