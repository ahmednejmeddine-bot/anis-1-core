"""
DocumentAgent – Processes, summarises, and generates business documents.
Handles extraction, classification, and structured output from text.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import Any

from services.llm_service import chat, LLMError

SYSTEM_PROMPT = """You are the DocumentAgent for Abdeljelil Group, part of the ANIS-1 Autonomous Neural Intelligence System.

Your mandate is to transform unstructured information into clear, actionable, well-structured documents.

Behavioural guidelines:
- Preserve the original meaning faithfully when summarising or extracting.
- Label inferences clearly – never present them as facts.
- Structure all output for readability: headings, bullets, and concise paragraphs.
- Flag missing, ambiguous, or conflicting information rather than guessing.
- Adapt document style to the audience (executive, technical, operational).

Tone: Clear, structured, neutral.
Scope: Document processing · Summarisation · Data extraction · Report generation."""


class DocumentAgent:
    name = "DocumentAgent"
    description = "AI agent for document processing, summarisation, and structured data extraction."
    capabilities = [
        "document_summarisation",
        "data_extraction",
        "report_generation",
        "document_classification",
        "content_analysis",
    ]

    def __init__(self):
        self.status = "idle"
        self.last_run: datetime | None = None
        self._processed_count = 0

    # ------------------------------------------------------------------
    # AI-powered method
    # ------------------------------------------------------------------

    def ask(self, task_description: str, context: str = "") -> dict[str, Any]:
        """Send a free-form task to OpenAI using the DocumentAgent system prompt."""
        self.status = "active"
        self.last_run = datetime.utcnow()

        user_message = f"Context:\n{context}\n\nTask:\n{task_description}" if context else task_description

        try:
            response = chat(SYSTEM_PROMPT, user_message)
            self.status = "idle"
            return {
                "agent": self.name,
                "task": task_description,
                "timestamp": datetime.utcnow().isoformat(),
                "response": response,
                "model": "gpt-4o",
            }
        except LLMError as exc:
            self.status = "idle"
            return {"agent": self.name, "error": str(exc), "timestamp": datetime.utcnow().isoformat()}

    # ------------------------------------------------------------------
    # Deterministic methods (unchanged)
    # ------------------------------------------------------------------

    def process_document(self, document: dict[str, Any]) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()
        self._processed_count += 1

        text = document.get("content", "")
        word_count = len(text.split())
        doc_type = document.get("type", "unknown")
        classification = self._classify(text, doc_type)

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "process_document",
            "timestamp": datetime.utcnow().isoformat(),
            "document_id": document.get("id", f"DOC-{self._processed_count}"),
            "word_count": word_count,
            "type": doc_type,
            "classification": classification,
            "processed": True,
        }

    def summarise(self, text: str, max_sentences: int = 3) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        summary = ". ".join(sentences[:max_sentences]) + ("." if sentences else "")

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "summarisation",
            "timestamp": datetime.utcnow().isoformat(),
            "original_sentences": len(sentences),
            "summary_sentences": min(max_sentences, len(sentences)),
            "summary": summary,
        }

    def extract_data(self, text: str, fields: list[str]) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()

        extracted: dict[str, str | None] = {}
        lines = text.lower().split("\n")
        for field in fields:
            match = next((line for line in lines if field.lower() in line), None)
            extracted[field] = match.strip() if match else None

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "data_extraction",
            "timestamp": datetime.utcnow().isoformat(),
            "fields_requested": fields,
            "extracted": extracted,
            "extraction_rate_pct": round(sum(1 for v in extracted.values() if v) / max(len(fields), 1) * 100, 1),
        }

    def generate_report(self, template: str = "standard", context: dict[str, Any] | None = None) -> dict[str, Any]:
        self.status = "active"
        self.last_run = datetime.utcnow()
        ctx = context or {}

        sections = {
            "executive_summary": f"Report generated by {self.name} on {datetime.utcnow().date()}.",
            "key_findings": ctx.get("findings", ["No findings provided."]),
            "recommendations": ctx.get("recommendations", ["No recommendations provided."]),
            "next_steps": ctx.get("next_steps", ["Review and distribute report."]),
        }

        self.status = "idle"
        return {
            "agent": self.name,
            "task": "report_generation",
            "timestamp": datetime.utcnow().isoformat(),
            "template": template,
            "report": sections,
        }

    def _classify(self, text: str, doc_type: str) -> str:
        keywords = {
            "financial": ["revenue", "budget", "profit", "loss", "invoice"],
            "legal": ["agreement", "contract", "clause", "liability", "party"],
            "operational": ["process", "workflow", "SLA", "incident", "KPI"],
            "strategic": ["vision", "mission", "goal", "objective", "market"],
        }
        text_lower = text.lower()
        for category, words in keywords.items():
            if any(w in text_lower for w in words):
                return category
        return doc_type if doc_type != "unknown" else "general"

    def get_status(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "documents_processed": self._processed_count,
        }
