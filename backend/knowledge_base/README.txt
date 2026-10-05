Put your knowledge base file(s) here - e.g. your_pdf_file.pdf
Supported: PDF, TXT, MD, DOCX, HTML

Then load them into the vector database:
    cd backend
    python scripts/seed_kb.py --reset

(--reset wipes the old knowledge first, so ONLY your file stays in the KB.)

Alternatively, admins can upload files from the Admin Panel in the web UI.
