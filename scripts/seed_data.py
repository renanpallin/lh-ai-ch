#!/usr/bin/env python3
"""
Seed script to generate sample PDF documents and upload them to DocProc.

Usage:
    pip install reportlab requests
    python seed_data.py

Make sure the backend is running at http://localhost:8000
"""

import os
import tempfile
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

API_URL = os.getenv("API_URL", "http://localhost:8000")

SAMPLE_DOCUMENTS = [
    {
        "filename": "company_handbook.pdf",
        "title": "Company Handbook",
        "tags": ["internal", "hr"],
        "content": [
            "Welcome to Acme Corporation",
            "",
            "Chapter 1: Introduction",
            "This handbook provides guidelines and policies for all employees.",
            "Please read through all sections carefully.",
            "",
            "Chapter 2: Code of Conduct",
            "All employees are expected to maintain professional behavior.",
            "Respect for colleagues and clients is paramount.",
            "",
            "Chapter 3: Benefits",
            "Full-time employees are eligible for health insurance,",
            "401k matching, and paid time off.",
        ],
    },
    {
        "filename": "technical_specification.pdf",
        "title": "Technical Specification",
        "tags": ["technical"],
        "content": [
            "Project: Document Processing System",
            "Version: 1.0",
            "",
            "1. Overview",
            "This system provides document upload and search capabilities.",
            "It uses FastAPI for the backend and React for the frontend.",
            "",
            "2. Architecture",
            "The system follows a microservices architecture with:",
            "- API Gateway",
            "- Document Service",
            "- Search Service",
            "- PostgreSQL Database",
            "",
            "3. API Endpoints",
            "POST /documents - Upload a document",
            "GET /documents - List all documents",
            "GET /search - Search document content",
        ],
    },
    {
        "filename": "meeting_notes_q4.pdf",
        "title": "Q4 Meeting Notes",
        "tags": ["meeting", "internal"],
        "content": [
            "Quarterly Review Meeting",
            "Date: October 15, 2024",
            "",
            "Attendees:",
            "- John Smith (CEO)",
            "- Jane Doe (CTO)",
            "- Bob Wilson (Engineering Lead)",
            "",
            "Discussion Points:",
            "1. Revenue exceeded targets by 15%",
            "2. New product launch scheduled for December",
            "3. Hiring plan for Q1 approved",
            "",
            "Action Items:",
            "- Finalize product roadmap by October 30",
            "- Complete security audit by November 15",
            "- Prepare board presentation",
        ],
    },
    {
        "filename": "user_guide.pdf",
        "title": "User Guide",
        "tags": ["manual"],
        "content": [
            "DocProc User Guide",
            "",
            "Getting Started",
            "1. Navigate to the application at http://localhost:5173",
            "2. You will see the main dashboard with upload form",
            "",
            "Uploading Documents",
            "1. Click the file input to select a PDF",
            "2. Click Upload to submit the document",
            "3. The document will be processed and appear in the list",
            "",
            "Searching",
            "1. Enter your search query in the search bar",
            "2. Click Search to find matching documents",
            "3. Click on a result to view the full document",
            "",
            "Viewing Documents",
            "Click on any document in the list to see its details",
            "including the extracted text content.",
        ],
    },
    {
        "filename": "security_policy.pdf",
        "title": "Security Policy",
        "tags": [],  # No tags for testing
        "content": [
            "Information Security Policy",
            "Effective Date: January 1, 2024",
            "",
            "1. Purpose",
            "This policy establishes security requirements",
            "for all company systems and data.",
            "",
            "2. Password Requirements",
            "- Minimum 12 characters",
            "- Must include uppercase, lowercase, numbers",
            "- Change every 90 days",
            "",
            "3. Data Classification",
            "- Public: Marketing materials",
            "- Internal: Company documents",
            "- Confidential: Customer data, financial records",
            "",
            "4. Incident Response",
            "Report security incidents immediately to IT.",
            "Do not attempt to investigate on your own.",
        ],
    },
]


def create_pdf(filename: str, title: str, content: list[str]) -> str:
    """Create a PDF file with the given content."""
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(1 * inch, height - 1 * inch, title)

    # Content
    c.setFont("Helvetica", 12)
    y_position = height - 1.5 * inch

    for line in content:
        if y_position < 1 * inch:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 1 * inch

        c.drawString(1 * inch, y_position, line)
        y_position -= 0.3 * inch

    c.save()
    return filepath


def upload_document(filepath: str, tags: list[str] = None) -> dict:
    """Upload a PDF to the API with optional tags."""
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f, "application/pdf")}
        data = {}
        if tags:
            data = [("tags", tag) for tag in tags]
        response = requests.post(f"{API_URL}/documents", files=files, data=data)
        response.raise_for_status()
        return response.json()


def main():
    print(f"Seeding documents to {API_URL}")
    print("-" * 40)

    for doc in SAMPLE_DOCUMENTS:
        print(f"Creating {doc['filename']}...")
        filepath = create_pdf(doc["filename"], doc["title"], doc["content"])

        tags = doc.get("tags", [])
        tags_str = f" (tags: {', '.join(tags)})" if tags else " (no tags)"
        print(f"Uploading {doc['filename']}{tags_str}...")
        result = upload_document(filepath, tags)
        print(f"  Created document ID: {result['id']}")

        os.remove(filepath)

    print("-" * 40)
    print(f"Successfully seeded {len(SAMPLE_DOCUMENTS)} documents")


if __name__ == "__main__":
    main()
