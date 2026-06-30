import React, { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import Badge from "../components/common/Badge";
import Button from "../common/Button";
import Skeleton from "../common/Skeleton";
import processingService from "@/services/processingService";
import type { Document } from "@/types/document";
import type { ProcessingTimelineEvent, ProcessingLog } from "@/types/processing";

const ProcessingDetails: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const [doc, setDoc] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [retrying, setRetrying] = useState(false);
  const [logsExpanded, setLogsExpanded] = useState(true);

  const fetchDetails = useCallback(async () => {
    if (!documentId) return;
    try {
      const res = await processingService.getJobDetails(documentId);
      setDoc(res);
    } catch (error) {
      console.error("Failed to fetch processing details", error);
    } finally {
      setLoading(false);
    }
  }, [documentId]);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

  // Dynamic status-polling if document is processing or queued
  useEffect(() => {
    if (!doc) return;
    const activeStates = ["Uploaded", "Queued", "Processing", "Retrying"];
    if (!activeStates.includes(doc.processing_status)) return;

    const timer = setInterval(() => {
      fetchDetails();
    }, 3000);

    return () => clearInterval(timer);
  }, [doc, fetchDetails]);

  const handleRetry = async () => {
    if (!documentId) return;
    setRetrying(true);
    try {
      await processingService.retryJob(documentId);
      await fetchDetails();
    } catch (error) {
      console.error("Failed to retry job", error);
      alert("Failed to trigger pipeline retry.");
    } finally {
      setRetrying(false);
    }
  };

  if (loading) {
    return (
      <div className="p-4 space-y-6">
        <Skeleton className="h-10 w-1/3 rounded-xl" />
        <Skeleton className="h-32 w-full rounded-2xl" />
        <Skeleton className="h-60 w-full rounded-2xl" />
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="p-1 text-center py-20 bg-white border border-pastel-slate-100 rounded-3xl max-w-lg mx-auto">
        <h2 className="text-xl font-bold text-pastel-slate-800 mb-2">Job Not Found</h2>
        <p className="text-pastel-slate-500 mb-6 text-sm">The document processing job does not exist.</p>
        <Link to="/processing">
          <Button variant="primary">Return to Processing</Button>
        </Link>
      </div>
    );
  }

  // Synthesize logs
  const logs: ProcessingLog[] = [];
  const addLog = (timestamp: string | null, level: 'info' | 'warn' | 'error', message: string) => {
    if (timestamp) {
      logs.push({
        timestamp: new Date(timestamp).toLocaleTimeString(),
        level,
        message
      });
    }
  };

  addLog(doc.created_at, 'info', `File uploaded: ${doc.original_filename} (${(doc.file_size / 1024).toFixed(1)} KB)`);
  addLog(doc.created_at, 'info', `Background processing job enqueued in task queue. Status set to Queued.`);
  addLog(doc.processing_started_at, 'info', `Background worker dequeued task. Pipeline active.`);
  
  if (doc.processing_status === 'Processing') {
    addLog(doc.processing_started_at, 'info', `Step 1/4: Downloading storage file from private bucket.`);
    addLog(doc.processing_started_at, 'info', `Step 2/4: Parser Factory checking document file type.`);
  }

  if (doc.parser_used) {
    addLog(doc.processing_started_at, 'info', `Step 3/4: Selected Parser [${doc.parser_used}]. Executing extraction...`);
  }

  if (doc.processing_completed_at && doc.processing_status === 'Completed') {
    addLog(doc.processing_completed_at, 'info', `Step 4/4: Text cleaner executed successfully. Normalized whitespace and line bounds.`);
    addLog(doc.processing_completed_at, 'info', `Persisted extracted text model and relationship in PostgreSQL (version ${doc.extracted_text_version}).`);
    addLog(doc.processing_completed_at, 'info', `Metadata synchronized. Extracted: ${doc.page_count} pages, ${doc.word_count} words (${doc.character_count} chars, ${doc.line_count} lines).`);
    addLog(doc.processing_completed_at, 'info', `Pipeline finished successfully in ${doc.processing_duration?.toFixed(2)} seconds. Status set to Completed.`);
  }

  if (doc.processing_completed_at && doc.processing_status === 'Failed') {
    addLog(doc.processing_completed_at, 'error', `Pipeline execution encountered a fatal crash.`);
    addLog(doc.processing_completed_at, 'error', `ERROR DETAILS: ${doc.processing_error}`);
    if (doc.retry_count > 0) {
      addLog(doc.processing_completed_at, 'warn', `Pipeline retry attempted ${doc.retry_count} times. Status set to Failed.`);
    } else {
      addLog(doc.processing_completed_at, 'error', `Status set to Failed.`);
    }
  }

  // Synthesize Timeline Events
  const events: ProcessingTimelineEvent[] = [];
  if (doc.created_at) {
    events.push({
      status: 'pending',
      title: 'Document Uploaded',
      description: `Uploaded file to Supabase Storage. Path: ${doc.storage_path}`,
      timestamp: new Date(doc.created_at).toLocaleTimeString()
    });
  }
  if (doc.created_at) {
    events.push({
      status: 'queued',
      title: 'Enqueued in Worker',
      description: 'Scheduled for background processing pipeline.',
      timestamp: new Date(doc.created_at).toLocaleTimeString()
    });
  }
  if (doc.processing_started_at) {
    events.push({
      status: 'processing',
      title: 'Processing Active',
      description: doc.parser_used ? `Parser selected: ${doc.parser_used}` : 'Downloading document and selecting parser...',
      timestamp: new Date(doc.processing_started_at).toLocaleTimeString()
    });
  }
  if (doc.processing_completed_at && doc.processing_status === 'Completed') {
    events.push({
      status: 'completed',
      title: 'Processing Completed',
      description: `Extracted ${doc.word_count} words and ${doc.line_count} lines in ${doc.processing_duration?.toFixed(2)}s.`,
      timestamp: new Date(doc.processing_completed_at).toLocaleTimeString(),
      duration: doc.processing_duration || undefined
    });
  }
  if (doc.processing_completed_at && doc.processing_status === 'Failed') {
    events.push({
      status: 'failed',
      title: 'Pipeline Failed',
      description: doc.processing_error || 'Unexpected exception occurred.',
      timestamp: new Date(doc.processing_completed_at).toLocaleTimeString()
    });
  }

  return (
    <div className="p-1">
      {/* Back button & title */}
      <div className="mb-6">
        <Link to="/processing" className="text-xs font-semibold text-pastel-blue-600 hover:underline flex items-center gap-1 mb-2">
          ← Back to Processing Dashboard
        </Link>
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
          <PageHeader
            title={doc.original_filename}
            description={`Job details for ID: ${doc.id}`}
          />
          <div className="flex gap-2">
            {doc.processing_status === "Failed" && (
              <Button
                variant="primary"
                onClick={handleRetry}
                isLoading={retrying}
              >
                Retry Processing
              </Button>
            )}
            <Badge variant={
              doc.processing_status === "Completed" ? "success" :
              doc.processing_status === "Failed" ? "error" : "warning"
            }>
              {doc.processing_status.toUpperCase()}
            </Badge>
          </div>
        </div>
      </div>

      {/* Info grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-3xl border border-pastel-slate-100 shadow-soft md:col-span-2">
          <h3 className="text-base font-semibold text-pastel-slate-800 mb-4">Metadata Summary</h3>
          <div className="grid grid-cols-2 gap-y-4 gap-x-6 text-sm">
            <div>
              <span className="text-xs font-medium text-pastel-slate-400 block">Original Filename</span>
              <span className="font-medium text-pastel-slate-700">{doc.original_filename}</span>
            </div>
            <div>
              <span className="text-xs font-medium text-pastel-slate-400 block">Mime Type</span>
              <span className="font-mono text-pastel-slate-600 text-xs">{doc.mime_type}</span>
            </div>
            <div>
              <span className="text-xs font-medium text-pastel-slate-400 block">File Size</span>
              <span className="font-medium text-pastel-slate-700">{(doc.file_size / 1024).toFixed(1)} KB</span>
            </div>
            <div>
              <span className="text-xs font-medium text-pastel-slate-400 block">Parser Used</span>
              <span className="font-medium text-pastel-slate-700 font-mono text-xs">{doc.parser_used || "-"}</span>
            </div>
            <div>
              <span className="text-xs font-medium text-pastel-slate-400 block">Supabase Storage Path</span>
              <span className="text-xs text-pastel-slate-500 font-mono break-all">{doc.storage_path}</span>
            </div>
            <div>
              <span className="text-xs font-medium text-pastel-slate-400 block">Extracted Version</span>
              <span className="font-medium text-pastel-slate-700">{doc.extracted_text_version}</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-pastel-slate-100 shadow-soft">
          <h3 className="text-base font-semibold text-pastel-slate-800 mb-4">Extraction Stats</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center text-sm border-b border-pastel-slate-50 pb-2">
              <span className="text-pastel-slate-500">Page Count</span>
              <span className="font-semibold text-pastel-slate-800">{doc.page_count !== null ? doc.page_count : "-"}</span>
            </div>
            <div className="flex justify-between items-center text-sm border-b border-pastel-slate-50 pb-2">
              <span className="text-pastel-slate-500">Word Count</span>
              <span className="font-semibold text-pastel-slate-800">{doc.word_count !== null ? doc.word_count : "-"}</span>
            </div>
            <div className="flex justify-between items-center text-sm border-b border-pastel-slate-50 pb-2">
              <span className="text-pastel-slate-500">Character Count</span>
              <span className="font-semibold text-pastel-slate-800">{doc.character_count !== null ? doc.character_count : "-"}</span>
            </div>
            <div className="flex justify-between items-center text-sm border-b border-pastel-slate-50 pb-2">
              <span className="text-pastel-slate-500">Line Count</span>
              <span className="font-semibold text-pastel-slate-800">{doc.line_count !== null ? doc.line_count : "-"}</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-pastel-slate-500">Processing Duration</span>
              <span className="font-semibold text-pastel-slate-800">
                {doc.processing_duration ? `${doc.processing_duration.toFixed(2)}s` : "-"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline view */}
      <div className="bg-white rounded-3xl p-6 lg:p-8 border border-pastel-slate-100 shadow-soft mb-8">
        <h3 className="text-lg font-semibold text-pastel-slate-800 mb-6">Processing Timeline</h3>
        <div className="relative border-l border-pastel-slate-100 ml-4 pl-6 space-y-6">
          {events.map((event, idx) => (
            <div key={idx} className="relative">
              {/* Dot */}
              <span className={`absolute -left-10 top-1.5 w-7 h-7 rounded-full flex items-center justify-center text-white ${
                event.status === 'completed' ? 'bg-pastel-green-500' :
                event.status === 'failed' ? 'bg-brand-error' :
                event.status === 'processing' ? 'bg-pastel-amber-500 animate-pulse' : 'bg-pastel-slate-400'
              }`}>
                {event.status === 'completed' ? '✓' :
                 event.status === 'failed' ? '✗' : '●'}
              </span>
              <div className="flex justify-between items-start gap-4">
                <div>
                  <h4 className="font-semibold text-pastel-slate-800 text-sm">{event.title}</h4>
                  <p className="text-pastel-slate-500 text-xs mt-1">{event.description}</p>
                </div>
                <span className="text-xs text-pastel-slate-400 font-medium">
                  {event.timestamp}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Terminal logs view */}
      <div className="bg-[#1E1E1E] text-[#D4D4D4] rounded-3xl overflow-hidden shadow-soft border border-pastel-slate-800">
        <div 
          onClick={() => setLogsExpanded(!logsExpanded)}
          className="bg-[#2D2D2D] px-6 py-4 flex justify-between items-center cursor-pointer select-none"
        >
          <span className="font-mono text-xs font-semibold tracking-wider uppercase text-pastel-slate-400">
            Pipeline Execution Console Logs
          </span>
          <span className="text-xs text-pastel-slate-400">
            {logsExpanded ? "▼ Hide Logs" : "▲ Show Logs"}
          </span>
        </div>
        {logsExpanded && (
          <div className="p-6 font-mono text-xs space-y-2 overflow-x-auto max-h-96">
            {logs.map((log, idx) => (
              <div key={idx} className="flex gap-4">
                <span className="text-[#858585] select-none">[{log.timestamp}]</span>
                <span className={
                  log.level === 'error' ? 'text-[#F44747]' : 
                  log.level === 'warn' ? 'text-[#CCA700]' : 'text-[#4FC1FF]'
                }>
                  {log.level.toUpperCase()}
                </span>
                <span className="text-[#E5E5E5]">{log.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessingDetails;
