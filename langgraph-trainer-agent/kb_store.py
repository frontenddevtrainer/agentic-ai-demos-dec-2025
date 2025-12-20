from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

@dataclass
class KBIngestConfig:
    kb_dir: str
    vectorstore_dir: str
    chunk_size: int
    chunk_overlap: int


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