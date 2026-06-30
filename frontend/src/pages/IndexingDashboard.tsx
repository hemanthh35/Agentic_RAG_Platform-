import React, { useEffect, useState, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import StatCard from "../components/common/StatCard";
import Badge from "../components/common/Badge";
import Button from "../components/common/Button";
import Skeleton from "../components/common/Skeleton";
import EmptyState from "../components/common/EmptyState";
import { useToast } from "../contexts/ToastContext";
import indexingService from "../services/indexingService";
import type { IndexStats, VectorDbStatus } from "../services/indexingService";
import type { Document } from "@/types/document";

const IndexingDashboard: React.FC = () => {
  const [jobs, setJobs] = useState<Document[]>([]);
  const [stats, setStats] = useState<IndexStats | null>(null);
  const [vectorDb, setVectorDb] = useState<VectorDbStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const { addToast } = useToast();

  // Filter and pagination state
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState<"name" | "status" | "chunks" | "date">("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const prevJobsRef = useRef<Document[]>([]);

  const fetchDashboardData = useCallback(async (showSkeleton = false) => {
    if (showSkeleton) setLoading(true);
    try {
      const [jobsRes, statsRes, vectorRes] = await Promise.all([
        indexingService.getIndexJobs(0, 100),
        indexingService.getIndexStats(),
        indexingService.getVectorDbStatus(),
      ]);

      const newJobs = jobsRes.items;
      setJobs(newJobs);
      setStats(statsRes);
      setVectorDb(vectorRes);
      setLastUpdated(new Date().toLocaleTimeString());

      // Trigger toasts on transitions
      if (prevJobsRef.current.length > 0) {
        newJobs.forEach((newJob) => {
          const oldJob = prevJobsRef.current.find((j) => j.id === newJob.id);
          if (!oldJob) return;

          // Processing (Extraction) status transition
          if (oldJob.processing_status !== newJob.processing_status) {
            if (newJob.processing_status === "Processing") {
              addToast(`Extraction started for "${newJob.original_filename}"`, "info");
            } else if (newJob.processing_status === "Completed") {
              addToast(`Extraction completed for "${newJob.original_filename}"`, "success");
            } else if (newJob.processing_status === "Failed") {
              addToast(`Extraction failed for "${newJob.original_filename}"`, "error");
            } else if (newJob.processing_status === "Retrying") {
              addToast(`Retrying extraction for "${newJob.original_filename}"`, "warning");
            }
          }

          // Chunking (implicitly triggered right after text extraction)
          if (oldJob.processing_status === "Processing" && newJob.processing_status === "Completed") {
            addToast(`Chunking started for "${newJob.original_filename}"`, "info");
          }
          if (oldJob.chunk_count === null && newJob.chunk_count !== null && newJob.chunk_count > 0) {
            addToast(`Chunking completed: generated ${newJob.chunk_count} chunks for "${newJob.original_filename}"`, "success");
          }

          // Embedding generation status transition
          if (oldJob.embedding_status !== newJob.embedding_status) {
            if (newJob.embedding_status === "Generating") {
              addToast(`Embedding started for "${newJob.original_filename}"`, "info");
            } else if (newJob.embedding_status === "Completed") {
              addToast(`Embedding completed for "${newJob.original_filename}"`, "success");
            } else if (newJob.embedding_status === "Failed") {
              addToast(`Embedding failed for "${newJob.original_filename}"`, "error");
            }
          }

          // Index status / Qdrant Upload transition
          if (oldJob.index_status !== newJob.index_status) {
            if (newJob.index_status === "Indexing") {
              addToast(`Vector upload started for "${newJob.original_filename}"`, "info");
            } else if (newJob.index_status === "Indexed") {
              addToast(`Vector upload & index completed for "${newJob.original_filename}"`, "success");
            } else if (newJob.index_status === "Failed") {
              addToast(`Indexing failed for "${newJob.original_filename}"`, "error");
            }
          }
        });
      }

      // Check for vector collection health or connection issues
      if (prevJobsRef.current.length > 0 && vectorDb && vectorRes) {
        if (vectorDb.connection_status === "Connected" && vectorRes.connection_status !== "Connected") {
          addToast("Qdrant connection lost", "error");
        } else if (vectorDb.connection_status !== "Connected" && vectorRes.connection_status === "Connected") {
          addToast("Qdrant connection restored", "success");
        }
      }

      prevJobsRef.current = newJobs;
    } catch (error) {
      console.error("Failed to load indexing dashboard data", error);
      addToast("Failed to sync dashboard status. Reconnecting...", "error");
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  // Initial load
  useEffect(() => {
    fetchDashboardData(true);
  }, [fetchDashboardData]);

  // Auto refresh polling
  useEffect(() => {
    if (!autoRefresh) return;

    // Check if any job is currently in progress
    const activeStates = ["Uploaded", "Queued", "Processing", "Retrying", "Indexing", "Generating"];
    const hasActiveJobs = jobs.some(
      (job) =>
        activeStates.includes(job.processing_status) ||
        activeStates.includes(job.index_status || "") ||
        activeStates.includes(job.embedding_status || "")
    );

    const intervalTime = hasActiveJobs ? 5000 : 10000;
    const timer = setInterval(() => {
      fetchDashboardData(false);
    }, intervalTime);

    return () => clearInterval(timer);
  }, [autoRefresh, jobs, fetchDashboardData]);

  // Sorting handlers
  const handleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
  };

  // Filter, search and sort documents
  const filteredJobs = jobs
    .filter((job) => {
      const matchSearch =
        job.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchStatus =
        statusFilter === "all" ||
        (statusFilter === "indexed" && job.index_status === "Indexed") ||
        (statusFilter === "processing" &&
          (job.index_status === "Indexing" || ["Queued", "Processing", "Retrying"].includes(job.processing_status))) ||
        (statusFilter === "failed" && (job.index_status === "Failed" || job.processing_status === "Failed"));
      return matchSearch && matchStatus;
    })
    .sort((a, b) => {
      let comparison = 0;
      if (sortBy === "name") {
        comparison = a.original_filename.localeCompare(b.original_filename);
      } else if (sortBy === "status") {
        comparison = (a.index_status || "").localeCompare(b.index_status || "");
      } else if (sortBy === "chunks") {
        comparison = (a.chunk_count || 0) - (b.chunk_count || 0);
      } else if (sortBy === "date") {
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      }
      return sortOrder === "asc" ? comparison : -comparison;
    });

  // Paginated jobs
  const paginatedJobs = filteredJobs.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
  const totalPagesCount = Math.ceil(filteredJobs.length / itemsPerPage);

  const getStatusBadge = (job: Document) => {
    // Determine overall status
    if (job.index_status === "Indexed") {
      return (
        <Badge variant="success" className="flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
          </svg>
          Indexed
        </Badge>
      );
    }

    if (job.index_status === "Failed" || job.processing_status === "Failed") {
      return (
        <Badge variant="danger" className="flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Failed
        </Badge>
      );
    }

    if (job.index_status === "Indexing") {
      return (
        <Badge variant="warning" className="flex items-center gap-1 animate-pulse">
          <svg className="w-3.5 h-3.5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Uploading
        </Badge>
      );
    }

    if (job.embedding_status === "Generating") {
      return (
        <Badge variant="primary" className="flex items-center gap-1 animate-pulse">
          <svg className="w-3.5 h-3.5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Embedding
        </Badge>
      );
    }

    if (job.processing_status === "Processing") {
      return (
        <Badge variant="warning" className="flex items-center gap-1 animate-pulse">
          <svg className="w-3.5 h-3.5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Chunking
        </Badge>
      );
    }

    if (job.processing_status === "Retrying") {
      return (
        <Badge variant="warning" className="flex items-center gap-1">
          <svg className="w-3 h-3 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Retrying
        </Badge>
      );
    }

    return (
      <Badge variant="neutral" className="flex items-center gap-1">
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Uploaded
      </Badge>
    );
  };

  const getEmbedBadge = (status: string | null) => {
    switch (status) {
      case "Completed":
        return <Badge variant="success">Completed</Badge>;
      case "Failed":
        return <Badge variant="danger">Failed</Badge>;
      case "Generating":
        return <Badge variant="warning" className="animate-pulse">Generating</Badge>;
      default:
        return <Badge variant="neutral">Pending</Badge>;
    }
  };

  const getVectorBadge = (status: string | null) => {
    switch (status) {
      case "Indexed":
        return <Badge variant="success">Indexed</Badge>;
      case "Failed":
        return <Badge variant="danger">Failed</Badge>;
      case "Indexing":
        return <Badge variant="warning" className="animate-pulse">Uploading</Badge>;
      default:
        return <Badge variant="neutral">Pending</Badge>;
    }
  };

  // Active queue
  const activeQueue = jobs.filter((j) =>
    ["Queued", "Processing", "Retrying"].includes(j.processing_status) ||
    j.index_status === "Indexing" ||
    j.embedding_status === "Generating"
  );

  return (
    <div className="p-1">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-8">
        <PageHeader
          title="Knowledge Index Operations"
          description="Monitor and orchestrate semantic chunking, embeddings generation, and vector indexing pipelines."
        />
        <div className="flex items-center gap-3 mt-4 md:mt-0 bg-white p-2.5 rounded-2xl border border-pastel-slate-100 shadow-soft">
          <span className="text-xs text-pastel-slate-400 font-medium">
            Sync Status: {lastUpdated ? `Active (${lastUpdated})` : "loading..."}
          </span>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`text-xs font-semibold px-3 py-1.5 rounded-xl border transition-all ${
              autoRefresh
                ? "bg-pastel-green-50 text-pastel-green-600 border-pastel-green-200"
                : "bg-pastel-slate-50 text-pastel-slate-400 border-pastel-slate-200"
            }`}
          >
            {autoRefresh ? "● Polling Active" : "○ Polling Paused"}
          </button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => fetchDashboardData(true)}
            className="flex items-center gap-1.5 text-pastel-blue-600 hover:bg-pastel-blue-50 border border-pastel-blue-100"
          >
            <svg className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Sync Now
          </Button>
        </div>
      </div>

      {loading && !stats ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Skeleton className="h-28 rounded-2xl" />
          <Skeleton className="h-28 rounded-2xl" />
          <Skeleton className="h-28 rounded-2xl" />
          <Skeleton className="h-28 rounded-2xl" />
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            title="Total Documents"
            value={stats?.total_documents?.toLocaleString() || "0"}
            icon={<svg className="w-5 h-5 text-pastel-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}
          />
          <StatCard
            title="Indexed Documents"
            value={stats?.indexed_documents?.toLocaleString() || "0"}
            icon={<svg className="w-5 h-5 text-pastel-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          />
          <StatCard
            title="Processing / Failed"
            value={`${stats?.documents_processing || 0} / ${stats?.failed_documents || 0}`}
            icon={<svg className="w-5 h-5 text-pastel-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          />
          <StatCard
            title="Total Chunks"
            value={stats?.total_chunks?.toLocaleString() || "0"}
            icon={<svg className="w-5 h-5 text-pastel-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4z" /></svg>}
          />
        </div>
      )}

      {/* Database/Embed and collection status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft">
          <h3 className="text-sm font-semibold text-pastel-slate-800 mb-4 uppercase tracking-wider flex items-center gap-2">
            <span className="w-2 h-2 bg-pastel-blue-500 rounded-full"></span>
            Pipeline Metrics Summary
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-pastel-slate-50 p-4 rounded-2xl text-center">
              <span className="text-[11px] font-semibold text-pastel-slate-400 uppercase tracking-wide">Total Embeddings</span>
              <span className="text-xl font-bold text-pastel-slate-800 block mt-1">{stats?.total_embeddings?.toLocaleString() || "0"}</span>
            </div>
            <div className="bg-pastel-slate-50 p-4 rounded-2xl text-center">
              <span className="text-[11px] font-semibold text-pastel-slate-400 uppercase tracking-wide">Avg Chunks / Doc</span>
              <span className="text-xl font-bold text-pastel-slate-800 block mt-1">{stats?.average_chunks_per_document || "0"}</span>
            </div>
            <div className="bg-pastel-slate-50 p-4 rounded-2xl text-center">
              <span className="text-[11px] font-semibold text-pastel-slate-400 uppercase tracking-wide">Avg Index Duration</span>
              <span className="text-xl font-bold text-pastel-slate-800 block mt-1">{stats?.average_indexing_time ? `${stats.average_indexing_time.toFixed(2)}s` : "0.00s"}</span>
            </div>
            <div className="bg-pastel-slate-50 p-4 rounded-2xl text-center">
              <span className="text-[11px] font-semibold text-pastel-slate-400 uppercase tracking-wide">Vector DB Type</span>
              <span className="text-xl font-bold text-pastel-slate-800 block mt-1">Qdrant Cloud</span>
            </div>
          </div>
        </div>

        {/* Vector DB status */}
        <div className="bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-pastel-slate-800 mb-3 uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${vectorDb?.status === "Green" ? "bg-pastel-green-500 animate-pulse" : "bg-pastel-rose-500"}`}></span>
                Vector Database Status
              </span>
              <Badge variant={vectorDb?.status === "Green" ? "success" : "danger"}>
                {vectorDb?.connection_status || "Disconnected"}
              </Badge>
            </h3>
            <div className="space-y-2.5 mt-4">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-pastel-slate-400">Collection Name:</span>
                <span className="text-pastel-slate-700 font-mono">{vectorDb?.collection_name || "semantic_chunks"}</span>
              </div>
              <div className="flex justify-between text-xs font-medium">
                <span className="text-pastel-slate-400">Indexed Vectors:</span>
                <span className="text-pastel-slate-700">{vectorDb?.total_indexed_vectors?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between text-xs font-medium">
                <span className="text-pastel-slate-400">Collection Health:</span>
                <span className="text-pastel-slate-700">{vectorDb?.collection_health || "Unknown"}</span>
              </div>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-pastel-slate-50 text-[10px] text-pastel-slate-400 flex justify-between font-medium">
            <span>Last Sync Time:</span>
            <span>{vectorDb?.last_sync_time ? new Date(vectorDb.last_sync_time).toLocaleTimeString() : "Never"}</span>
          </div>
        </div>
      </div>

      {/* Live Indexing Queue */}
      <div className="bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft mb-8">
        <h2 className="text-base font-bold text-pastel-slate-800 mb-6 flex items-center gap-2">
          <span>Active Indexing Queue</span>
          {activeQueue.length > 0 ? (
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pastel-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-pastel-amber-500"></span>
            </span>
          ) : null}
        </h2>

        {loading && jobs.length === 0 ? (
          <div className="space-y-3">
            <Skeleton className="h-10 w-full rounded-xl" />
            <Skeleton className="h-10 w-full rounded-xl" />
          </div>
        ) : activeQueue.length === 0 ? (
          <div className="text-center py-6">
            <span className="text-xs text-pastel-slate-400 font-semibold block">All tasks completed. Queue is clean.</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-pastel-slate-600">
              <thead className="text-xs uppercase bg-pastel-slate-50 text-pastel-slate-500 border-b border-pastel-slate-100">
                <tr>
                  <th className="px-6 py-3.5 font-semibold">Document Name</th>
                  <th className="px-6 py-3.5 font-semibold">Text Extraction</th>
                  <th className="px-6 py-3.5 font-semibold">Embeddings Status</th>
                  <th className="px-6 py-3.5 font-semibold">Vector Indexing</th>
                  <th className="px-6 py-3.5 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {activeQueue.map((job) => (
                  <tr key={job.id} className="border-b border-pastel-slate-5 hover:bg-pastel-slate-50/50 transition-colors">
                    <td className="px-6 py-4 font-semibold text-pastel-slate-800 truncate max-w-[240px]">
                      {job.original_filename}
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={job.processing_status === "Completed" ? "success" : job.processing_status === "Failed" ? "danger" : "warning"}>
                        {job.processing_status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">{getEmbedBadge(job.embedding_status)}</td>
                    <td className="px-6 py-4">{getVectorBadge(job.index_status)}</td>
                    <td className="px-6 py-4 text-right">
                      <Link to={`/indexing/${job.id}`}>
                        <Button variant="ghost" size="sm" className="text-pastel-blue-600 font-bold hover:bg-pastel-blue-50">
                          Monitor Pipeline
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

      {/* Document Index Table */}
      <div className="bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <h2 className="text-base font-bold text-pastel-slate-800">Document Index Status</h2>

          {/* Filtering and Search Controls */}
          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <div className="relative flex-1 md:flex-initial">
              <input
                type="text"
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full md:w-60 text-xs px-3.5 py-2.5 pl-9 bg-pastel-slate-50 border border-pastel-slate-100 rounded-xl focus:outline-none focus:border-pastel-blue-300 font-medium"
              />
              <svg className="w-4 h-4 text-pastel-slate-400 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-xs px-3.5 py-2.5 bg-pastel-slate-50 border border-pastel-slate-100 rounded-xl focus:outline-none font-semibold text-pastel-slate-600"
            >
              <option value="all">All Statuses</option>
              <option value="indexed">Indexed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>

        {loading && jobs.length === 0 ? (
          <div className="space-y-4">
            <Skeleton className="h-12 w-full rounded-xl" />
            <Skeleton className="h-12 w-full rounded-xl" />
            <Skeleton className="h-12 w-full rounded-xl" />
          </div>
        ) : filteredJobs.length === 0 ? (
          <EmptyState
            title="No Documents Found"
            description="You haven't indexed any knowledge documents matching the query. Start the process by uploading a document."
            icon={
              <svg className="w-10 h-10 text-pastel-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            }
            action={
              <div className="mt-4">
                <Link to="/documents">
                  <Button size="sm" className="bg-brand-primary text-white font-bold px-4 py-2.5 rounded-xl hover:bg-brand-primary/90 transition-all">
                    Upload Document
                  </Button>
                </Link>
              </div>
            }
          />
        ) : (
          <div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-pastel-slate-600">
                <thead className="text-xs uppercase bg-pastel-slate-50 text-pastel-slate-500 border-b border-pastel-slate-100">
                  <tr>
                    <th
                      className="px-6 py-3 font-semibold cursor-pointer select-none hover:text-pastel-slate-800"
                      onClick={() => handleSort("name")}
                    >
                      <div className="flex items-center gap-1">
                        Document Name
                        {sortBy === "name" && (sortOrder === "asc" ? "▲" : "▼")}
                      </div>
                    </th>
                    <th
                      className="px-6 py-3 font-semibold cursor-pointer select-none hover:text-pastel-slate-800"
                      onClick={() => handleSort("status")}
                    >
                      <div className="flex items-center gap-1">
                        Overall Status
                        {sortBy === "status" && (sortOrder === "asc" ? "▲" : "▼")}
                      </div>
                    </th>
                    <th
                      className="px-6 py-3 font-semibold cursor-pointer select-none hover:text-pastel-slate-800 text-center"
                      onClick={() => handleSort("chunks")}
                    >
                      <div className="flex items-center justify-center gap-1">
                        Chunk Count
                        {sortBy === "chunks" && (sortOrder === "asc" ? "▲" : "▼")}
                      </div>
                    </th>
                    <th className="px-6 py-3 font-semibold text-center">Embedding Status</th>
                    <th className="px-6 py-3 font-semibold text-center">Vector Status</th>
                    <th
                      className="px-6 py-3 font-semibold cursor-pointer select-none hover:text-pastel-slate-800"
                      onClick={() => handleSort("date")}
                    >
                      <div className="flex items-center gap-1">
                        Indexed At
                        {sortBy === "date" && (sortOrder === "asc" ? "▲" : "▼")}
                      </div>
                    </th>
                    <th className="px-6 py-3 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedJobs.map((job) => (
                    <tr key={job.id} className="border-b border-pastel-slate-5 hover:bg-pastel-slate-50/50 transition-colors">
                      <td className="px-6 py-4 truncate max-w-[200px]">
                        <div className="flex flex-col">
                          <span className="font-semibold text-pastel-slate-800 hover:text-brand-primary cursor-pointer truncate">
                            <Link to={`/indexing/${job.id}`}>{job.original_filename}</Link>
                          </span>
                          <span className="text-[10px] text-pastel-slate-400 font-mono mt-0.5">{job.id}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">{getStatusBadge(job)}</td>
                      <td className="px-6 py-4 text-center font-semibold text-pastel-slate-700">
                        {job.chunk_count !== null ? job.chunk_count : "-"}
                      </td>
                      <td className="px-6 py-4 text-center">{getEmbedBadge(job.embedding_status)}</td>
                      <td className="px-6 py-4 text-center">{getVectorBadge(job.index_status)}</td>
                      <td className="px-6 py-4 text-xs font-semibold text-pastel-slate-500">
                        {job.indexed_at ? new Date(job.indexed_at).toLocaleString() : "-"}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Link to={`/indexing/${job.id}`}>
                          <Button variant="ghost" size="sm" className="text-pastel-blue-600 font-bold hover:bg-pastel-blue-50 rounded-xl px-3 py-1.5 border border-transparent hover:border-pastel-blue-100">
                            Details
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination controls */}
            {totalPagesCount > 1 && (
              <div className="flex items-center justify-between mt-6 pt-4 border-t border-pastel-slate-100">
                <span className="text-xs font-semibold text-pastel-slate-400">
                  Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, filteredJobs.length)} of {filteredJobs.length} documents
                </span>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage(currentPage - 1)}
                    className="text-pastel-slate-500 disabled:text-pastel-slate-300 font-semibold border border-pastel-slate-100 rounded-xl"
                  >
                    Previous
                  </Button>
                  <span className="text-xs font-bold text-pastel-slate-700 px-2">
                    {currentPage} / {totalPagesCount}
                  </span>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={currentPage === totalPagesCount}
                    onClick={() => setCurrentPage(currentPage + 1)}
                    className="text-pastel-slate-500 disabled:text-pastel-slate-300 font-semibold border border-pastel-slate-100 rounded-xl"
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default IndexingDashboard;
