export interface ProcessingTimelineEvent {
  status: 'pending' | 'queued' | 'processing' | 'retrying' | 'completed' | 'failed';
  title: string;
  description: string;
  timestamp: string;
  duration?: number;
}

export interface ProcessingLog {
  timestamp: string;
  level: 'info' | 'warn' | 'error';
  message: string;
}
