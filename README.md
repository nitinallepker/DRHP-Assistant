# 🚀 DRHP Assistant

> **Companies can make your DRHP at ease for IPO**

An AI-powered platform that automates the preparation of a **Draft Red Herring Prospectus (DRHP)** by extracting corporate information from uploaded documents, generating SEBI-compliant draft sections, reviewing content using specialized AI agents, improving document quality, transforming the DRHP into multiple marketing assets, and exporting production-ready deliverables.

---

## 🌐 Live Demo

- **Frontend:** <https://drhp-assistant.vercel.app/>
- **Backend API:** <https://drhp-assistant.onrender.com/>

---

# 📖 Overview

Preparing a DRHP for an IPO is a lengthy and documentation-heavy process involving legal, financial, compliance, business, and risk-related information.

**DRHP Assistant** streamlines this workflow using AI by automatically:

- Extracting structured knowledge from uploaded corporate documents
- Building a centralized knowledge repository
- Generating multiple DRHP sections
- Reviewing the document using independent AI reviewer agents
- Applying AI-driven improvements
- Producing downstream marketing assets
- Exporting a complete DRHP and supporting deliverables

---

# ✨ Features

## 📂 Workspace Management
- Upload company document packages (.zip)
- Automatic file classification
- Corporate workspace creation
- File inventory management

## 🧠 Knowledge Extraction
- AI-powered fact extraction
- Structured knowledge repository
- Corporate information indexing
- Categorized fact storage

## 📝 DRHP Generation
Generates major DRHP sections including:

- Cover Page
- Company Overview
- Industry Overview
- Business Overview
- Risk Factors
- IPO Details
- Financial Highlights
- Glossary
- Legal Litigation Declaration

---

## 🤖 AI Compliance Review

Independent reviewer agents audit the generated DRHP.

- Legal Reviewer
- Finance Reviewer
- Business Reviewer
- Risk Reviewer
- Compliance Reviewer
- Language Reviewer
- Consistency Reviewer

---

## ⚡ AI Improvement Engine

- Accept reviewer suggestions
- Automatically revise document sections
- Maintain version history
- Improve draft quality

---

## 🎨 Downstream Transformation

Generate business-ready assets including:

- Executive Summary
- Investor Brochure
- Presentation Deck
- Public FAQ
- Website Landing Page
- Social Media Campaigns
- Creative Prompts
- Video Narration Script

---

## 📤 Export System

Export:

- Complete DRHP PDF
- Marketing Assets
- Downloadable Deliverables

---

# 🏗️ System Workflow

```
Upload ZIP
      │
      ▼
Document Classification
      │
      ▼
Knowledge Extraction
      │
      ▼
Knowledge Repository
      │
      ▼
DRHP Draft Generation
      │
      ▼
AI Review Agents
      │
      ▼
Improvement Engine
      │
      ▼
Transformation Engine
      │
      ▼
Export & Download
```

---

# 🛠️ Tech Stack

## Frontend

- React.js
- Vite
- Tailwind CSS
- Axios
- Framer Motion
- Lucide React

## Backend

- FastAPI
- Python
- SQLAlchemy
- SQLite
- Google Gemini API

## AI Components

- Knowledge Extraction Agent
- DRHP Generation Agents
- Review Agents
- Improvement Engine
- Transformation Engine

---

# 📂 Project Structure

```
DRHP-Assistant
│
├── backend
│   ├── agents
│   ├── api
│   ├── database
│   ├── ingestion
│   ├── orchestrator
│   ├── repository
│   ├── review
│   ├── transformation
│   ├── exports
│   └── services
│
├── frontend
│   ├── src
│   ├── components
│   ├── context
│   └── pages
│
└── README.md
```

---

# 📸 Screenshots

## Dashboard

![Dashboard](/UI.png)

---

## Workspace Upload

![Workspace](/workspace.png)

---

## Knowledge Repository

![Knowledge](/knowledge.png)

---

## DRHP Generation

![DRHP](/DRHPPage.png)

---

## AI Compliance Review

![Review](/Review.png)

---

## AI Improvement Engine

![Improvement](/Imrovement.png)

---

## Transformation Engine

![Transformation](/Transformation.png)

---

## Export Page

![Export](/Export.png)

---

# 🚀 Installation

## Clone

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

---

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# ⚙️ Environment Variables

Create a `.env` file inside the backend directory.

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./storage/drhp_system.db
HOST=127.0.0.1
PORT=8000
```

---

# 🎯 Future Improvements

- RAG-powered corporate knowledge retrieval
- Multi-company workspace support
- Human-in-the-loop editing
- Collaborative review workflow
- Advanced compliance validation
- OCR support for scanned documents
- Digital signatures
- Cloud storage integration
- Multi-language support

---

# 👨‍💻 Author

**Nitin Anand**

GitHub: https://github.com/<YOUR_USERNAME>

---

# 📄 License

This project is intended for educational and research purposes.
