import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import axios from "axios";

const WorkspaceContext = createContext(null);

export const useWorkspace = () => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return context;
};

// Set backend base URL globally
axios.defaults.baseURL = "http://127.0.0.1:8000";

export const WorkspaceProvider = ({ children }) => {
  // Pre-seed workspace ID as requested for standard testing
  const [workspaceId, setWorkspaceId] = useState("5be79f52-0d47-429f-a554-26c705fc4e7a");
  const [workspaceName, setWorkspaceName] = useState("Audit Test Company");
  const [workspaceStatus, setWorkspaceStatus] = useState("READY");
  const [loading, setLoading] = useState(false);
  const pollIntervalRef = useRef(null);

  const fetchWorkspaceDetails = async (id) => {
    if (!id) return;
    setLoading(true);
    try {
      const res = await axios.get(`/api/workspaces/${id}`);
      if (res.data && res.data.workspace) {
        setWorkspaceName(res.data.workspace.name || "Workspace");
        setWorkspaceStatus(res.data.workspace.status || "READY");
      }
    } catch (err) {
      console.warn("Could not retrieve workspace metadata. Using fallbacks.", err);
      // Keep pre-seed fallback values on error
    } finally {
      setLoading(false);
    }
  };

  // Poll workspace status if it's currently processing
  useEffect(() => {
    if (workspaceStatus === "PROCESSING") {
      if (!pollIntervalRef.current) {
        console.log("Start polling status for workspace:", workspaceId);
        pollIntervalRef.current = setInterval(async () => {
          try {
            const res = await axios.get(`/api/workspaces/${workspaceId}`);
            if (res.data && res.data.workspace) {
              const currentStatus = res.data.workspace.status;
              setWorkspaceStatus(currentStatus);
              if (currentStatus !== "PROCESSING") {
                clearInterval(pollIntervalRef.current);
                pollIntervalRef.current = null;
                console.log("Stopped polling. Status reached:", currentStatus);
              }
            }
          } catch (err) {
            console.error("Error polling workspace status:", err);
          }
        }, 2000);
      }
    } else {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [workspaceStatus, workspaceId]);

  // Initial fetch on mount or workspace ID change
  useEffect(() => {
    fetchWorkspaceDetails(workspaceId);
  }, [workspaceId]);

  const selectWorkspace = (id) => {
    setWorkspaceId(id);
  };

  const triggerRefresh = () => {
    fetchWorkspaceDetails(workspaceId);
  };

  return (
    <WorkspaceContext.Provider
      value={{
        workspaceId,
        workspaceName,
        workspaceStatus,
        loading,
        selectWorkspace,
        triggerRefresh,
        setWorkspaceStatus
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
};
