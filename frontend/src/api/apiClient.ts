import axios from "axios";

// Read API base URL from Vite environment variables, fallback to local standard port
const API_BASE_URL =
  (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000, // 5 seconds request timeout limit
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Ideal for appending future JWT tokens
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("auth_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Standardized error parsing
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle specific codes (like 401 Unauthorized or network exceptions)
    const errorDetails = {
      message: error.message || "Network connection failure",
      status: error.response?.status || null,
      data: error.response?.data || null,
    };

    console.error("API client interceptor catch:", errorDetails);
    return Promise.reject(errorDetails);
  }
);

export default apiClient;
