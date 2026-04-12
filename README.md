# Eenera – AI-Powered Workflow Audit System

Eenera is a full-stack workflow audit application that analyzes business documents (PDF/DOCX) using AI to extract workflow steps, identify inefficiencies, calculate financial impact, and generate actionable markdown reports.

## Architecture

- **Backend:** FastAPI (Python 3.11), asynchronous execution, background task polling.
- **Frontend:** Next.js 14, React, Tailwind CSS, Framer Motion processing animations, Glassmorphism UI.
- **AI Engine:** Support for OpenAI & Gemini (lazy loaded), modular chunk-based extraction, and LLM-powered inefficiency analysis.

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Navigate to the project root
cd EENERAEIS-APR

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # macOS / Linux

# Install dependencies needed for PDF, DOCX, and LLM services
pip install -r requirements.txt

# Set your API keys (Default uses OpenAI)
export OPENAI_API_KEY="sk-your-key-here"
# Optional: export LLM_PROVIDER="gemini" and GEMINI_API_KEY="..."

# Run the server on port 8000
uvicorn app.main:app --reload --port 8000
```
Backend will be available at: **http://localhost:8000**  
Swagger UI Docs: **http://localhost:8000/docs**


### 2. Frontend Setup

```bash
# Open a new terminal window
cd EENERAEIS-APR/frontend

# Install node modules
npm install

# Run the Next.js development server
npm run dev -- --port 3000
```
Frontend will be available at: **http://localhost:3000**

---

## 🛠 Project Structure

```
EENERAEIS-APR/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── api/routes.py              # Upload, Status, and Report endpoints
│   ├── models/job.py              # In-memory storage and job state
│   ├── services/
│   │   ├── audit_service.py       # Pipeline orchestration
│   │   ├── extractor.py           # Content extraction from PDF / DOCX
│   │   ├── pipeline.py            # Text chunking logic
│   │   ├── llm_service.py         # AI Provider abstraction
│   │   ├── workflow_analyzer.py   # LLM Chunk analysis & deduplication
│   │   ├── analysis_engine.py     # Inefficiency & cost impact calculations
│   │   └── report_generator.py    # Formatting everything into Markdown
├── frontend/                      # Next.js 14 Application
│   ├── app/
│   │   ├── components/            # UI components (Hero, Navbar, ReportDisplay...)
│   │   ├── page.js                # Main interaction logic (Polling & hooks)
│   │   └── globals.css            # Tailwind & custom CSS variables
└── requirements.txt               # Backend dependencies
```

## ✨ Highlights

* **Resilient LLM Design:** `LLMService` utilizes lazy initialization to avoid hanging on missing dependencies or network configuration on module import.
* **Intelligent Document Chunking:** The pipeline chunks documents on natural boundaries (paragraphs, sentences) to preserve context for the LLM.
* **Cross-Chunk Aggregation:** Extracts steps from every chunk individually and smartly deduplicates findings.
* **Beautiful Frontend:** Premium clean single-page site with smooth upload interactions, staggered visual processing states, and gradient glass cards for the final report.

## 📝 Usage

Drop your workflow document onto the Drag-and-Drop zone on the frontend, optionally enter the estimated hourly cost (e.g. `15.00`), and click "Analyze". 

The UI will progress through extraction, analysis, cost calculation, and report generation, finalizing by displaying dynamic cost savings and downloadable markdown reports.
