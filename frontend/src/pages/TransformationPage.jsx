import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { useWorkspace } from "../context/WorkspaceContext";
import { Play, Eye, Download, FileText, CheckCircle2, Monitor } from "lucide-react";

// Master function to construct styled, high-fidelity visual HTML pages from raw markdown text
export const buildStyledHTML = (contentType, title, contentText, workspaceName) => {
  const lines = contentText.split("\n");
  const cleanName = workspaceName || "ABC Industries";

  // Helper: Basic Markdown inline parser for bold and italics
  const parseInline = (text) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/`(.*?)`/g, "<code class='bg-slate-800 px-1.5 py-0.5 rounded text-xs font-mono'>$1</code>");
  };

  // Unique Layout 1: WEBSITE_CONTENT (SaaS Landing Page)
  if (contentType === "WEBSITE_CONTENT") {
    // Extract a description from paragraphs to use as a hero subtitle
    const paragraph = lines.find(l => l.trim().length > 30 && !l.trim().startsWith("#") && !l.trim().startsWith("-")) || "Compliance-ready investor portal presenting corporate financials, IPO details, and regulatory filings.";
    
    // Extract bullet points to display in a beautiful features grid
    const bulletLines = lines.filter(l => l.trim().startsWith("-") || l.trim().startsWith("*")).map(l => l.trim().slice(2));
    const features = bulletLines.slice(0, 3);
    const mockFeatures = [
      { t: "Optimal Capitalization", d: "Solid EBITDA margins and structured debt reduction." },
      { t: "Market Leadership", d: "Leading client bases across core software services." },
      { t: "SEBI Compliant", d: "Strict regulatory disclosures audited by AI reviewers." }
    ];
    while (features.length < 3) {
      features.push(mockFeatures[features.length]?.t + ": " + mockFeatures[features.length]?.d || "Data Node");
    }

    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title} | ${cleanName}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans">
  <!-- Nav Menu -->
  <header class="bg-slate-900/80 backdrop-blur border-b border-slate-800 sticky top-0 py-4 px-8 flex justify-between items-center z-50">
    <div class="flex items-center space-x-2">
      <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white uppercase">${cleanName.slice(0,2)}</div>
      <div>
        <h1 class="text-sm font-black tracking-widest uppercase text-white">${cleanName}</h1>
        <p class="text-[8px] text-blue-400 font-bold uppercase tracking-widest">Investor Relations Portal</p>
      </div>
    </div>
    <nav class="flex items-center space-x-6 text-xs font-bold text-slate-400 uppercase tracking-wider">
      <a href="#" class="text-white hover:text-blue-500 transition-colors">Prospectus Summary</a>
      <a href="#" class="hover:text-blue-500 transition-colors">Issue Details</a>
      <a href="#" class="hover:text-blue-500 transition-colors">Key Metrics</a>
      <a href="#" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">Register as Investor</a>
    </nav>
  </header>

  <!-- Hero Section -->
  <div class="relative px-8 py-24 text-center overflow-hidden border-b border-slate-900 bg-gradient-to-b from-slate-900 to-slate-950">
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.12),transparent_70%)]"></div>
    <div class="relative max-w-3xl mx-auto">
      <span class="text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-3 py-1 rounded-full font-bold uppercase tracking-widest">IPO Public Announcement</span>
      <h1 class="text-4xl md:text-5xl font-black text-white mt-6 leading-tight tracking-tight uppercase">${cleanName} Limited</h1>
      <p class="text-base text-slate-400 mt-4 leading-relaxed max-w-2xl mx-auto">${parseInline(paragraph)}</p>
      <div class="flex justify-center gap-4 mt-10">
        <a href="#" class="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-3 rounded-lg transition-colors text-xs uppercase tracking-wider">Download DRHP (PDF)</a>
        <a href="#" class="bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 font-bold px-6 py-3 rounded-lg transition-colors text-xs uppercase tracking-wider">Audit History</a>
      </div>
    </div>
  </div>

  <!-- Highlights Grid -->
  <section class="max-w-6xl w-full mx-auto px-6 py-20">
    <h2 class="text-xl font-black text-white text-center mb-12 uppercase tracking-widest text-blue-500">Core Investment Strengths</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      ${features.map(f => {
        const parts = f.split(":");
        const title = parts[0]?.trim() || "Advantage";
        const desc = parts.slice(1).join(":")?.trim() || "High growth and regulatory compliance metrics.";
        return `
          <div class="bg-slate-900 border border-slate-800/80 rounded-xl p-6 hover:border-blue-500/30 transition-all shadow-xl relative overflow-hidden group">
            <div class="absolute top-0 left-0 right-0 h-[2px] bg-slate-800 group-hover:bg-blue-500 transition-colors"></div>
            <h3 class="text-base font-bold text-white uppercase tracking-wide mb-3">${title}</h3>
            <p class="text-xs text-slate-400 leading-relaxed">${parseInline(desc)}</p>
          </div>
        `;
      }).join("")}
    </div>
  </section>

  <!-- Prospectus Details Container -->
  <section class="max-w-4xl w-full mx-auto px-6 py-6 flex-1">
    <div class="bg-slate-900 border border-slate-850 rounded-2xl p-8 shadow-2xl">
      <h3 class="text-sm font-black text-slate-500 uppercase tracking-widest mb-6">Filing Disclosures</h3>
      <div class="text-slate-350 space-y-4 text-sm leading-relaxed">
        ${lines.filter(l => !l.trim().startsWith("#") && !l.trim().startsWith("-")).slice(3, 8).map(l => `<p>${parseInline(l)}</p>`).join("")}
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="bg-slate-950 border-t border-slate-900 py-8 px-8 text-center text-xs text-slate-500 mt-12">
    © ${new Date().getFullYear()} ${cleanName} Limited. Proprietary IPO filing material under SEBI ICDR guidelines. All rights reserved.
  </footer>
</body>
</html>
    `;
  }

  // Unique Layout 2: INVESTOR_BROCHURE (Dossier Pamphlet)
  if (contentType === "INVESTOR_BROCHURE") {
    const listItems = lines.filter(l => l.trim().startsWith("-") || l.trim().startsWith("*")).map(l => l.trim().slice(2));
    const paragraphs = lines.filter(l => l.trim().length > 20 && !l.trim().startsWith("#") && !l.trim().startsWith("-") && !l.trim().startsWith("|"));
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title} | ${cleanName}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B1220] text-slate-100 min-h-screen py-10 px-6 font-sans">
  <div class="max-w-5xl mx-auto bg-[#151E2D] border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
    <!-- Brochure Header Banner -->
    <div class="bg-gradient-to-r from-blue-900/40 to-indigo-950/40 border-b border-slate-800 p-8 flex flex-col md:flex-row justify-between items-center gap-6">
      <div>
        <span class="text-[9px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-3 py-1 rounded-full font-black tracking-widest uppercase">Investor Leaflet Dossier</span>
        <h1 class="text-3xl font-black text-white mt-4 uppercase tracking-tight">${cleanName} LIMITED</h1>
        <p class="text-xs text-slate-400 mt-1.5">Official marketing collateral outlining business strengths and objects of issue.</p>
      </div>
      <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl text-center flex-shrink-0 min-w-[140px]">
        <span class="text-[9px] font-bold text-slate-500 block uppercase">Aggregate Issue</span>
        <span class="text-2xl font-black text-white block mt-1">₹650 Cr</span>
        <span class="text-[10px] bg-green-500/10 text-green-500 px-2 py-0.5 rounded font-bold mt-1.5 inline-block uppercase">READY</span>
      </div>
    </div>

    <!-- Brochure Main Body columns -->
    <div class="grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-slate-800">
      <!-- Left Column: Dossier Details -->
      <div class="p-8 lg:col-span-2 space-y-6">
        <h2 class="text-lg font-black text-white uppercase tracking-wider border-b border-slate-800 pb-3">Corporate Narrative</h2>
        <div class="text-slate-300 text-sm leading-relaxed space-y-4">
          ${paragraphs.slice(0, 3).map(p => `<p>${parseInline(p)}</p>`).join("")}
        </div>

        <h3 class="text-sm font-black text-blue-400 uppercase tracking-widest mt-8">Highlights Portfolio</h3>
        <ul class="grid grid-cols-1 md:grid-cols-2 gap-4">
          ${listItems.map(item => `
            <li class="flex items-start space-x-2 text-xs text-slate-350 bg-slate-900 border border-slate-850 p-3 rounded-lg">
              <span class="text-blue-500 font-bold mr-1">✓</span>
              <span>${parseInline(item)}</span>
            </li>
          `).join("")}
        </ul>
      </div>

      <!-- Right Column: Stats Panel -->
      <div class="p-8 bg-slate-900/40 space-y-6">
        <h2 class="text-sm font-black text-slate-500 uppercase tracking-widest border-b border-slate-800 pb-3">Filing Telemetry</h2>
        <div class="space-y-4">
          <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <span class="text-[9px] font-bold text-slate-500 uppercase block">Registered Office</span>
            <span class="text-xs text-white block mt-1 font-semibold">Bandra Kurla Complex, Mumbai</span>
          </div>
          <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <span class="text-[9px] font-bold text-slate-500 uppercase block">Promoters</span>
            <span class="text-xs text-white block mt-1 font-semibold">Nitin Sharma & Sharma Capital Group</span>
          </div>
          <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <span class="text-[9px] font-bold text-slate-500 uppercase block">Fresh Issue Size</span>
            <span class="text-xs text-white block mt-1 font-semibold">₹400 Crores</span>
          </div>
          <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <span class="text-[9px] font-bold text-slate-500 uppercase block">Regulatory Advisor</span>
            <span class="text-[10px] text-blue-400 font-bold block mt-1 uppercase">DRHP Compliance AI OS</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Brochure Footer -->
    <div class="bg-slate-950 border-t border-slate-800 p-6 text-center text-[10px] text-slate-500 uppercase font-semibold">
      © ${cleanName} Limited. Restricted distribution brochure. Not for publication in foreign jurisdictions.
    </div>
  </div>
</body>
</html>
    `;
  }

  // Unique Layout 3: PPT_PRESENTATION (Widescreen 16:9 Deck View)
  if (contentType === "PPT_PRESENTATION") {
    const slides = contentText.split(/(?=Slide \d+:|# Slide \d+:)/i).filter(Boolean);
    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title} | ${cleanName}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .slide-card {
      background-color: #151E2D;
      border: 1px solid #1e293b;
      border-radius: 1rem;
      padding: 2rem;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
      margin-bottom: 2.5rem;
      position: relative;
      overflow: hidden;
      aspect-ratio: 16 / 9;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
  </style>
</head>
<body class="bg-slate-950 text-slate-200 py-10 px-6 font-sans">
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="text-center mb-8">
      <span class="text-[9px] bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full font-black tracking-widest uppercase">IPO Roadshow Presentation</span>
      <h1 class="text-2xl font-black text-white uppercase tracking-wider mt-2">${cleanName} LIMITED</h1>
    </div>

    <!-- Map Slide Content -->
    ${slides.map((slideText, sIdx) => {
      const slideLines = slideText.trim().split("\n");
      const slideTitle = slideLines[0].replace(/^(#\s*|Slide\s*\d+:\s*)/i, "").trim() || `Slide ${sIdx + 1}`;
      const bullets = slideLines.slice(1).map(l => l.trim()).filter(l => l.startsWith("-") || l.startsWith("*")).map(l => l.slice(2));
      return `
        <div class="slide-card">
          <!-- Slide Header -->
          <div class="flex justify-between items-center border-b border-slate-800 pb-3 flex-shrink-0">
            <span class="text-[10px] font-black text-blue-500 tracking-widest uppercase">SLIDE ${sIdx + 1} OF ${slides.length}</span>
            <span class="text-[9px] text-slate-500 uppercase font-black tracking-wider">${cleanName} Roadshow Deck</span>
          </div>

          <!-- Slide Content -->
          <div class="flex-1 flex flex-col justify-center my-4">
            <h2 class="text-2xl font-black text-white tracking-wide uppercase mb-4">${slideTitle}</h2>
            <ul class="list-disc pl-6 space-y-2.5 text-slate-350 text-sm">
              ${bullets.length > 0 ? bullets.map(b => `<li>${parseInline(b)}</li>`).join("") : `<p class="italic text-slate-500 text-xs">${slideLines.slice(1).join("<br>")}</p>`}
            </ul>
          </div>

          <!-- Slide Footer -->
          <div class="flex justify-between items-center text-[9px] text-slate-600 border-t border-slate-800/80 pt-3 flex-shrink-0 uppercase font-bold">
            <span>SEBI Registered Filing</span>
            <span>Strictly Confidential</span>
          </div>
        </div>
      `;
    }).join("")}
  </div>
</body>
</html>
    `;
  }

  // Unique Layout 4: VIDEO_SCRIPT (2-Column Production Table)
  if (contentType === "VIDEO_SCRIPT") {
    // Attempt to extract visual direction blocks and voiceovers
    const scriptRows = [];
    let currentBlock = { visual: "", audio: "" };
    
    for (let line of lines) {
      const trimLine = line.trim();
      if (trimLine.toLowerCase().includes("visual") || trimLine.startsWith("[") || trimLine.toLowerCase().includes("camera")) {
        if (currentBlock.visual || currentBlock.audio) {
          scriptRows.push({ ...currentBlock });
          currentBlock = { visual: "", audio: "" };
        }
        currentBlock.visual = trimLine.replace(/^[\[\s]*visuals?[\s\]:]*/i, "").replace(/[\]\s]*$/g, "");
      } else if (trimLine.toLowerCase().includes("voice") || trimLine.toLowerCase().includes("audio") || trimLine.toLowerCase().includes("narrator")) {
        currentBlock.audio = trimLine.replace(/^[\[\s]*audio[\s\]:]*/i, "").replace(/^[\[\s]*voiceover[\s\]:]*/i, "");
      } else if (trimLine.length > 10) {
        if (currentBlock.visual && !currentBlock.audio) {
          currentBlock.audio = trimLine;
        } else if (!currentBlock.visual) {
          currentBlock.visual = trimLine;
        } else {
          scriptRows.push({ ...currentBlock });
          currentBlock = { visual: trimLine, audio: "" };
        }
      }
    }
    if (currentBlock.visual || currentBlock.audio) {
      scriptRows.push(currentBlock);
    }

    // Standard fallback rows if script parse is empty
    if (scriptRows.length === 0) {
      scriptRows.push(
        { visual: "Open on corporate logo overlay, shifting dynamically into drone B-Roll footage of tech office headquarters.", audio: `Voiceover: Welcome to the future of compliance operations. Presenting ${cleanName} Limited's upcoming initial public offering.` },
        { visual: "Pan into key metrics dashboard cards zooming on revenue growth from 850 Cr to 1250 Cr.", audio: "Voiceover: Strong business capitalization with fiscal revenue metrics expanding rapidly." },
        { visual: "Transition to compliance checklist screen with checkmark badges lighting up green.", audio: "Voiceover: Fully vetted and audited for SEBI compliance under automated AI operating systems." }
      );
    }

    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title} | ${cleanName}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B1220] text-slate-200 py-10 px-6 font-sans">
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8 flex justify-between items-center shadow-xl">
      <div>
        <span class="text-[9px] bg-red-500/10 text-red-400 px-3 py-1 rounded-full font-black tracking-widest uppercase">Promotional Video Script</span>
        <h1 class="text-xl font-black text-white mt-3 uppercase tracking-wider">${cleanName} IPO Launch Clip</h1>
      </div>
      <div class="text-right text-[10px] text-slate-500 uppercase font-black">Length: 2 Min</div>
    </div>

    <!-- Script Grid Table -->
    <div class="bg-[#151E2D] border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
      <div class="grid grid-cols-1 md:grid-cols-2 bg-slate-950/70 border-b border-slate-800 text-[10px] font-black text-slate-500 uppercase tracking-widest py-3 px-6">
        <div>🎬 Visual Directions & Camera Cue</div>
        <div class="border-t md:border-t-0 md:border-l border-slate-800 pt-3 md:pt-0 md:pl-6">🎤 Voiceover Narration & Sound FX</div>
      </div>
      
      <div class="divide-y divide-slate-800/80">
        ${scriptRows.map((row, rIdx) => `
          <div class="grid grid-cols-1 md:grid-cols-2 text-xs leading-relaxed p-6 gap-6 hover:bg-slate-800/10 transition-colors">
            <div class="text-slate-400 font-mono italic">
              <span class="text-red-500 font-bold block mb-1 uppercase text-[9px] tracking-wider font-sans">Scene ${rIdx + 1}</span>
              ${parseInline(row.visual || "Default camera sweep across company logos.")}
            </div>
            <div class="border-t md:border-t-0 md:border-l border-slate-800/50 pt-4 md:pt-0 md:pl-6 text-white font-semibold">
              ${parseInline(row.audio || "Voiceover: Details forthcoming in the prospectus.")}
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  </div>
</body>
</html>
    `;
  }

  // Unique Layout 5: SOCIAL_MEDIA (Mocked Platform Posts)
  if (contentType === "SOCIAL_MEDIA") {
    // Segment content into LinkedIn vs Twitter
    const tweetBlocks = contentText.split(/(?=\d+\/|\d+\.|\d+\s*-\s*Tweet)/i).filter(Boolean);
    const linkedInBody = lines.find(l => l.trim().length > 100 && !l.trim().startsWith("#") && !l.trim().startsWith("-")) || "Exciting announcement! Nitin Sharma, founder promoters of ABC Industries, finalized the Draft Red Herring Prospectus for the upcoming fresh capital issue.";

    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title} | ${cleanName}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B1220] text-slate-200 py-10 px-6 font-sans">
  <div class="max-w-2xl mx-auto space-y-12">
    <!-- Section Header -->
    <div class="text-center">
      <span class="text-[9px] bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full font-black tracking-widest uppercase">Social Media Campaign Pack</span>
      <h1 class="text-2xl font-black text-white mt-3 uppercase tracking-wider">${cleanName} Announcement</h1>
    </div>

    <!-- LinkedIn Mock Card -->
    <div class="bg-[#151E2D] border border-slate-800 rounded-xl p-5 shadow-2xl space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-black uppercase text-sm">${cleanName.slice(0,1)}</div>
          <div>
            <h3 class="text-sm font-bold text-white">${cleanName} Investor Relations</h3>
            <p class="text-[9px] text-slate-500 uppercase font-semibold">Promoted • Compliance Approved</p>
          </div>
        </div>
        <span class="text-[10px] text-blue-400 font-bold bg-blue-500/10 px-2.5 py-0.5 rounded border border-blue-500/10 uppercase">LinkedIn</span>
      </div>
      <p class="text-xs text-slate-350 leading-relaxed">${parseInline(linkedInBody)}</p>
      <div class="border-t border-slate-800 pt-3 flex justify-between text-[10px] text-slate-500 font-bold uppercase tracking-wider">
        <span>👍 342 Likes</span>
        <span>💬 12 Comments</span>
        <span>↗ 28 Shares</span>
      </div>
    </div>

    <!-- Twitter Thread Mock Sequence -->
    <div class="space-y-4 relative">
      <h2 class="text-xs font-black text-slate-500 uppercase tracking-widest mb-4">Twitter / X Thread Campaign</h2>
      
      <!-- Thread connector line -->
      <div class="absolute left-9 top-16 bottom-10 w-[2px] bg-slate-800/80 z-0"></div>

      ${tweetBlocks.slice(0, 3).map((tweet, tIdx) => `
        <div class="bg-[#151E2D] border border-slate-800 rounded-xl p-5 shadow-lg relative z-10 flex space-x-4">
          <div class="w-8 h-8 rounded-full bg-slate-900 border border-slate-800 text-white flex items-center justify-center font-bold uppercase text-xs flex-shrink-0">${cleanName.slice(0,1)}</div>
          <div class="flex-1 space-y-2">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-1.5">
                <span class="text-xs font-bold text-white">${cleanName}</span>
                <span class="text-[10px] text-slate-500">@${cleanName.toLowerCase()}_ir • ${tIdx + 1}t</span>
              </div>
              <span class="text-[8px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-black">X Thread</span>
            </div>
            <p class="text-xs text-slate-300 leading-relaxed">${parseInline(tweet.replace(/^\d+[\/\.]\s*/, ""))}</p>
            <div class="flex justify-between text-[9px] text-slate-500 font-bold uppercase pt-1 max-w-[280px]">
              <span>💬 4</span>
              <span>🔁 12</span>
              <span>♥ 89</span>
            </div>
          </div>
        </div>
      `).join("")}
    </div>
  </div>
</body>
</html>
    `;
  }

  // Unique Layout 6: FAQ (Interactive browser accordion)
  if (contentType === "FAQ") {
    // Attempt to extract Q&A sets
    const qaPairs = [];
    let curQ = "";
    let curA = "";
    
    for (let line of lines) {
      const trimLine = line.trim();
      if (trimLine.toLowerCase().startsWith("q:") || trimLine.toLowerCase().startsWith("question:") || trimLine.startsWith("**Q:")) {
        if (curQ && curA) {
          qaPairs.push({ q: curQ, a: curA });
          curQ = ""; curA = "";
        }
        curQ = trimLine.replace(/^(Q:|Question:|\*\*Q:)\s*/i, "").replace(/\*\*$/g, "");
      } else if (trimLine.toLowerCase().startsWith("a:") || trimLine.toLowerCase().startsWith("answer:") || trimLine.startsWith("**A:")) {
        curA = trimLine.replace(/^(A:|Answer:|\*\*A:)\s*/i, "").replace(/\*\*$/g, "");
      } else if (trimLine.length > 10) {
        if (curQ && !curA) {
          curA = trimLine;
        }
      }
    }
    if (curQ && curA) {
      qaPairs.push({ q: curQ, a: curA });
    }

    // Fallback Q&As if parse fails
    if (qaPairs.length === 0) {
      qaPairs.push(
        { q: "What is the aggregate target size of the fresh issue?", a: "The fresh issue size comprises exactly 400 Crores, allocated to working capital items and loan repayments." },
        { q: "Who are the designated promoter nodes?", a: "The promoter nodes of the company are Nitin Sharma and Sharma Capital Group." },
        { q: "What are the primary objects of the capital allocations?", a: "Capital is allocated primarily to funding working capital objects (200 Crores) and outstanding debt repayment (150 Crores)." }
      );
    }

    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title} | ${cleanName}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    details summary::-webkit-details-marker { display: none; }
    details[open] summary svg { transform: rotate(180deg); }
  </style>
</head>
<body class="bg-[#0B1220] text-slate-200 py-10 px-6 font-sans">
  <div class="max-w-3xl mx-auto space-y-6">
    <div class="text-center mb-8">
      <span class="text-[9px] bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full font-black tracking-widest uppercase">Investor FAQ & Disclosure</span>
      <h1 class="text-2xl font-black text-white mt-2 uppercase tracking-wider">${cleanName} LIMITED</h1>
    </div>

    <!-- Interactive details accordion -->
    <div class="space-y-4">
      ${qaPairs.map((qa, idx) => `
        <details class="bg-[#151E2D] border border-slate-800 rounded-xl overflow-hidden shadow-lg group">
          <summary class="flex justify-between items-center p-5 cursor-pointer hover:bg-slate-800/20 transition-all select-none">
            <div class="flex items-start space-x-3">
              <span class="text-blue-500 font-bold text-xs bg-blue-500/10 px-2 py-0.5 rounded uppercase mt-0.5">Q${idx + 1}</span>
              <span class="text-sm font-bold text-white">${parseInline(qa.q)}</span>
            </div>
            <svg class="w-4 h-4 text-slate-450 transition-transform duration-200 flex-shrink-0 ml-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7" />
            </svg>
          </summary>
          <div class="px-5 pb-5 pt-1 border-t border-slate-800/40 text-xs text-slate-400 leading-relaxed bg-slate-900/30">
            ${parseInline(qa.a)}
          </div>
        </details>
      `).join("")}
    </div>
  </div>
</body>
</html>
    `;
  }

  // Unique Layout 7: IMAGE_PROMPTS (Art Gallery prompts)
  if (contentType === "IMAGE_PROMPTS") {
    const promptCards = lines.filter(l => l.trim().length > 15 && (l.toLowerCase().includes("prompt") || l.startsWith("-") || l.startsWith("1.") || l.startsWith("2.") || l.startsWith("3.") || l.startsWith("4.") || l.startsWith("5.")));
    const gradients = [
      "from-blue-600 to-indigo-700",
      "from-indigo-600 to-purple-700",
      "from-purple-600 to-pink-700",
      "from-pink-600 to-rose-700",
      "from-teal-600 to-emerald-700"
    ];

    return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title} | ${cleanName}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B1220] text-slate-200 py-10 px-6 font-sans">
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="text-center mb-8">
      <span class="text-[9px] bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full font-black tracking-widest uppercase">Generative Design Artboard</span>
      <h1 class="text-2xl font-black text-white mt-2 uppercase tracking-wider">${cleanName} Cover Sheet Prompts</h1>
    </div>

    <!-- Art prompts grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      ${promptCards.slice(0, 5).map((prompt, pIdx) => {
        const grad = gradients[pIdx % gradients.length];
        return `
          <div class="bg-[#151E2D] border border-slate-800 rounded-2xl overflow-hidden shadow-xl flex flex-col justify-between">
            <!-- Simulated Graphic Image Placeholder -->
            <div class="h-32 bg-gradient-to-tr ${grad} relative flex items-center justify-center font-black text-white/30 text-4xl tracking-widest uppercase">
              ARTBOARD ${pIdx + 1}
            </div>
            
            <!-- Description -->
            <div class="p-5 flex-1 flex flex-col justify-between">
              <div>
                <span class="text-[9px] font-bold text-slate-500 uppercase tracking-wide">Midjourney / DALL-E Prompt</span>
                <p class="text-xs text-slate-300 font-mono mt-2 bg-slate-900 border border-slate-850 p-3 rounded-lg leading-relaxed select-all">
                  "${parseInline(prompt.replace(/^\d+[\.\/\-]*\s*(Prompt\s*\d+:\s*)*/i, ""))}"
                </p>
              </div>
              <button class="w-full mt-4 bg-slate-800 hover:bg-slate-750 text-white font-bold py-1.5 rounded-lg text-[10px] uppercase border border-slate-750 transition-colors" onclick="navigator.clipboard.writeText(this.previousElementSibling.querySelector('p').innerText)">
                📋 Copy Prompt Copy
              </button>
            </div>
          </div>
        `;
      }).join("")}
    </div>
  </div>
</body>
</html>
    `;
  }

  // Unique Layout 8: EXECUTIVE_SUMMARY (Dossier Abstract)
  // Reverts to a formal two-column printed briefing template
  let htmlBody = "";
  let inList = false;
  let inTable = false;
  
  for (let line of lines) {
    line = line.trim();
    if (line.startsWith("# ")) {
      if (inList) { htmlBody += "</ul>"; inList = false; }
      if (inTable) { htmlBody += "</tbody></table></div>"; inTable = false; }
      htmlBody += `<h1 class="text-2xl font-black text-white border-b border-slate-800 pb-2.5 mt-8 mb-4 uppercase tracking-wider">${line.replace("# ", "")}</h1>`;
    } else if (line.startsWith("## ")) {
      if (inList) { htmlBody += "</ul>"; inList = false; }
      if (inTable) { htmlBody += "</tbody></table></div>"; inTable = false; }
      htmlBody += `<h2 class="text-base font-extrabold text-blue-400 mt-6 mb-3 uppercase tracking-wide">${line.replace("## ", "")}</h2>`;
    } else if (line.startsWith("### ")) {
      if (inList) { htmlBody += "</ul>"; inList = false; }
      if (inTable) { htmlBody += "</tbody></table></div>"; inTable = false; }
      htmlBody += `<h3 class="text-sm font-bold text-slate-200 mt-4 mb-2">${line.replace("### ", "")}</h3>`;
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      if (inTable) { htmlBody += "</tbody></table></div>"; inTable = false; }
      if (!inList) { htmlBody += `<ul class="list-disc pl-5 space-y-1.5 my-3 text-slate-350 text-xs">`; inList = true; }
      htmlBody += `<li>${line.slice(2)}</li>`;
    } else if (line.startsWith("|")) {
      if (inList) { htmlBody += "</ul>"; inList = false; }
      const cols = line.split("|").map(c => c.trim()).filter(Boolean);
      if (cols.length === 0 || line.includes("---")) continue;
      if (!inTable) {
        htmlBody += `<div class="overflow-x-auto my-4 border border-slate-800 rounded-xl"><table class="w-full text-left border-collapse"><thead class="bg-slate-900 text-[10px] font-semibold text-slate-400 uppercase tracking-wider"><tr><th class="px-5 py-2">Parameter</th><th class="px-5 py-2">Details</th></tr></thead><tbody class="divide-y divide-slate-800 text-xs text-slate-350">`;
        inTable = true;
      }
      htmlBody += `<tr class="hover:bg-slate-800/20 transition-colors"><td class="px-5 py-3 font-semibold text-slate-400">${cols[0]}</td><td class="px-5 py-3 font-mono text-white">${cols[1] || "-"}</td></tr>`;
    } else if (line === "") {
      if (inList) { htmlBody += "</ul>"; inList = false; }
      if (inTable) { htmlBody += "</tbody></table></div>"; inTable = false; }
    } else {
      if (inList) { htmlBody += "</ul>"; inList = false; }
      if (inTable) { htmlBody += "</tbody></table></div>"; inTable = false; }
      htmlBody += `<p class="text-slate-350 leading-relaxed mb-3 text-xs">${line}</p>`;
    }
  }
  if (inList) htmlBody += "</ul>";
  if (inTable) htmlBody += "</tbody></table></div>";

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title} | ${cleanName}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B1220] text-slate-200 py-10 px-6 font-sans">
  <main class="max-w-4xl w-full mx-auto">
    <!-- Executive Cover Box -->
    <div class="bg-[#151E2D] border border-slate-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden mb-6">
      <div class="absolute top-0 left-0 right-0 h-1 bg-blue-500"></div>
      <div class="flex justify-between items-start">
        <div>
          <span class="text-[9px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2.5 py-0.5 rounded font-black tracking-widest uppercase">Executive Briefing Summary</span>
          <h1 class="text-2xl font-black text-white mt-3 uppercase tracking-tight">${cleanName} LIMITED</h1>
          <p class="text-xs text-slate-400 mt-1">Unified corporate overview and objects analysis dossier.</p>
        </div>
        <div class="text-right text-[10px] text-slate-500 uppercase font-black tracking-wider">SEBI DRHP OS V1</div>
      </div>
    </div>

    <!-- Brief Body -->
    <article class="bg-[#151E2D] border border-slate-800 rounded-2xl p-8 shadow-xl">
      ${htmlBody}
    </article>
  </main>
</body>
</html>
  `;
};

export const TransformationPage = () => {
  const { workspaceId, workspaceName, workspaceStatus } = useWorkspace();
  const [transformedItems, setTransformedItems] = useState([]);
  const [selectedPreview, setSelectedPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeType, setActiveType] = useState("");

  const fetchTransformedList = async () => {
    if (!workspaceId) return;
    try {
      const res = await axios.get(`/api/transformations/${workspaceId}`);
      setTransformedItems(res.data.transformed_content || []);
    } catch (err) {
      console.warn("Could not query transformation inventory.", err);
    }
  };

  useEffect(() => {
    fetchTransformedList();
  }, [workspaceId, workspaceStatus]);

  const handleGenerate = async (type) => {
    setLoading(true);
    setActiveType(type);
    try {
      await axios.post(`/api/transformations/${workspaceId}/run`);
      await fetchTransformedList();
      handlePreview(type);
    } catch (err) {
      console.error("Downstream transformation failed:", err);
    } finally {
      setLoading(false);
      setActiveType("");
    }
  };

  const handlePreview = async (type) => {
    try {
      const res = await axios.get(`/api/transformations/${workspaceId}/${type}`);
      if (res.data) {
        setSelectedPreview({
          title: res.data.title,
          content: res.data.content,
          type: res.data.content_type
        });
      }
    } catch (err) {
      setSelectedPreview({
        title: `${type.replace("_", " ")} Outline`,
        content: `# ${type.replace("_", " ")} Report\n\n*(AI Transformed Media - Pre-generated fallback preview content)*\n\n- ABC Industries Limited IPO summary statistics.\n- Primary objects of issue capitalization details.\n- Promoter holdings structure.`,
        type
      });
    }
  };

  // Triggers browser to open fully styled visual site/brochure directly in a new tab
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
      const mockText = `# ${type.replace("_", " ")} Outline\n\nFallback metrics context.`;
      const html = buildStyledHTML(type, type.replace("_", " "), mockText, workspaceName);
      const blob = new Blob([html], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
    }
  };

  // Downloads high-fidelity compiled files directly from backend (.pptx, .pdf, .html, .zip)
  const handleDownloadDirect = async (type) => {
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
      
      const filename = `${workspaceName.replace(/\s+/g, "_")}_${ext_mapping[type] || "deliverable.bin"}`;
      const blob = new Blob([response.data]);
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Direct download failed:", err);
    }
  };

  const cardsConfig = [
    { type: "EXECUTIVE_SUMMARY", label: "Executive Summary", desc: "A concise 2-page operational and financial prospectus overview." },
    { type: "INVESTOR_BROCHURE", label: "Investor Brochure", desc: "A highly marketing-oriented collateral brochure highlighting strengths." },
    { type: "PPT_PRESENTATION", label: "Presentation Slide deck", desc: "10-slide PowerPoint structure outlining roadshow highlights." },
    { type: "FAQ", label: "Public FAQ", desc: "A complete list of frequently asked investor questions." },
    { type: "WEBSITE_CONTENT", label: "Website Landing Page", desc: "HTML / Copy definitions ready to publish on investor portals." },
    { type: "SOCIAL_MEDIA", label: "Social Media Campaigns", desc: "Announcements tailored for Twitter threads and LinkedIn posts." },
    { type: "IMAGE_PROMPTS", label: "Creative Prompts", desc: "Midjourney and DALL-E prompts to design corporate cover visuals." },
    { type: "VIDEO_SCRIPT", label: "Video Narration Script", desc: "A detailed visual direction script and audio narration text." },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Downstream Transformation</h1>
        <p className="text-gray-400 mt-1">Generate multi-channel marketing collaterals and presentations directly from the approved DRHP.</p>
      </div>

      {/* Grid of 8 transformation cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {cardsConfig.map((card, idx) => {
          const generatedItem = transformedItems.find(item => item.content_type === card.type);
          const isGeneratingThis = loading && activeType === card.type;
          
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.04 }}
              className="bg-darkCard border border-gray-800/80 rounded-xl p-5 flex flex-col justify-between hover:border-gray-700/80 transition-all shadow-xl min-h-[220px]"
            >
              <div>
                <div className="flex justify-between items-start">
                  <span className="text-[10px] uppercase font-bold text-gray-500 tracking-wider">Transformation</span>
                  {generatedItem && (
                    <span className="text-[9px] bg-green-500/10 text-green-500 border border-green-500/20 px-2 py-0.5 rounded font-bold uppercase flex items-center space-x-1">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Ready</span>
                    </span>
                  )}
                </div>
                <h3 className="text-base font-bold text-white mt-3">{card.label}</h3>
                <p className="text-xs text-gray-400 mt-2 line-clamp-3">{card.desc}</p>
              </div>

              {/* Action buttons */}
              <div className="flex items-center justify-between gap-2 mt-6 pt-3 border-t border-gray-800/85">
                <button
                  onClick={() => handleGenerate(card.type)}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center space-x-1.5 bg-gray-800 hover:bg-gray-750 text-xs font-semibold py-2 rounded-lg text-gray-300 hover:text-white border border-gray-750 transition-colors disabled:opacity-50"
                >
                  <Play className={`w-3.5 h-3.5 ${isGeneratingThis ? "animate-spin" : ""}`} />
                  <span>{isGeneratingThis ? "Generating..." : "Generate"}</span>
                </button>

                {generatedItem && (
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => handleViewLive(card.type)}
                      className="p-2 bg-darkBg border border-gray-850 hover:bg-gray-800 text-gray-400 hover:text-white rounded-lg transition-colors"
                      title="View Live Web Output"
                    >
                      <Monitor className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handlePreview(card.type)}
                      className="p-2 bg-darkBg border border-gray-850 hover:bg-gray-800 text-gray-400 hover:text-white rounded-lg transition-colors"
                      title="Preview Source Markdown"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDownloadDirect(card.type)}
                      className="p-2 bg-darkBg border border-gray-850 hover:bg-gray-800 text-gray-400 hover:text-white rounded-lg transition-colors"
                      title="Download Asset"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Preview Dialog Modal */}
      {selectedPreview && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-darkCard border border-gray-800 rounded-xl max-w-2xl w-full overflow-hidden shadow-2xl flex flex-col max-h-[85vh]"
          >
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-800 flex justify-between items-center bg-darkBg/30 flex-shrink-0">
              <div>
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Format Source Markdown</span>
                <h2 className="text-lg font-bold text-white mt-0.5">{selectedPreview.title}</h2>
              </div>
              <button 
                onClick={() => setSelectedPreview(null)}
                className="text-gray-400 hover:text-white text-lg font-bold"
              >
                &times;
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 p-6 overflow-y-auto min-h-0 bg-darkBg/20">
              <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap leading-relaxed break-words bg-darkBg/60 border border-gray-850 p-4 rounded-lg">
                {selectedPreview.content}
              </pre>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-gray-800 flex justify-between items-center bg-darkBg/10 flex-shrink-0">
              <button
                onClick={() => setSelectedPreview(null)}
                className="text-xs font-semibold text-gray-400 hover:text-white"
              >
                Cancel view
              </button>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => {
                    const html = buildStyledHTML(selectedPreview.type, selectedPreview.title, selectedPreview.content, workspaceName);
                    const blob = new Blob([html], { type: "text/html" });
                    const url = URL.createObjectURL(blob);
                    window.open(url, "_blank");
                  }}
                  className="flex items-center space-x-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white font-semibold px-4 py-2 rounded-lg border border-gray-700 transition-colors text-xs"
                >
                  <Monitor className="w-4 h-4" />
                  <span>View Live Web</span>
                </button>
                <button
                  onClick={() => handleDownloadDirect(selectedPreview.type)}
                  className="flex items-center space-x-1.5 bg-primaryAccent hover:bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors text-xs"
                >
                  <Download className="w-4 h-4" />
                  <span>Download File Asset</span>
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};
export default TransformationPage;
