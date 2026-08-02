import React, { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { useWorkspace } from "../context/WorkspaceContext";
import { Download, FileText, ArrowRight, BookOpen, Monitor } from "lucide-react";
import { buildStyledHTML } from "./TransformationPage"; // Reuse the master HTML formatter

export const ExportPage = () => {
  const { workspaceId, workspaceName, workspaceStatus } = useWorkspace();
  const [downloading, setDownloading] = useState("");

  const handleDownloadPDF = async () => {
    setDownloading("PDF");
    try {
      const response = await axios.post(`/api/workspaces/${workspaceId}/export`, {}, {
        responseType: "blob"
      });
      const blob = new Blob([response.data], { type: "application/pdf" });
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = `${workspaceName || "SEBI"}_DRHP_Prospectus.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("PDF export failed:", err);
    } finally {
      setDownloading("");
    }
  };

  const handleDownloadTransformed = async (type) => {
    setDownloading(type);
    try {
      const response = await axios.get(`/api/transformations/${workspaceId}/${type}/download`, {
        responseType: "blob"
      });
      
      const ext_mapping = {
        PPT_PRESENTATION: "ppt_presentation.pptx",
        WEBSITE_CONTENT: "website_content.html",
        SOCIAL_MEDIA: "social_media.zip",
        IMAGE_PROMPTS: "image_prompts.txt",
        EXECUTIVE_SUMMARY: "executive_summary.pdf",
        INVESTOR_BROCHURE: "investor_brochure.pdf",
        FAQ: "faq.pdf",
        VIDEO_SCRIPT: "video_script.pdf"
      };
      
      const filename = `${workspaceName.replace(/\s+/g, "_")}_${ext_mapping[type] || "document.bin"}`;
      const blob = new Blob([response.data]);
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Transformed asset download failed:", err);
    } finally {
      setDownloading("");
    }
  };

  // Allows user to view the live webpage/slides visually in a new tab directly from the export section
  const handleViewLive = async (type) => {
    try {
      const res = await axios.get(`/api/transformations/${workspaceId}/${type}`);
      if (res.data) {
        const html = buildStyledHTML(type, res.data.title, res.data.content, workspaceName);
        const blob = new Blob([html], { type: "text/html" });
        const url = URL.createObjectURL(blob);
        window.open(url, "_blank");
      }
    } catch (err) {
      const mockText = `# ${type.replace("_", " ")} Outline\n\nGenerated for Workspace: ${workspaceName}.\n`;
      const html = buildStyledHTML(type, type.replace("_", " "), mockText, workspaceName);
      const blob = new Blob([html], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
    }
  };

  const assets = [
    { name: "SEBI Compliant Final DRHP Book (PDF)", type: "PDF", filename: "final_prospectus.pdf", category: "OFFICIAL_PROSPECTUS", size: "~3.8 MB", downloadFn: handleDownloadPDF, canViewLive: false },
    { name: "Executive Summary Report (PDF)", type: "EXECUTIVE_SUMMARY", filename: "executive_summary.pdf", category: "SUMMARY", size: "35 KB", downloadFn: () => handleDownloadTransformed("EXECUTIVE_SUMMARY"), canViewLive: true },
    { name: "Investor Marketing Brochure (PDF)", type: "INVESTOR_BROCHURE", filename: "investor_brochure.pdf", category: "MARKETING", size: "48 KB", downloadFn: () => handleDownloadTransformed("INVESTOR_BROCHURE"), canViewLive: true },
    { name: "IPO Slide Presentation deck (PowerPoint PPTX)", type: "PPT_PRESENTATION", filename: "ppt_presentation.pptx", category: "PRESENTATION", size: "120 KB", downloadFn: () => handleDownloadTransformed("PPT_PRESENTATION"), canViewLive: true },
    { name: "IPO Public FAQ Guide (PDF)", type: "FAQ", filename: "faq.pdf", category: "GUIDELINES", size: "28 KB", downloadFn: () => handleDownloadTransformed("FAQ"), canViewLive: true },
    { name: "Corporate Landing Page Web Portal (HTML)", type: "WEBSITE_CONTENT", filename: "website_content.html", category: "WEBPAGE", size: "10 KB", downloadFn: () => handleDownloadTransformed("WEBSITE_CONTENT"), canViewLive: true },
    { name: "Social Announcement campaign package (ZIP)", type: "SOCIAL_MEDIA", filename: "social_media.zip", category: "SOCIAL", size: "85 KB", downloadFn: () => handleDownloadTransformed("SOCIAL_MEDIA"), canViewLive: true },
    { name: "AI Visual Generation Prompts (TXT)", type: "IMAGE_PROMPTS", filename: "image_prompts.txt", category: "DESIGN", size: "4 KB", downloadFn: () => handleDownloadTransformed("IMAGE_PROMPTS"), canViewLive: true },
    { name: "Promotional Narration Script (PDF)", type: "VIDEO_SCRIPT", filename: "video_script.pdf", category: "SCRIPT", size: "32 KB", downloadFn: () => handleDownloadTransformed("VIDEO_SCRIPT"), canViewLive: true },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Downstream Export</h1>
        <p className="text-gray-400 mt-1">Download compliance-compliant PDFs and digital marketing assets for distribution.</p>
      </div>

      {/* Primary Export Book Panel */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-950/40 to-slate-900/40 border border-primaryAccent/30 rounded-xl p-6 shadow-xl flex flex-col md:flex-row justify-between items-center gap-6"
      >
        <div className="flex items-center space-x-4">
          <div className="bg-primaryAccent/10 border border-primaryAccent/20 p-4 rounded-xl text-primaryAccent">
            <BookOpen className="w-10 h-10" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white uppercase tracking-wide">SEBI COMPLIANT DRHP BOOK</h2>
            <p className="text-sm text-gray-400 mt-1">Compiled in accordance with SEBI ICDR Regulations including warnings, headers, footers, and page numbers.</p>
          </div>
        </div>
        <button
          onClick={handleDownloadPDF}
          disabled={downloading === "PDF"}
          className="flex items-center space-x-2 bg-primaryAccent hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-lg transition-all text-sm shadow-lg shadow-primaryAccent/20 disabled:opacity-50 flex-shrink-0"
        >
          <Download className="w-4 h-4" />
          <span>{downloading === "PDF" ? "Compiling Book..." : "Compile & Download PDF"}</span>
        </button>
      </motion.div>

      {/* Assets Table Inventory */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-darkCard border border-gray-800/80 rounded-xl overflow-hidden shadow-xl"
      >
        <div className="px-6 py-4 border-b border-gray-800 flex justify-between items-center">
          <h3 className="font-bold text-white uppercase tracking-wide text-xs">Transformed Deliverables Packages</h3>
        </div>

        <div className="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead class="bg-darkBg/50 text-[10px] font-bold text-gray-500 uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="px-6 py-3">Asset Description</th>
                <th className="px-6 py-3">Category</th>
                <th className="px-6 py-3">Format</th>
                <th className="px-6 py-3">Est. Size</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800 text-sm text-gray-300">
              {assets.map((asset, idx) => (
                <tr key={idx} className="hover:bg-gray-800/10 transition-colors">
                  <td className="px-6 py-4 font-semibold text-white flex items-center space-x-3">
                    <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    <span>{asset.name}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-xs bg-gray-800 px-2.5 py-0.5 rounded text-gray-400 font-semibold border border-gray-700/50">
                      {asset.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-xs text-gray-500 uppercase">
                    {asset.filename.split(".").pop()}
                  </td>
                  <td className="px-6 py-4 text-xs text-gray-500">{asset.size}</td>
                  <td className="px-6 py-4 text-right">
                    <div className="inline-flex items-center space-x-2">
                      {asset.canViewLive && (
                        <button
                          onClick={() => handleViewLive(asset.type)}
                          className="inline-flex items-center space-x-1 bg-darkBg border border-gray-750 hover:bg-gray-800 text-gray-400 hover:text-white px-3 py-1.5 rounded-lg transition-all text-xs font-semibold"
                          title="View Live Visual Page"
                        >
                          <Monitor className="w-3.5 h-3.5" />
                          <span>View Live</span>
                        </button>
                      )}
                      <button
                        onClick={asset.downloadFn}
                        disabled={downloading === asset.type}
                        className="inline-flex items-center space-x-1 bg-gray-800 hover:bg-primaryAccent hover:text-white text-gray-400 px-3 py-1.5 rounded-lg border border-gray-750 hover:border-primaryAccent transition-all text-xs font-semibold disabled:opacity-50"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>{downloading === asset.type ? "Downloading..." : "Download"}</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
};
export default ExportPage;
