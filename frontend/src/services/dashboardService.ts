import apiClient from "@/api/apiClient";
import type { HealthResponse } from "@/types/health";

export const dashboardService = {
  /** Fetch backend operational metrics from endpoints.
   *
   * @returns HealthResponse details.
   */
  async getHealthStatus(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>("/api/v1/health");
    return response.data;
  },
};

export default dashboardService;
