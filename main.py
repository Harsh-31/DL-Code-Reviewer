import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from agents.orchestrator import create_review_graph
from tools.mcp_client import read_file_via_mcp, list_files_via_mcp
from utils.rate_limiter import RateLimiter

load_dotenv()

app = FastAPI(
    title="DSL Code Reviewer",
    description="AI-powered multi-agent code review for domain-specific languages",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

rate_limiter = RateLimiter(requests_per_minute=50, tokens_per_minute=40000)
graph = create_review_graph(llm)


class ReviewRequest(BaseModel):
    code: str
    language: str
    file_path: Optional[str] = "inline"


class FileReviewRequest(BaseModel):
    file_path: str


async def run_review(code: str, language: str, file_path: str) -> dict:
    rate_limiter.wait_if_needed(estimated_tokens=len(code.split()) * 4)
    return await graph.ainvoke({
        "code": code,
        "language": language,
        "file_path": file_path,
        "syntax_issues": [],
        "adversarial_questions": [],
        "explanation": "",
        "remediation": [],
        "quality_score": 0,
        "executive_summary": "",
        "revised_code": "",
        "final_report": "",
    })


@app.post("/review")
async def review_code(request: ReviewRequest):
    """Review an inline code snippet."""
    try:
        return await run_review(request.code, request.language, request.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review/file")
async def review_file(request: FileReviewRequest):
    """
    Review a code file by path.
    File is read via the MCP server (mcp_server.py) over stdio transport
    using the official MCP Python SDK.
    """
    try:
        code, language = await read_file_via_mcp(request.file_path)
        return await run_review(code, language, request.file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_files(directory: str = "samples"):
    """
    List all reviewable DSL files in a directory.
    Uses the MCP server to scan the filesystem.
    """
    try:
        files = await list_files_via_mcp(directory)
        return {"directory": directory, "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy", "model": "claude-sonnet-4-20250514"}


@app.get("/supported-languages")
async def supported_languages():
    return {
        "languages": ["verilog", "systemverilog", "sql", "cuda", "vhdl", "assembly", "matlab"]
    }


@app.get("/rate-limit/usage")
async def rate_limit_usage():
    return rate_limiter.get_usage()
