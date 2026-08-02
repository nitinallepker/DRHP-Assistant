import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { WorkspaceProvider } from "./context/WorkspaceContext";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import WorkspacePage from "./pages/WorkspacePage";
import KnowledgeRepository from "./pages/KnowledgeRepository";
import DRHPPage from "./pages/DRHPPage";
import ReviewPage from "./pages/ReviewPage";
import ImprovementPage from "./pages/ImprovementPage";
import TransformationPage from "./pages/TransformationPage";
import ExportPage from "./pages/ExportPage";
import WorkspaceChat from "./pages/WorkspaceChat";

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);

  return (
    <WorkspaceProvider>
      <Router>
        <div className="flex bg-darkBg min-h-screen text-gray-100">
          {/* Fixed left sidebar navigation */}
          <Sidebar onCollapse={setSidebarCollapsed} />

          {/* Main viewport panels */}
          <main className={`flex-1 p-8 overflow-y-auto transition-all duration-300 ${
            sidebarCollapsed ? "ml-20" : "ml-64"
          }`}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/workspace" element={<WorkspacePage />} />
              <Route path="/repository" element={<KnowledgeRepository />} />
              <Route path="/drhp" element={<DRHPPage />} />
              <Route path="/review" element={<ReviewPage />} />
              <Route path="/improvement" element={<ImprovementPage />} />
              <Route path="/transformation" element={<TransformationPage />} />
              <Route path="/export" element={<ExportPage />} />
              <Route path="/chat" element={<WorkspaceChat />} />
            </Routes>
          </main>
        </div>
      </Router>
    </WorkspaceProvider>
  );
}

export default App;
