import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import StatCard from "../components/common/StatCard";
import Badge from "../components/common/Badge";
import Button from "../common/Button";
import Skeleton from "../common/Skeleton";
import EmptyState from "../common/EmptyState";
import processingService from "@/services/processingService";
import type { Document } from "@/types/document";

const ProcessingDashboard: React.FC = () => {
  const [jobs, setJobs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchJobs = useCallback(async (showSkeleton = false) => {
    if (showSkeleton) setLoading(true);
    try {
      const res = await processingService.getProcessingJobs(0, 100);
      setJobs(res.items);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      console.error("Failed to fetch processing jobs", error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchJobs(true);
  }, [fetchJobs]);

  // Auto-refresh mechanism (every 5 seconds if active)
  useEffect(() => {
    if (!autoRefresh) return;
    
    // Check if there are any active (non-terminal) jobs
    const activeStates = ["Uploaded", "Queued", "Processing", "Retrying"];
    const hasActiveJobs = jobs.some((job) => activeStates.includes(job.processing_status));

    // Even if no active jobs, we still poll but maybe at a slower rate. 
    // Let's poll every 5s if active, or otherwise every 10s.
    const intervalTime = hasActiveJobs ? 5000 : 10000;

    const timer = setInterval(() => {
      fetchJobs(false);
    }, intervalTime);

    return () => clearInterval(timer);
  }, [autoRefresh, jobs, fetchJobs]);

  // Statistics calculation
  const totalCount = jobs.length;
  const queuedCount = jobs.filter((j) => ["Uploaded", "Queued"].includes(j.processing_status)).length;
  const processingCount = jobs.filter((j) => j.processing_status === "Processing").length;
  const completedCount = jobs.filter((j) => j.processing_status === "Completed").length;
  const failedCount = jobs.filter((j) => j.processing_status === "Failed").length;
  
  const completedJobs = jobs.filter((j) => j.processing_status === "Completed" && j.processing_duration);
  const avgDuration = completedJobs.length > 0 
    ? (completedJobs.reduce((acc, j) => acc + (j.processing_duration || 0), 0) / completedJobs.length).toFixed(2)
    : "0.00";

  const totalPages = jobs.reduce((acc, j) => acc + (j.page_count || 0), 0);
  const totalCharacters = jobs.reduce((acc, j) => acc + (j.character_count || 0), 0);

  // Active queue filter
  const activeQueue = jobs.filter((j) => 
    ["Queued", "Processing", "Retrying"].includes(j.processing_status)
  );

  const getStatusVariant = (status: string) => {
    switch (status) {
      case "Completed": return "success";
      case "Failed": return "error";
      case "Processing": return "warning";
      case "Queued":
      case "Uploaded":
      case "Retrying": return "info";
      default: return "neutral";
    }
  };

  return (
    <div className="p-1">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-6">
        <PageHeader
          title="Processing Dashboard"
          description="Control and monitor extraction status for RAG processing pipelines."
        />
        <div className="flex items-center gap-3 mt-4 md:mt-0">
          <span className="text-xs text-pastel-slate-400">
            Last updated: {lastUpdated || "never"}
          </span>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`text-xs font-medium px-2.5 py-1 rounded-full transition-colors ${
              autoRefresh 
                ? "bg-pastel-green-50 text-pastel-green-600 border border-pastel-green-200" 
                : "bg-pastel-slate-50 text-pastel-slate-400 border border-pastel-slate-200"
            }`}
          >
            {autoRefresh ? "● Auto Refresh On" : "○ Auto Refresh Off"}
          </button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => fetchJobs(true)}
            className="flex items-center gap-1 text-pastel-blue-600 hover:bg-pastel-blue-50"
          >
            <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Grid of Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Total Documents"
          value={totalCount.toString()}
          icon={<svg className="w-5 h-5 text-pastel-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
        />
        <StatCard
          title="Active Queue"
          value={(queuedCount + processingCount).toString()}
          icon={<svg className="w-5 h-5 text-pastel-amber-500 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
        />
        <StatCard
          title="Completed / Failed"
          value={`${completedCount} / ${failedCount}`}
          icon={<svg className="w-5 h-5 text-pastel-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
        />
        <StatCard
          title="Avg processing time"
          value={`${avgDuration}s`}
          icon={<svg className="w-5 h-5 text-pastel-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}
        />
      </div>

      {/* Grid of details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="bg-white p-5 rounded-2xl border border-pastel-slate-100 shadow-soft">
          <span className="text-xs font-semibold text-pastel-slate-400 block mb-1">Total Pages Extracted</span>
          <span className="text-2xl font-bold text-pastel-slate-800">{totalPages.toLocaleString()}</span>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-pastel-slate-100 shadow-soft">
          <span className="text-xs font-semibold text-pastel-slate-400 block mb-1">Characters Extracted</span>
          <span className="text-2xl font-bold text-pastel-slate-800">{totalCharacters.toLocaleString()}</span>
        </div>
      </div>

      {/* Live Processing Queue */}
      <div className="bg-white rounded-3xl p-6 lg:p-8 border border-pastel-slate-100 shadow-soft mb-8">
        <h2 className="text-lg font-semibold text-pastel-slate-800 mb-6 flex items-center gap-2">
          <span>Processing Queue</span>
          {activeQueue.length > 0 && (
            <span className="w-2.5 h-2.5 bg-pastel-amber-500 rounded-full animate-ping"></span>
          )}
        </h2>

        {loading && jobs.length === 0 ? (
          <div className="space-y-4">
            <Skeleton className="h-10 w-full rounded-xl" />
            <Skeleton className="h-10 w-full rounded-xl" />
          </div>
        ) : activeQueue.length === 0 ? (
          <EmptyState
            title="Queue is Empty"
            description="All document processing jobs have completed. Upload new documents to start pipeline."
            icon={<svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" /></svg>}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-pastel-slate-600">
              <thead className="text-xs uppercase bg-pastel-slate-50 text-pastel-slate-500 border-b border-pastel-slate-100">
                <tr>
                  <th scope="col" className="px-6 py-3 font-semibold">Filename</th>
                  <th scope="col" className="px-6 py-3 font-semibold">Stage</th>
                  <th scope="col" className="px-6 py-3 font-semibold">Status</th>
                  <th scope="col" className="px-6 py-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {activeQueue.map((job) => (
                  <tr key={job.id} className="border-b border-pastel-slate-5 hover:bg-pastel-slate-50/50">
                    <td className="px-6 py-4 font-medium text-pastel-slate-800 truncate max-w-[200px]">
                      {job.original_filename}
                    </td>
                    <td className="px-6 py-4 text-xs font-semibold text-pastel-amber-600">
                      {job.processing_status === "Processing" ? "Extracting Text..." : "Waiting in queue..."}
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={getStatusVariant(job.processing_status)}>
                        {job.processing_status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link to={`/processing/${job.id}`}>
                        <Button variant="ghost" size="sm" className="text-pastel-blue-600">
                          Monitor Details
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* History Log Table */}
      <div className="bg-white rounded-3xl p-6 lg:p-8 border border-pastel-slate-100 shadow-soft">
        <h2 className="text-lg font-semibold text-pastel-slate-800 mb-6">Recent Activities</h2>
        {loading && jobs.length === 0 ? (
          <div className="space-y-4">
            <Skeleton className="h-10 w-full rounded-xl" />
            <Skeleton className="h-10 w-full rounded-xl" />
          </div>
        ) : jobs.length === 0 ? (
          <EmptyState
            title="No Activity Logged"
            description="You haven't uploaded any documents yet."
            icon={<svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-pastel-slate-600">
              <thead className="text-xs uppercase bg-pastel-slate-50 text-pastel-slate-500 border-b border-pastel-slate-100">
                <tr>
                  <th scope="col" className="px-6 py-3 font-semibold">Document</th>
                  <th scope="col" className="px-6 py-3 font-semibold">Parser</th>
                  <th scope="col" className="px-6 py-3 font-semibold">Duration</th>
                  <th scope="col" className="px-6 py-3 font-semibold">Status</th>
                  <th scope="col" className="px-6 py-3 font-semibold text-right">Details</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id} className="border-b border-pastel-slate-5 hover:bg-pastel-slate-50/50">
                    <td className="px-6 py-4 truncate max-w-[200px]">
                      <div className="flex flex-col">
                        <span className="font-medium text-pastel-slate-800">{job.original_filename}</span>
                        <span className="text-xs text-pastel-slate-400 mt-0.5">{job.id}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-pastel-slate-500 font-mono text-xs">
                      {job.parser_used || "-"}
                    </td>
                    <td className="px-6 py-4 text-pastel-slate-500">
                      {job.processing_duration ? `${job.processing_duration.toFixed(2)}s` : "-"}
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={getStatusVariant(job.processing_status)}>
                        {job.processing_status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link to={`/processing/${job.id}`}>
                        <Button variant="ghost" size="sm" className="text-pastel-blue-600">
                          View details
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessingDashboard;
