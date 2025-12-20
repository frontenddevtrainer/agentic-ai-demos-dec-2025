from __future__ import annotations

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

from config import load_settings
from kb_store import KBIngestConfig, build_vectorstore, load_kb_documents

# 
def main() -> None: 
    load_dotenv()
    settings = load_settings()

    docs = load_kb_documents(settings.kb_dir)

    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )

    config = KBIngestConfig(
        kb_dir=settings.kb_dir,
        vectorstore_dir=settings.vectorstore_dir,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    build_vectorstore(docs, embeddings, config)

    print(
        f"Vectorstore saved to {settings.vectorstore_dir} with {len(docs)} documents."
    )

if __name__ == "__main__":
    main()


