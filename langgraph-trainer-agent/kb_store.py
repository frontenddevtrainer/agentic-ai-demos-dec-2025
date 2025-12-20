from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

@dataclass
class KBIngestConfig:
    kb_dir: str
    vectorstore_dir: str
    chunk_size: int
    chunk_overlap: int


# Add Documents
def load_kb_documents(kb_dir: str) -> list[Document]:
    docs: list[Document] = []
    base = Path(kb_dir)
    if not base.exists():
        raise RuntimeError(f"KB directory not found: {kb_dir}")

    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": str(path)}))
    return docs

# Create Vector Store
def build_vectorstore(
    documents: Iterable[Document],
    embeddings,
    config: KBIngestConfig,
) -> FAISS:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )
    chunks = splitter.split_documents(list(documents))

    if not chunks:
        raise RuntimeError("No KB chunks found; add documents to the KB directory")

    vectorstore = FAISS.from_documents(chunks, embeddings)
    Path(config.vectorstore_dir).mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(config.vectorstore_dir)
    return vectorstore

# Read Vector DB
def load_vectorstore(vectorstore_dir: str, embeddings) -> FAISS:
    path = Path(vectorstore_dir)
    if not path.exists():
        raise RuntimeError(
            "Vectorstore not found. Run ingest_kb.py to build it before starting the bot."
        )
    return FAISS.load_local(
        vectorstore_dir, embeddings, allow_dangerous_deserialization=True
    )