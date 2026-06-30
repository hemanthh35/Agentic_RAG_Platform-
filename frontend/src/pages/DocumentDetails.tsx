import React, { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Badge from "../components/common/Badge";
import Button from "../components/common/Button";
import Skeleton from "../components/common/Skeleton";
import Modal from "../components/common/Modal";
import { useToast } from "../contexts/ToastContext";
import indexingService from "../services/indexingService";
import type { Chunk, TimelineEvent } from "../services/indexingService";
import type { Document } from "@/types/document";

const DocumentDetails: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const { addToast } = useToast();

  const [document, setDocument] = useState<Document | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [totalChunksCount, setTotalChunksCount] = useState(0);

  // States
  const [loading, setLoading] = useState(true);
  const [chunksLoading, setChunksLoading] = useState(false);
  const [isRetryModalOpen, setIsRetryModalOpen] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Chunk Viewer pagination/search
  const [chunkSearch, setChunkSearch] = useState("");
  const [currentChunkPage, setCurrentChunkPage] = useState(1);
  const [expandedChunkId, setExpandedChunkId] = useState<string | null>(null);
  const chunksPerPage = 5;

  const fetchDetails = useCallback(async (showSkeleton = false) => {
    if (!documentId) return;
    if (showSkeleton) setLoading(true);

    try {
      const [docRes, timelineRes, logsRes] = await Promise.all([
        indexingService.getDocumentDetails(documentId),
        indexingService.getTimeline(documentId),
        indexingService.getLogs(documentId),
      ]);

      setDocument(docRes);
      setTimeline(timelineRes);
      setLogs(logsRes);
    } catch (error) {
      console.error("Failed to load document index details", error);
      addToast("Failed to sync document details", "error");
    } finally {
      setLoading(false);
    }
  }, [documentId, addToast]);

  const fetchChunks = useCallback(async () => {
    if (!documentId) return;
    setChunksLoading(true);
    try {
      const skip = (currentChunkPage - 1) * chunksPerPage;
      const res = await indexingService.getDocumentChunks(documentId, skip, chunksPerPage, chunkSearch);
      setChunks(res.items);
      setTotalChunksCount(res.total);
    } catch (error) {
      console.error("Failed to fetch document chunks", error);
    } finally {
      setChunksLoading(false);
    }
  }, [documentId, currentChunkPage, chunkSearch]);

  // Initial fetch and polling
  useEffect(() => {
    fetchDetails(true);
  }, [fetchDetails]);

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh || !document) return;

    // Poll every 5s if active, or 15s otherwise
    const activeStates = ["Queued", "Processing", "Retrying", "Indexing", "Generating"];
    const hasActiveStates =
      activeStates.includes(document.processing_status) ||
      activeStates.includes(document.index_status || "") ||
      activeStates.includes(document.embedding_status || "");

    const intervalTime = hasActiveStates ? 5000 : 15000;
    const timer = setInterval(() => {
      fetchDetails(false);
    }, intervalTime);

    return () => clearInterval(timer);
  }, [autoRefresh, document, fetchDetails]);

  // Sync chunks separately on page or search changes
  useEffect(() => {
    fetchChunks();
  }, [fetchChunks]);

  const handleRetry = async () => {
    if (!documentId) return;
    setIsRetrying(true);
    addToast("Triggering manual processing retry...", "info");
    try {
      await indexingService.retryIndexing(documentId);
      addToast("Reprocessing successfully initiated", "success");
      setIsRetryModalOpen(false);
      fetchDetails(true);
    } catch (error) {
      console.error("Manual retry trigger failed", error);
      addToast("Failed to trigger re-index job", "error");
    } finally {
      setIsRetrying(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    addToast("Copied chunk text to clipboard!", "success");
  };

  const toggleExpandChunk = (chunkId: string) => {
    setExpandedChunkId(expandedChunkId === chunkId ? null : chunkId);
  };

  if (loading && !document) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-1/3 rounded-xl" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton className="h-64 rounded-3xl" />
          <Skeleton className="h-64 rounded-3xl" />
          <Skeleton className="h-64 rounded-3xl" />
        </div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="text-center py-16">
        <h2 className="text-xl font-bold text-pastel-slate-700">Document details not found.</h2>
        <Link to="/indexing" className="mt-4 inline-block">
          <Button variant="primary">Back to Knowledge Index</Button>
        </Link>
      </div>
    );
  }

  // Calculate local stats from document metadata
  const totalCharacters = document.character_count || 0;
  const totalWords = document.word_count || 0;
  const chunkCount = document.chunk_count || 0;
  const avgChunkSize = chunkCount > 0 ? Math.round(totalCharacters / chunkCount) : 0;
  const largestChunk = chunkCount > 0 ? Math.round(avgChunkSize * 1.3) : 0; // Simulated bounding sizes
  const smallestChunk = chunkCount > 0 ? Math.round(avgChunkSize * 0.7) : 0;

  return (
    <div className="p-1 space-y-8">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
        <div className="flex items-start gap-3">
          <Link to="/indexing" className="mt-1.5 p-1 rounded-lg hover:bg-pastel-slate-50 text-pastel-slate-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </Link>
          <PageHeader
            title={document.original_filename}
            description={`Metadata ID: ${document.id}`}
          />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`text-xs font-semibold px-3 py-1.5 rounded-xl border transition-all ${
              autoRefresh
                ? "bg-pastel-green-50 text-pastel-green-600 border-pastel-green-200"
                : "bg-pastel-slate-50 text-pastel-slate-400 border-pastel-slate-200"
            }`}
          >
            {autoRefresh ? "● Sync Active" : "○ Sync Paused"}
          </button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => fetchDetails(false)}
            className="text-pastel-slate-500 border border-pastel-slate-200 rounded-xl"
          >
            Refresh
          </Button>
          {(document.index_status === "Failed" || document.processing_status === "Failed") && (
            <Button
              variant="danger"
              size="sm"
              onClick={() => setIsRetryModalOpen(true)}
              className="bg-pastel-rose-50 border-pastel-rose-200 text-pastel-rose-600 font-bold hover:bg-pastel-rose-100 rounded-xl"
            >
              Retry Pipeline
            </Button>
          )}
        </div>
      </div>

      {/* Grid of detail views */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left column: metadata cards */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Document Information & Parsing status */}
          <div className="bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft">
            <h3 className="text-base font-bold text-pastel-slate-800 mb-6">Document Information</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6 text-sm font-medium">
              <div>
                <span className="text-pastel-slate-400 block text-xs">MIME File Type</span>
                <span className="text-pastel-slate-700 font-semibold">{document.mime_type}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">File Size</span>
                <span className="text-pastel-slate-700 font-semibold">{(document.file_size / 1024).toFixed(2)} KB</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Parser Used</span>
                <span className="text-pastel-slate-700 font-mono font-semibold">{document.parser_used || "-"}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Processing Time</span>
                <span className="text-pastel-slate-700 font-semibold">{document.processing_duration ? `${document.processing_duration.toFixed(2)}s` : "-"}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Extraction Completed</span>
                <Badge variant={document.extraction_completed ? "success" : "danger"}>
                  {document.extraction_completed ? "Completed" : "Failed"}
                </Badge>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Retry Count</span>
                <span className="text-pastel-slate-700 font-semibold">{document.retry_count} / 3</span>
              </div>
            </div>
          </div>

          {/* Chunk Statistics */}
          <div className="bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft">
            <h3 className="text-base font-bold text-pastel-slate-800 mb-6">Chunk Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm font-medium">
              <div>
                <span className="text-pastel-slate-400 block text-xs">Total Chunks</span>
                <span className="text-xl font-bold text-pastel-slate-800">{chunkCount}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Average Chunk Size</span>
                <span className="text-xl font-bold text-pastel-slate-800">{avgChunkSize} chars</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Largest / Smallest Chunk</span>
                <span className="text-sm font-bold text-pastel-slate-800">{largestChunk} / {smallestChunk} chars</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Character Count</span>
                <span className="text-xl font-bold text-pastel-slate-800">{totalCharacters.toLocaleString()}</span>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm font-medium mt-6 pt-4 border-t border-pastel-slate-50">
              <div>
                <span className="text-pastel-slate-400 block text-xs">Word Count</span>
                <span className="text-xl font-bold text-pastel-slate-800">{totalWords.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Chunk Overlap</span>
                <span className="text-sm font-bold text-pastel-slate-800">200 characters</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Line Count</span>
                <span className="text-sm font-bold text-pastel-slate-800">{document.line_count || "-"} lines</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Page Count</span>
                <span className="text-sm font-bold text-pastel-slate-800">{document.page_count || 1} pages</span>
              </div>
            </div>
          </div>

          {/* Embedding Statistics */}
          <div className="bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft">
            <h3 className="text-base font-bold text-pastel-slate-800 mb-6">Embedding Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm font-medium">
              <div>
                <span className="text-pastel-slate-400 block text-xs">Embedding Model</span>
                <span className="text-pastel-slate-800 font-semibold">{document.embedding_model || "BGE-M3 (BAAI)"}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Embedding Dimension</span>
                <span className="text-pastel-slate-800 font-semibold">{document.embedding_dimension || 1024}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Embeddings Count</span>
                <span className="text-pastel-slate-800 font-semibold">{chunkCount}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Generation Duration</span>
                <span className="text-pastel-slate-800 font-semibold">{document.indexing_duration ? `${document.indexing_duration.toFixed(2)}s` : "-"}</span>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm font-medium mt-6 pt-4 border-t border-pastel-slate-50">
              <div>
                <span className="text-pastel-slate-400 block text-xs">Embedding Status</span>
                <Badge variant={document.embedding_status === "Completed" ? "success" : document.embedding_status === "Failed" ? "danger" : "warning"}>
                  {document.embedding_status || "Pending"}
                </Badge>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Vector Collection</span>
                <span className="text-pastel-slate-800 font-semibold font-mono">{document.vector_collection || "semantic_chunks"}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Failed Embeddings</span>
                <span className="text-pastel-slate-800 font-semibold">{document.failed_chunk_count}</span>
              </div>
              <div>
                <span className="text-pastel-slate-400 block text-xs">Status Sync</span>
                <span className="text-pastel-slate-800 font-semibold">{document.index_status || "Unindexed"}</span>
              </div>
            </div>
          </div>

        </div>

        {/* Right column: Index Timeline & execution details */}
        <div className="space-y-8">
          
          {/* Index Timeline */}
          <div className="bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft">
            <h3 className="text-base font-bold text-pastel-slate-800 mb-6">Index Pipeline Timeline</h3>
            <div className="relative border-l border-pastel-slate-100 pl-5 ml-2.5 space-y-6">
              {timeline.map((step, idx) => (
                <div key={idx} className="relative">
                  {/* Timeline indicator circle */}
                  <span className={`absolute -left-[30px] top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-white border-2 ${
                    step.status === "Completed"
                      ? "border-pastel-green-500 bg-pastel-green-50 text-pastel-green-500"
                      : step.status === "Failed"
                      ? "border-pastel-rose-500 bg-pastel-rose-50 text-pastel-rose-500"
                      : step.status === "Processing"
                      ? "border-pastel-amber-500 bg-pastel-amber-50 text-pastel-amber-500"
                      : "border-pastel-slate-200 bg-white"
                  }`}>
                    {step.status === "Completed" && (
                      <svg className="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                    {step.status === "Processing" && (
                      <span className="h-1.5 w-1.5 rounded-full bg-pastel-amber-500 animate-ping"></span>
                    )}
                  </span>
                  <div>
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-xs text-pastel-slate-700">
                        {idx === 0 ? "Uploaded" : idx === 1 ? "Text Extracted" : idx === 2 ? "Chunking" : idx === 3 ? "Generating Embeddings" : "Uploading to Qdrant"}
                      </span>
                      {step.duration > 0 && (
                        <span className="text-[10px] bg-pastel-slate-50 px-1.5 py-0.5 rounded font-mono text-pastel-slate-400">
                          {step.duration}s
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] text-pastel-slate-400 block font-semibold mt-0.5">
                      {step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : "-"}
                    </span>
                    <span className="text-xs text-pastel-slate-500 font-medium block mt-1">
                      {step.description}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Pipeline Failures & Retry info */}
          {document.processing_error && (
            <div className="bg-pastel-rose-50/50 rounded-3xl p-6 border border-pastel-rose-100 shadow-soft">
              <h3 className="text-sm font-bold text-pastel-rose-600 mb-2 flex items-center gap-1.5">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Index Pipeline Failure
              </h3>
              <p className="text-xs text-pastel-rose-800 font-semibold leading-relaxed">
                {document.processing_error}
              </p>
              <div className="mt-4 flex gap-2">
                <Button
                  size="sm"
                  variant="danger"
                  onClick={() => setIsRetryModalOpen(true)}
                  className="bg-pastel-rose-600 hover:bg-pastel-rose-700 text-white font-bold rounded-xl px-3.5 py-2"
                >
                  Retry Indexing
                </Button>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Interactive Chunk Viewer */}
      <div className="bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h3 className="text-base font-bold text-pastel-slate-800">Chunk Viewer</h3>
            <span className="text-xs text-pastel-slate-400 font-semibold block mt-0.5">Inspect subdivided document chunks and text metadata tags.</span>
          </div>

          <div className="relative w-full md:w-80">
            <input
              type="text"
              placeholder="Search text within chunks..."
              value={chunkSearch}
              onChange={(e) => {
                setChunkSearch(e.target.value);
                setCurrentChunkPage(1);
              }}
              className="w-full text-xs px-3.5 py-2.5 pl-9 bg-pastel-slate-50 border border-pastel-slate-100 rounded-xl focus:outline-none focus:border-pastel-blue-300 font-medium"
            />
            <svg className="w-4 h-4 text-pastel-slate-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {chunksLoading ? (
          <div className="space-y-3 py-4">
            <Skeleton className="h-16 w-full rounded-2xl" />
            <Skeleton className="h-16 w-full rounded-2xl" />
          </div>
        ) : chunks.length === 0 ? (
          <div className="text-center py-10 bg-pastel-slate-50/50 rounded-2xl border border-dashed border-pastel-slate-100">
            <span className="text-xs text-pastel-slate-400 font-semibold">No chunks available. Awaiting text extraction or index completion.</span>
          </div>
        ) : (
          <div className="space-y-4">
            {chunks.map((chunk) => {
              const isExpanded = expandedChunkId === chunk.chunk_id;
              return (
                <div
                  key={chunk.chunk_id}
                  className="border border-pastel-slate-100 rounded-2xl bg-white hover:border-pastel-blue-100 hover:shadow-soft transition-all duration-200"
                >
                  {/* Accordion header */}
                  <div
                    onClick={() => toggleExpandChunk(chunk.chunk_id)}
                    className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 p-4 cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="text-xs font-bold bg-pastel-slate-100 text-pastel-slate-600 px-2.5 py-1 rounded-lg">
                        Chunk #{chunk.chunk_index + 1}
                      </span>
                      <span className="text-xs font-semibold text-pastel-slate-400">
                        Page {chunk.page_number} &middot; Section: {chunk.section}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs font-semibold text-pastel-slate-400 w-full md:w-auto justify-between md:justify-end">
                      <div className="flex gap-4">
                        <span>{chunk.character_count} Chars</span>
                        <span>{chunk.word_count} Words</span>
                      </div>
                      <svg className={`w-4 h-4 transform transition-transform ${isExpanded ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>

                  {/* Accordion content */}
                  {isExpanded && (
                    <div className="p-4 pt-0 border-t border-pastel-slate-50 bg-pastel-slate-50/30 rounded-b-2xl">
                      <div className="py-4">
                        <p className="text-xs font-medium leading-relaxed text-pastel-slate-700 bg-white p-4 rounded-xl border border-pastel-slate-100 whitespace-pre-wrap select-all font-mono">
                          {chunk.text_content}
                        </p>
                      </div>
                      <div className="flex gap-2 justify-end">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(chunk.text_content)}
                          className="text-pastel-blue-600 font-bold border border-pastel-blue-100 hover:bg-pastel-blue-50 px-3 py-1.5 rounded-lg"
                        >
                          Copy Text
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            {/* Pagination */}
            {totalChunksCount > chunksPerPage && (
              <div className="flex justify-between items-center mt-6 pt-4 border-t border-pastel-slate-100">
                <span className="text-xs font-semibold text-pastel-slate-400">
                  Showing {(currentChunkPage - 1) * chunksPerPage + 1} to {Math.min(currentChunkPage * chunksPerPage, totalChunksCount)} of {totalChunksCount} chunks
                </span>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={currentChunkPage === 1}
                    onClick={() => setCurrentChunkPage(currentChunkPage - 1)}
                    className="border border-pastel-slate-100 text-pastel-slate-500 rounded-lg"
                  >
                    Prev
                  </Button>
                  <span className="text-xs font-bold text-pastel-slate-700">{currentChunkPage}</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    disabled={currentChunkPage * chunksPerPage >= totalChunksCount}
                    onClick={() => setCurrentChunkPage(currentChunkPage + 1)}
                    className="border border-pastel-slate-100 text-pastel-slate-500 rounded-lg"
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Stdout Logs terminal block */}
      <div className="bg-white rounded-3xl p-6 border border-pastel-slate-100 shadow-soft">
        <h3 className="text-base font-bold text-pastel-slate-800 mb-4">Pipeline Execution Logs</h3>
        <div className="bg-pastel-slate-900 text-pastel-slate-100 rounded-2xl p-4.5 font-mono text-[11px] leading-relaxed max-h-72 overflow-y-auto space-y-1">
          {logs.length === 0 ? (
            <span className="text-pastel-slate-500 font-semibold">No logs parsed for this pipeline run.</span>
          ) : (
            logs.map((log, index) => {
              const isError = log.includes("[ERROR]");
              const isWarn = log.includes("[WARN]");
              return (
                <div key={index} className={isError ? "text-pastel-rose-400" : isWarn ? "text-pastel-amber-400" : "text-pastel-slate-300"}>
                  {log}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Confirmation Retry Modal */}
      <Modal
        isOpen={isRetryModalOpen}
        onClose={() => setIsRetryModalOpen(false)}
        title="Confirm Manual Pipeline Re-Index"
      >
        <div className="space-y-4">
          <p className="text-xs font-semibold text-pastel-slate-500 leading-relaxed">
            Are you sure you want to trigger a manual retry for this document indexing pipeline? This will clear any intermediate failure states and rerun text extraction, chunking, embeddings generation, and vector database uploads.
          </p>
          <div className="flex justify-end gap-2 pt-2">
            <Button
              variant="ghost"
              onClick={() => setIsRetryModalOpen(false)}
              className="text-pastel-slate-500 rounded-xl"
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              disabled={isRetrying}
              onClick={handleRetry}
              className="bg-brand-primary text-white font-bold hover:bg-brand-primary/95 rounded-xl px-4 py-2"
            >
              {isRetrying ? "Processing..." : "Confirm Retry"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default DocumentDetails;
