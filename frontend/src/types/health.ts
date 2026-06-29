export interface ServiceStatus {
  database: "connected" | "disconnected";
  supabase: "connected" | "disconnected";
}

export interface HealthStatusData {
  status: "healthy" | "degraded" | "unhealthy";
  version: string;
  environment: string;
  uptime_seconds: number;
  timestamp: string;
  response_time_ms: number;
  services: ServiceStatus;
}

export interface HealthResponse {
  success: boolean;
  data: HealthStatusData;
}
export type BackendStatusType = "connected" | "disconnected" | "loading";
