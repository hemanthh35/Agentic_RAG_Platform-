import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layouts/AppLayout";
import Agent from "./pages/Agent";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import Evaluation from "./pages/Evaluation";
import Memory from "./pages/Memory";
import NotFound from "./pages/NotFound";
import Observability from "./pages/Observability";
import Retrieval from "./pages/Retrieval";
import Settings from "./pages/Settings";

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Main application layout containing sidebars and headers */}
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="documents" element={<Documents />} />
          <Route path="retrieval" element={<Retrieval />} />
          <Route path="agent" element={<Agent />} />
          <Route path="memory" element={<Memory />} />
          <Route path="evaluation" element={<Evaluation />} />
          <Route path="observability" element={<Observability />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Catch-all 404 handler redirect */}
        <Route path="/404" element={<NotFound />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
