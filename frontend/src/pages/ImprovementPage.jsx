import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { useWorkspace } from "../context/WorkspaceContext";
import { 
  Check, 
  X, 
  Eye, 
  AlertCircle, 
  Sparkles, 
  HelpCircle, 
  ChevronRight,
  Info
} from "lucide-react";

export const ImprovementPage = () => {
  const { workspaceId, workspaceStatus, setWorkspaceStatus } = useWorkspace();
  const [suggestions, setSuggestions] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  const fetchRevisionsData = async () => {
    if (!workspaceId) return;
    setLoading(true);
    try {
      // 1. Fetch suggestions
      const sugsRes = await axios.get(`/api/reviews/${workspaceId}/suggestions`);
      setSuggestions(sugsRes.data.suggestions || []);
      
      // 2. Fetch conflicts
      const conflictsRes = await axios.get(`/api/improvements/${workspaceId}/conflicts`);
      setConflicts(conflictsRes.data.conflicts || []);
    } catch (err) {
      console.warn("Could not query improvement database. Using fallbacks.", err);
      // Offline fallback seeds
      setSuggestions([
        { suggestion_id: "SUG-001", section_slug: "LEGAL_LITIGATION_DECLARATION", section_version: 1, reviewer: "LEGAL", severity: "MEDIUM", confidence: 0.9, reason: "Outstanding litigation requires a petition reference number.", evidence: "Fact category: LITIGATION, source: litigation_audit.pdf", recommendation: "Append: 'Municipal corporation petition status is pending under reference suit no. 204/2025.'", status: "OPEN" },
        { suggestion_id: "SUG-002", section_slug: "FINANCIAL_HIGHLIGHTS_MDA", section_version: 1, reviewer: "FINANCE", severity: "HIGH", confidence: 0.98, reason: "FY25 revenue totals must match corporate audited balance sheets.", evidence: "Fact category: FINANCIAL_STATEMENTS, source: financial_highlights.json", recommendation: "Ensure revenue reads INR 1,250 Crores in subsequent statements.", status: "OPEN" },
        { suggestion_id: "SUG-003", section_slug: "RISK_FACTORS", section_version: 1, reviewer: "RISK", severity: "MEDIUM", confidence: 0.92, reason: "The server downtime risk lacks mitigation details.", evidence: "Fact category: RISK_REGISTRY, source: risk_registry.json", recommendation: "Add clause: We mitigate downtime via multi-region cloud backup strategies.", status: "ACCEPTED" }
      ]);
      setConflicts([
        {
          conflict_id: "CF-001",
          section_slug: "LEGAL_LITIGATION_DECLARATION",
          keyword: "NOIDA",
          description: "Potential drafting conflict detected on keyword 'NOIDA' between LEGAL and CONSISTENCY reviewers."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRevisionsData();
  }, [workspaceId, workspaceStatus]);

  const handleUpdateStatus = async (id, status) => {
    setUpdating(true);
    try {
      await axios.post(`/api/reviews/suggestions/${id}/status`, { status });
      // Update local state state to reflect change instantly
      setSuggestions(prev => 
        prev.map(sug => sug.suggestion_id === id ? { ...sug, status } : sug)
      );
    } catch (err) {
      console.error("Updating suggestion status failed:", err);
    } finally {
      setUpdating(false);
    }
  };

  const handleApplyImprovements = async () => {
    setLoading(true);
    try {
      setWorkspaceStatus("PROCESSING");
      await axios.post(`/api/improvements/${workspaceId}/apply`);
      setWorkspaceStatus("READY");
      fetchRevisionsData();
    } catch (err) {
      console.error("Applying improvements failed:", err);
      setWorkspaceStatus("READY");
    } finally {
      setLoading(false);
    }
  };

  // Group suggestions by section
  const groupedSuggestions = {};
  suggestions.forEach(s => {
    if (!groupedSuggestions[s.section_slug]) {
      groupedSuggestions[s.section_slug] = [];
    }
    groupedSuggestions[s.section_slug].push(s);
  });

  return (
    <div className="space-y-8">
      {/* Header Panel */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Content Improvement</h1>
          <p className="text-gray-400 mt-1">Accept or reject reviewer suggestions to rewrite draft sections automatically.</p>
        </div>
      </div>

      {/* Reviewer Conflicts Box */}
      {conflicts.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-5 shadow-lg space-y-3">
          <div className="flex items-center space-x-2 text-red-500 font-bold text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>Reviewer Conflict Warning</span>
          </div>
          <div className="space-y-2">
            {conflicts.map((c, idx) => (
              <div key={idx} className="flex justify-between items-center text-xs text-red-400 bg-red-950/20 border border-red-900/40 p-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Info className="w-4 h-4 text-red-500" />
                  <span>{c.description}</span>
                </div>
                <span className="font-bold bg-red-950 border border-red-800 text-red-500 px-2.5 py-0.5 rounded text-[10px]">
                  Keyword: {c.keyword}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Revisions grouped by sections list */}
      <div className="space-y-6">
        {Object.entries(groupedSuggestions).map(([slug, sugsList], idx) => (
          <div key={idx} className="bg-darkCard border border-gray-805 rounded-xl shadow-xl overflow-hidden">
            {/* Group Header */}
            <div className="px-6 py-4 border-b border-gray-800 bg-darkBg/30 flex justify-between items-center">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                Section: {slug.replace("_", " ")}
              </h2>
              <span className="text-xs bg-gray-800 border border-gray-750 px-2 py-0.5 rounded text-gray-400 font-semibold">
                {sugsList.length} suggestions
              </span>
            </div>

            {/* Suggestions list */}
            <div className="divide-y divide-gray-800">
              {sugsList.map((sug, sIdx) => (
                <div key={sIdx} className="p-6 flex flex-col md:flex-row gap-6 justify-between items-start hover:bg-gray-800/10 transition-colors">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] bg-gray-800/60 border border-gray-750 px-2 py-0.5 rounded text-gray-400 font-bold uppercase tracking-wider">
                        {sug.reviewer}
                      </span>
                      <span className="text-xs text-gray-500">v{sug.section_version}</span>
                    </div>
                    
                    <h3 className="text-sm font-semibold text-white">{sug.reason}</h3>
                    <p className="text-xs text-gray-400 bg-darkBg/30 p-2.5 border border-gray-850 rounded italic">
                      "{sug.recommendation}"
                    </p>
                  </div>

                  {/* Actions buttons */}
                  <div className="flex items-center space-x-2 self-center flex-shrink-0">
                    <button
                      onClick={() => setSelectedEvidence(sug.evidence)}
                      className="p-2 bg-gray-800 hover:bg-gray-750 text-gray-400 hover:text-white rounded-lg border border-gray-700 transition-colors"
                      title="View Evidence Source"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    
                    <button
                      onClick={() => handleUpdateStatus(sug.suggestion_id, "ACCEPTED")}
                      className={`p-2 rounded-lg border transition-colors flex items-center space-x-1.5 text-xs font-semibold ${
                        sug.status === "ACCEPTED"
                          ? "bg-green-500 border-green-600 text-white"
                          : "bg-gray-800 border-gray-700 text-gray-400 hover:text-green-500 hover:border-green-500/50"
                      }`}
                      title="Accept Suggestion"
                    >
                      <Check className="w-4 h-4" />
                      {sug.status === "ACCEPTED" && <span>Accepted</span>}
                    </button>

                    <button
                      onClick={() => handleUpdateStatus(sug.suggestion_id, "REJECTED")}
                      className={`p-2 rounded-lg border transition-colors flex items-center space-x-1.5 text-xs font-semibold ${
                        sug.status === "REJECTED"
                          ? "bg-red-500 border-red-600 text-white"
                          : "bg-gray-800 border-gray-700 text-gray-400 hover:text-red-500 hover:border-red-500/50"
                      }`}
                      title="Reject Suggestion"
                    >
                      <X className="w-4 h-4" />
                      {sug.status === "REJECTED" && <span>Rejected</span>}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        {suggestions.length === 0 && (
          <div className="bg-darkCard border border-gray-800 rounded-xl p-12 text-center text-gray-500 shadow-xl">
            No suggestions generated to improve. Run review audits first.
          </div>
        )}
      </div>

      {/* Apply improvements button */}
      {suggestions.length > 0 && (
        <div className="flex justify-end pt-4">
          <button
            onClick={handleApplyImprovements}
            disabled={loading || workspaceStatus === "PROCESSING"}
            className="flex items-center space-x-2 bg-primaryAccent hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-all text-sm font-semibold shadow-lg shadow-primaryAccent/20 disabled:opacity-50"
          >
            <Sparkles className="w-5 h-5" />
            <span>Generate Improved Version</span>
          </button>
        </div>
      )}

      {/* Evidence Viewer dialog */}
      {selectedEvidence && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-darkCard border border-gray-805 rounded-xl max-w-md w-full overflow-hidden shadow-2xl"
          >
            <div className="px-6 py-4 border-b border-gray-800 flex justify-between items-center bg-darkBg/30">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">CITED EVIDENCE SOURCE</h2>
              <button 
                onClick={() => setSelectedEvidence(null)}
                className="text-gray-400 hover:text-white text-lg font-bold"
              >
                &times;
              </button>
            </div>
            <div className="p-6">
              <p className="text-sm text-gray-300 font-mono bg-darkBg border border-gray-850 p-4 rounded-lg leading-relaxed">
                {selectedEvidence}
              </p>
            </div>
            <div className="px-6 py-4 border-t border-gray-800 flex justify-end bg-darkBg/20">
              <button
                onClick={() => setSelectedEvidence(null)}
                className="bg-primaryAccent hover:bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors text-xs"
              >
                Close source
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};
export default ImprovementPage;
