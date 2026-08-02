import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { useWorkspace } from "../context/WorkspaceContext";
import { Search, ShieldAlert, CheckCircle2, ChevronRight, Filter } from "lucide-react";

export const ReviewPage = () => {
  const { workspaceId, workspaceStatus } = useWorkspace();
  const [suggestions, setSuggestions] = useState([]);
  const [filterReviewer, setFilterReviewer] = useState("ALL");
  const [filterSeverity, setFilterSeverity] = useState("ALL");
  const [loading, setLoading] = useState(false);

  const fetchSuggestions = async () => {
    if (!workspaceId) return;
    setLoading(true);
    try {
      const res = await axios.get(`/api/reviews/${workspaceId}/suggestions`);
      setSuggestions(res.data.suggestions || []);
    } catch (err) {
      console.warn("Could not query suggestions list details.", err);
      // Offline fallback seeds
      setSuggestions([
        { suggestion_id: "SUG-001", section_slug: "LEGAL_LITIGATION_DECLARATION", section_version: 1, reviewer: "LEGAL", severity: "MEDIUM", confidence: 0.9, reason: "Outstanding litigation requires a petition reference number.", evidence: "Fact category: LITIGATION, source: litigation_audit.pdf", recommendation: "Append: 'Municipal corporation petition status is pending under reference suit no. 204/2025.'", status: "OPEN" },
        { suggestion_id: "SUG-002", section_slug: "FINANCIAL_HIGHLIGHTS_MDA", section_version: 1, reviewer: "FINANCE", severity: "HIGH", confidence: 0.98, reason: "FY25 revenue totals must match corporate audited balance sheets.", evidence: "Fact category: FINANCIAL_STATEMENTS, source: financial_highlights.json", recommendation: "Ensure revenue reads INR 1,250 Crores in subsequent statements.", status: "OPEN" },
        { suggestion_id: "SUG-003", section_slug: "RISK_FACTORS", section_version: 1, reviewer: "RISK", severity: "MEDIUM", confidence: 0.92, reason: "The server downtime risk lacks mitigation details.", evidence: "Fact category: RISK_REGISTRY, source: risk_registry.json", recommendation: "Add clause: We mitigate downtime via multi-region cloud backup strategies.", status: "ACCEPTED" }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  }, [workspaceId, workspaceStatus]);

  const handleRunReview = async () => {
    setLoading(true);
    try {
      await axios.post(`/api/reviews/${workspaceId}/run`);
      fetchSuggestions();
    } catch (err) {
      console.error("Running review engine failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const reviewers = ["ALL", "LEGAL", "FINANCE", "RISK", "COMPLIANCE", "LANGUAGE", "CONSISTENCY", "BUSINESS"];
  const severities = ["ALL", "HIGH", "MEDIUM", "LOW"];

  const filteredSuggestions = suggestions.filter(sug => {
    const matchReviewer = filterReviewer === "ALL" || sug.reviewer === filterReviewer;
    const matchSeverity = filterSeverity === "ALL" || sug.severity === filterSeverity;
    return matchReviewer && matchSeverity;
  });

  const getSeverityStyle = (sev) => {
    switch (sev) {
      case "HIGH":
        return "bg-red-500/10 text-red-500 border-red-500/20";
      case "MEDIUM":
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
      case "LOW":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      default:
        return "bg-gray-800 text-gray-400 border-gray-700";
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Panel */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">AI Compliance Review</h1>
          <p className="text-gray-400 mt-1">Review SEBI guidelines audits, grammatical style edits, and corporate metrics matches.</p>
        </div>
        <button
          onClick={handleRunReview}
          disabled={loading}
          className="flex items-center space-x-2 bg-primaryAccent hover:bg-blue-600 text-white px-4 py-2.5 rounded-lg transition-all text-sm font-semibold shadow-lg shadow-primaryAccent/20 disabled:opacity-50"
        >
          <span>{loading ? "Running audits..." : "Execute Review Engine"}</span>
        </button>
      </div>

      {/* Filter Toolbar bar */}
      <div className="bg-darkCard border border-gray-805 rounded-xl p-4 flex flex-wrap gap-4 items-center shadow-md">
        <div className="flex items-center space-x-2 text-xs font-bold text-gray-500 uppercase tracking-wider">
          <Filter className="w-4 h-4 text-gray-600" />
          <span>Filters:</span>
        </div>
        
        {/* Reviewer Filter selection */}
        <div>
          <select
            value={filterReviewer}
            onChange={(e) => setFilterReviewer(e.target.value)}
            className="bg-darkBg border border-gray-800 focus:border-primaryAccent rounded-lg text-xs font-semibold text-gray-300 px-3 py-2 outline-none cursor-pointer"
          >
            {reviewers.map((rev, idx) => (
              <option key={idx} value={rev}>
                Reviewer: {rev === "ALL" ? "All Reviewers" : rev}
              </option>
            ))}
          </select>
        </div>

        {/* Severity Filter selection */}
        <div>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-darkBg border border-gray-800 focus:border-primaryAccent rounded-lg text-xs font-semibold text-gray-300 px-3 py-2 outline-none cursor-pointer"
          >
            {severities.map((sev, idx) => (
              <option key={idx} value={sev}>
                Severity: {sev === "ALL" ? "All Severities" : sev}
              </option>
            ))}
          </select>
        </div>

        <span className="text-xs text-gray-500 ml-auto">
          Showing {filteredSuggestions.length} of {suggestions.length} suggestions
        </span>
      </div>

      {/* GitHub Issues style suggestions list */}
      <div className="space-y-4">
        {filteredSuggestions.map((sug, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.05 }}
            className="bg-darkCard border border-gray-800/80 rounded-xl p-6 hover:border-gray-700 transition-all shadow-lg flex flex-col md:flex-row gap-6 justify-between items-start"
          >
            {/* Suggestion Core Info */}
            <div className="space-y-3 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold text-gray-500 font-mono">#{sug.suggestion_id.slice(0, 8)}</span>
                <span className="text-xs bg-gray-800/60 border border-gray-750 px-2 py-0.5 rounded text-gray-400 font-semibold uppercase tracking-wider">
                  {sug.reviewer} REVIEWER
                </span>
                <span className={`text-[10px] font-bold border px-2 py-0.5 rounded-full ${getSeverityStyle(sug.severity)}`}>
                  {sug.severity}
                </span>
                <span className="text-xs text-gray-500">
                  Target: <span className="font-semibold text-gray-300">{sug.section_slug}</span> (v{sug.section_version})
                </span>
              </div>
              
              <h2 className="text-sm font-semibold text-white uppercase tracking-wide">
                {sug.reason}
              </h2>
              
              <div className="text-sm text-gray-300 pl-4 border-l-2 border-primaryAccent/50">
                <span className="text-xs font-bold text-gray-500 block uppercase mb-1">Recommendation</span>
                <p className="italic font-sans">"{sug.recommendation}"</p>
              </div>
              
              <div className="text-xs text-gray-500 flex items-center space-x-2">
                <span className="font-semibold text-gray-400">Evidence Cited:</span>
                <span className="font-mono bg-darkBg border border-gray-850 px-2 py-0.5 rounded text-gray-400 truncate max-w-sm">
                  {sug.evidence}
                </span>
              </div>
            </div>

            {/* Status Panel Actions */}
            <div className="flex flex-col items-end justify-between self-stretch flex-shrink-0 gap-4">
              <span className={`text-[10px] font-bold px-3 py-1 rounded-full flex items-center space-x-1.5 ${
                sug.status === "ACCEPTED" 
                  ? "bg-green-500/10 text-green-500" 
                  : sug.status === "REJECTED" 
                    ? "bg-red-500/10 text-red-500" 
                    : "bg-yellow-500/10 text-yellow-500"
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${
                  sug.status === "ACCEPTED" ? "bg-green-500" : sug.status === "REJECTED" ? "bg-red-500" : "bg-yellow-500"
                }`} />
                <span>{sug.status}</span>
              </span>

              <div className="text-xs text-gray-500 font-medium">
                {Math.round(sug.confidence * 100)}% Match Confidence
              </div>
            </div>
          </motion.div>
        ))}

        {filteredSuggestions.length === 0 && (
          <div className="bg-darkCard border border-gray-800 rounded-xl p-12 text-center text-gray-500 shadow-lg">
            No reviewer findings match the active filter criteria.
          </div>
        )}
      </div>
    </div>
  );
};
export default ReviewPage;
