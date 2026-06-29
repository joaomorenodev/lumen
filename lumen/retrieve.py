import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STORAGE_DIR = PROJECT_ROOT / "storage"
EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_K = 4


def load_vector_store():
    """Open the Chroma store persisted during ingestion."""
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(
        persist_directory=str(STORAGE_DIR),
        embedding_function=embeddings,
    )


def retrieve(question, k=DEFAULT_K):
    """Return the k chunks most similar to the question."""
    vector_store = load_vector_store()
    return vector_store.similarity_search(question, k=k)


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How do I authenticate?"
    print(f"Question: {question}\n")

    results = retrieve(question)
    print(f"Retrieved {len(results)} chunk(s):\n")
    for i, doc in enumerate(results, start=1):
        source = doc.metadata.get("source", "?")
        print(f"--- Result {i} (source: {source}) ---")
        print(doc.page_content[:300])
        print()
