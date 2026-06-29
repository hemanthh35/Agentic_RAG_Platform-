import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import dashboardService from "@/services/dashboardService";
import type { BackendStatusType, HealthStatusData } from "@/types/health";

interface HealthContextProps {
  backendStatus: BackendStatusType;
  healthData: HealthStatusData | null;
  loading: boolean;
  error: string | null;
  refreshHealth: () => Promise<void>;
}

const HealthContext = createContext<HealthContextProps | undefined>(undefined);

export const HealthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [backendStatus, setBackendStatus] = useState<BackendStatusType>("loading");
  const [healthData, setHealthData] = useState<HealthStatusData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refreshHealth = useCallback(async () => {
    try {
      const response = await dashboardService.getHealthStatus();
      if (response.success && response.data) {
        setHealthData(response.data);
        setBackendStatus("connected");
        setError(null);
      } else {
        setBackendStatus("disconnected");
        setHealthData(null);
        setError("Invalid response format received from system health API.");
      }
    } catch (err: any) {
      setBackendStatus("disconnected");
      setHealthData(null);
      setError(
        err?.message || "Failed to establish connection with the API backend."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshHealth();

    // Poll the backend status every 10 seconds to detect status changes dynamically
    const interval = setInterval(() => {
      refreshHealth();
    }, 10000);

    return () => clearInterval(interval);
  }, [refreshHealth]);

  return (
    <HealthContext.Provider
      value={{ backendStatus, healthData, loading, error, refreshHealth }}
    >
      {children}
    </HealthContext.Provider>
  );
};

export const useHealth = () => {
  const context = useContext(HealthContext);
  if (context === undefined) {
    throw new Error("useHealth must be used within a HealthProvider");
  }
  return context;
};
