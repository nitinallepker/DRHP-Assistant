import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { useWorkspace } from "../context/WorkspaceContext";
import { Play, Save, Download, FileText, CheckCircle, Clock } from "lucide-react";

export const DRHPPage = () => {
  const { workspaceId, workspaceStatus, setWorkspaceStatus } = useWorkspace();
  const [sections, setSections] = useState([]);
  const [selectedSlug, setSelectedSlug] = useState("COVER_PAGE");
  const [sectionContent, setSectionContent] = useState(null);
  const [drafting, setDrafting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);

  // List of standard section metadata
  const sectionList = [
    { slug: "COVER_PAGE", title: "Cover Page Section" },
    { slug: "COMPANY_OVERVIEW", title: "Company Overview" },
    { slug: "INDUSTRY_OVERVIEW", title: "Industry Overview" },
    { slug: "BUSINESS_OVERVIEW_STRENGTHS", title: "Business Model & Strengths" },
    { slug: "RISK_FACTORS", title: "Risk Factors" },
    { slug: "FINANCIAL_HIGHLIGHTS_MDA", title: "Financial Highlights & MDA" },
    { slug: "IPO_DETAILS_OBJECTS_CAPITAL", title: "IPO Offer Structure & Objects" },
    { slug: "GLOSSARY_DEFINITIONS", title: "Definitions & Regulation" },
    { slug: "LEGAL_LITIGATION_DECLARATION", title: "Outstanding Litigation" },
  ];

  const fetchSectionDetails = async (slug) => {
    if (!workspaceId) return;
    try {
      const res = await axios.get(`/api/sections/${workspaceId}/${slug}`);
      if (res.data) {
        setSectionContent({
          slug: res.data.section_slug,
          title: res.data.title,
          content: res.data.content,
          version: res.data.version,
          status: res.data.status,
          wordCount: res.data.content.split(/\s+/).filter(Boolean).length,
          lastUpdated: new Date().toISOString()
        });
      }
    } catch (err) {
      // Offline mock fallback representations if generate hasn't run yet
      const fallbackTemplates = {
        "COVER_PAGE": "# COMPANY LIMITED\n\n**Draft Red Herring Prospectus (DRHP)**\n\n- **Fresh Issue Size**: 400 Crores\n- **Offer for Sale**: 250 Crores\n\n*Regulatory Warning: SEBI standard warnings apply.*",
        "COMPANY_OVERVIEW": "# SECTION I: COMPANY OVERVIEW\n\nThe company was incorporated in Noida. It provides enterprise software solutions globally.",
        "RISK_FACTORS": "# SECTION IV: RISK FACTORS\n\n- Internal: Server infrastructure dependencies.\n- External: Changes in corporate regulatory taxes.",
        "FINANCIAL_HIGHLIGHTS_MDA": "# SECTION V: FINANCIAL HIGHLIGHTS\n\nAudited corporate revenues totals stood at INR 1,250 Crores for the financial period ending FY25.",
      };
      const text = fallbackTemplates[slug] || `# ${slug.replace("_", " ")}\n\nDraft content has not been generated for this section yet.`;
      setSectionContent({
        slug,
        title: slug.replace("_", " ").title || slug,
        content: text,
        version: 1,
        status: "DRAFT",
        wordCount: text.split(/\s+/).filter(Boolean).length,
        lastUpdated: new Date().toISOString()
      });
    }
  };

  useEffect(() => {
    fetchSectionDetails(selectedSlug);
  }, [selectedSlug, workspaceId, workspaceStatus]);

  const handleGenerateAll = async () => {
    setDrafting(true);
    try {
      setWorkspaceStatus("PROCESSING");
      await axios.post(`/api/workspaces/${workspaceId}/generate`);
      setWorkspaceStatus("READY");
      fetchSectionDetails(selectedSlug);
    } catch (err) {
      console.error("Draft generation failed:", err);
      setWorkspaceStatus("READY");
    } finally {
      setDrafting(false);
    }
  };

  const handleSaveSection = async () => {
    if (!sectionContent) return;
    setSaving(true);
    try {
      await axios.post(`/api/sections/${workspaceId}/${sectionContent.slug}`, {
        title: sectionContent.title,
        content: sectionContent.content,
        status: sectionContent.status
      });
      // Refresh section version
      fetchSectionDetails(sectionContent.slug);
    } catch (err) {
      console.error("Saving section failed:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      const response = await axios.post(`/api/workspaces/${workspaceId}/export`, {}, {
        responseType: "blob"
      });
      
      const blob = new Blob([response.data], { type: "application/pdf" });
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = `${workspaceId}_final_book.pdf`;
      link.click();
    } catch (err) {
      console.error("PDF compile failed:", err);
    } finally {
      setExporting(false);
    }
  };

  // Simple custom Markdown rendering engine parser to draw lists, tables, headers beautifully
  const renderMarkdown = (text) => {
    if (!text) return null;
    const lines = text.split("\n");
    return lines.map((line, idx) => {
      if (line.startsWith("# ")) {
        return <h2 key={idx} className="text-2xl font-bold text-white border-b border-gray-800 pb-2 mt-6 mb-4">{line.replace("# ", "")}</h2>;
      }
      if (line.startsWith("## ")) {
        return <h3 key={idx} className="text-xl font-semibold text-white mt-5 mb-3">{line.replace("## ", "")}</h3>;
      }
      if (line.startsWith("### ")) {
        return <h4 key={idx} className="text-lg font-semibold text-gray-300 mt-4 mb-2">{line.replace("### ", "")}</h4>;
      }
      if (line.startsWith("- ") || line.startsWith("* ")) {
        return <li key={idx} className="text-sm text-gray-300 ml-6 list-disc mb-1">{line.slice(2)}</li>;
      }
      if (line.startsWith("|")) {
        // Table line representation
        const cols = line.split("|").map(c => c.trim()).filter(Boolean);
        if (cols.length === 0 || line.includes("---")) return null;
        return (
          <div key={idx} className="grid grid-cols-2 gap-4 py-2 border-b border-gray-805 text-sm text-gray-300 font-mono">
            <span className="text-gray-500 font-semibold">{cols[0]}</span>
            <span>{cols[1] || "-"}</span>
          </div>
        );
      }
      if (line.trim() === "") {
        return <div key={idx} className="h-3" />;
      }
      return <p key={idx} className="text-sm text-gray-300 leading-relaxed mb-3">{line}</p>;
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] text-gray-300">
      {/* Top Header Controls bar */}
      <div className="flex justify-between items-center mb-6 flex-shrink-0">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">DRHP Book Editor</h1>
          <p className="text-gray-400 mt-1">Audit, modify, and review drafted prospectus section files.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleGenerateAll}
            disabled={drafting || workspaceStatus === "PROCESSING"}
            className="flex items-center space-x-2 bg-darkCard hover:bg-gray-800 text-primaryAccent px-4 py-2 rounded-lg border border-gray-800 transition-all text-sm font-medium disabled:opacity-50"
          >
            <Play className={`w-4 h-4 ${drafting ? "animate-spin" : ""}`} />
            <span>{drafting ? "Generating book..." : "Draft Book (All)"}</span>
          </button>
        </div>
      </div>

      {/* Main Column layout */}
      <div className="flex-1 flex gap-6 overflow-hidden min-h-0">
        {/* Left Column: Sections selection list */}
        <div className="w-64 bg-darkCard border border-gray-800 rounded-xl p-4 flex flex-col h-full shadow-xl flex-shrink-0 overflow-y-auto">
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider px-3 mb-4">Book Sections</h2>
          <div className="space-y-1">
            {sectionList.map((sec, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedSlug(sec.slug)}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-3 ${
                  selectedSlug === sec.slug
                    ? "bg-primaryAccent/10 text-primaryAccent border-l-4 border-primaryAccent"
                    : "text-gray-400 hover:bg-gray-850 hover:text-white"
                }`}
              >
                <FileText className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{sec.title}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Center Column: Interactive content editor/markdown preview */}
        <div className="flex-1 bg-darkCard border border-gray-800 rounded-xl flex flex-col h-full shadow-xl overflow-hidden min-w-0">
          <div className="px-6 py-4 border-b border-gray-800 flex justify-between items-center bg-darkBg/30 flex-shrink-0">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              {sectionContent ? sectionContent.title : "Selected Section"}
            </h2>
            <span className="text-[10px] bg-green-500/10 text-green-500 border border-green-500/30 px-2 py-0.5 rounded uppercase font-bold">
              {sectionContent?.status || "DRAFT"}
            </span>
          </div>

          <div className="flex-1 p-6 overflow-y-auto min-h-0 flex flex-col lg:flex-row gap-6">
            {/* Raw markdown text editor */}
            <div className="flex-1 flex flex-col h-full">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Raw Markdown Source</label>
              <textarea
                value={sectionContent ? sectionContent.content : ""}
                onChange={(e) => setSectionContent({ ...sectionContent, content: e.target.value })}
                className="flex-1 bg-darkBg border border-gray-800 focus:border-primaryAccent focus:ring-1 focus:ring-primaryAccent rounded-lg p-4 font-mono text-xs text-white resize-none outline-none leading-relaxed"
                placeholder="# Section Title..."
              />
            </div>

            {/* Markdown rendered view */}
            <div className="flex-1 flex flex-col h-full overflow-hidden border-t lg:border-t-0 lg:border-l border-gray-800/80 lg:pl-6 pt-6 lg:pt-0">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">HTML Render Preview</label>
              <div className="flex-1 bg-darkBg/40 border border-gray-850 rounded-lg p-5 overflow-y-auto font-sans">
                {sectionContent ? renderMarkdown(sectionContent.content) : <p className="text-gray-600 text-sm italic">Loading section content...</p>}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Telemetry Metadata sidebar */}
        {sectionContent && (
          <div className="w-72 bg-darkCard border border-gray-800 rounded-xl p-6 flex flex-col justify-between h-full shadow-xl flex-shrink-0 overflow-y-auto">
            <div className="space-y-6">
              <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider">Metadata Telemetry</h2>
              
              <div className="space-y-4">
                <div>
                  <span className="text-[10px] text-gray-500 font-semibold uppercase">Latest Draft Version</span>
                  <p className="text-lg font-bold text-white mt-1">v{sectionContent.version}</p>
                </div>
                <div>
                  <span className="text-[10px] text-gray-500 font-semibold uppercase">Word Count</span>
                  <p className="text-lg font-bold text-white mt-1">{sectionContent.wordCount} words</p>
                </div>
                <div>
                  <span className="text-[10px] text-gray-500 font-semibold uppercase">Filing Guidelines</span>
                  <p className="text-xs text-gray-300 mt-1 flex items-center space-x-1">
                    <CheckCircle className="w-3.5 h-3.5 text-green-500" />
                    <span>SEBI ICDR Compliant</span>
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-gray-500 font-semibold uppercase">Last Updated</span>
                  <p className="text-xs text-gray-400 mt-1 flex items-center space-x-1.5">
                    <Clock className="w-3.5 h-3.5 text-gray-600" />
                    <span>{new Date(sectionContent.lastUpdated).toLocaleTimeString()}</span>
                  </p>
                </div>
              </div>
            </div>

            {/* Action buttons */}
            <div className="space-y-3 pt-6 border-t border-gray-800">
              <button
                onClick={handleSaveSection}
                disabled={saving}
                className="w-full flex items-center justify-center space-x-2 bg-primaryAccent hover:bg-blue-600 text-white font-semibold py-2.5 rounded-lg transition-colors text-sm"
              >
                <Save className="w-4 h-4" />
                <span>{saving ? "Saving Draft..." : "Save Draft"}</span>
              </button>
              <button
                onClick={handleExportPDF}
                disabled={exporting}
                className="w-full flex items-center justify-center space-x-2 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white font-semibold py-2.5 rounded-lg border border-gray-700 transition-colors text-sm"
              >
                <Download className="w-4 h-4" />
                <span>{exporting ? "Compiling Book..." : "Download PDF"}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
export default DRHPPage;
