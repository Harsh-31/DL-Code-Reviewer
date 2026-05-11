# DSL Code Reviewer: AI-Powered Code Review Agent for Domain-Specific Languages

An agentic code review system using **Groq**, **LangGraph**, and **FastAPI** that performs multi-stage analysis of domain-specific language (DSL) code including Verilog, SystemVerilog, SQL, CUDA, VHDL and Assembly.

---

## Features

- **Multi-Agent Pipeline** — 4 specialized agents orchestrated via LangGraph StateGraph
- **MCP-Inspired File Tool** — Filesystem reader that auto-detects language from extension
- **Skills System** — Reusable domain-specific review guidelines per language (loaded per request)
- **Adversarial Questioning** — First-principles challenges to code assumptions
- **Rubber Duck Explainer** — Step-by-step plain-English walkthrough of what code actually does
- **Rate Limit Handling** — Token budget tracking with rolling-window request throttle
- **FastAPI REST API** — Clean endpoints for inline code or file-path review
- **Docker Ready** — `docker-compose up` deploys in one command

---

## Supported Languages

| Language | Extensions |
|---|---|
| Verilog / SystemVerilog | `.v`, `.sv`, `.vh`, `.svh` |
| SQL | `.sql` |
| CUDA | `.cu`, `.cuh` |
| VHDL | `.vhd`, `.vhdl` |
| Assembly | `.asm`, `.s` |
| MATLAB | `.m` |

---

## Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/YOUR_USERNAME/dsl-code-reviewer
cd dsl-code-reviewer
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

### 2a. Run with Docker (recommended)
```bash
docker-compose up --build
```

### 2b. Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API is now live at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

---

## Usage

### Review inline code
```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "always @(posedge clk) count = count + 1;",
    "language": "verilog"
  }'
```

### Review a file
```bash
curl -X POST http://localhost:8000/review/file \
  -H "Content-Type: application/json" \
  -d '{"file_path": "samples/sample.v"}'
```

### Check rate limit usage
```bash
curl http://localhost:8000/rate-limit/usage
```

---

## Sample Response

```json
{
  "language": "verilog",
  "quality_score": 42,
  "executive_summary": "The counter module has critical issues: blocking assignments in a sequential block will cause simulation/synthesis mismatch, and the mixed assignment style introduces race conditions...",
  "syntax_issues": [
    {
      "line": 15,
      "severity": "error",
      "message": "Blocking assignment (=) used in sequential always block",
      "suggestion": "Replace = with <= for all assignments in always @(posedge clk)"
    }
  ],
  "adversarial_questions": [
    {
      "question": "What happens when count reaches 255 — is silent wraparound the intended behavior?",
      "concern": "Unhandled overflow could cause undefined downstream behavior",
      "priority": "high"
    }
  ],
  "explanation": "This module is an 8-bit counter. On every rising clock edge...",
  "remediation": [...],
  "revised_code": "module counter (\n    input clk,\n    ...",
  "final_report": "# DSL Code Review Report\n**Quality Score:** 42/100\n..."
}
```

---

## Project Structure

```
dsl-code-reviewer/
├── main.py                    # FastAPI app + all endpoints
├── agents/
│   ├── orchestrator.py        # LangGraph StateGraph wiring
│   ├── syntax_agent.py        # Lint & syntax analysis node
│   ├── adversarial_agent.py   # First-principles questioning node
│   ├── explainer_agent.py     # Rubber duck explanation node
│   └── remediation_agent.py   # Fix generation + scoring node
├── skills/
│   ├── loader.py              # Maps language → skill file
│   ├── verilog.md             # Verilog/SV review guidelines
│   ├── sql.md                 # SQL review guidelines
│   ├── cuda.md                # CUDA review guidelines
│   ├── vhdl.md                # VHDL review guidelines
│   └── assembly.md            # Assembly review guidelines
├── tools/
│   └── file_reader.py         # MCP-inspired filesystem tool
├── utils/
│   └── rate_limiter.py        # Token budget & rate limiting
├── samples/
│   ├── sample.v               # Verilog with intentional issues
│   ├── sample.sql             # SQL with intentional issues
│   └── sample.cu              # CUDA with intentional issues
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq (`llama-3.3-70b-versatile`) |
| Agent Orchestration | LangGraph `StateGraph` |
| API Framework | FastAPI + Uvicorn |
| Containerization | Docker + Docker Compose |
| Language | Python 3.11+ |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/review` | Review inline code |
| `POST` | `/review/file` | Review file by path (MCP tool) |
| `GET` | `/health` | Health check |
| `GET` | `/supported-languages` | List supported languages |
| `GET` | `/rate-limit/usage` | Current rate limit stats |
| `GET` | `/docs` | Swagger UI |

---
