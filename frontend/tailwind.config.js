/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Poppins", "sans-serif"],
      },
      colors: {
        pastel: {
          blue: {
            50: "#f0f7ff",
            100: "#e0effe",
            200: "#bae0fd",
            300: "#93c5fd",
            500: "#3b82f6",
          },
          purple: {
            50: "#fdf8ff",
            100: "#f3e8ff",
            200: "#e9d5ff",
            300: "#d8b4fe",
            500: "#a855f7",
          },
          green: {
            50: "#f0fdf4",
            100: "#dcfce7",
            200: "#bbf7d0",
            300: "#86efac",
            500: "#22c55e",
          },
          rose: {
            50: "#fff1f2",
            100: "#ffe4e6",
            200: "#fecdd3",
            300: "#fca5a5",
            500: "#ef4444",
          },
          amber: {
            50: "#fffbeb",
            100: "#fef3c7",
            200: "#fde68a",
            300: "#fcd34d",
            500: "#f59e0b",
          },
          slate: {
            50: "#f8fafc",
            100: "#f1f5f9",
            200: "#e2e8f0",
            300: "#cbd5e1",
            400: "#94a3b8",
            500: "#64748b",
            600: "#475569",
            700: "#334155",
            800: "#1e293b",
            900: "#0f172a",
          }
        },
        brand: {
          bg: "#f8fafc",
          card: "#ffffff",
          primary: "#6366f1",
          secondary: "#a855f7",
          text: {
            primary: "#0f172a",
            secondary: "#475569",
            muted: "#94a3b8",
          }
        }
      },
      boxShadow: {
        soft: "0 4px 20px -2px rgba(148, 163, 184, 0.08), 0 2px 8px -1px rgba(148, 163, 184, 0.04)",
        card: "0 10px 30px -10px rgba(148, 163, 184, 0.12)",
      }
    },
  },
  plugins: [],
}
