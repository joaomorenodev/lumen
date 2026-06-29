from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    DirectoryLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"
STORAGE_DIR = PROJECT_ROOT / "storage"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
EMBEDDING_MODEL = "nomic-embed-text"


# Each glob is paired with the loader that knows how to read that format.
# Text formats need an explicit encoding; PDF/DOCX loaders handle bytes themselves.
LOADERS = [
    ("**/*.md", TextLoader, {"encoding": "utf-8"}),
    ("**/*.txt", TextLoader, {"encoding": "utf-8"}),
    ("**/*.pdf", PyPDFLoader, {}),
    ("**/*.docx", Docx2txtLoader, {}),
]


def load_documents():
    """Read every supported file (.md, .txt, .pdf, .docx) inside docs/."""
    documents = []
    for pattern, loader_cls, loader_kwargs in LOADERS:
        loader = DirectoryLoader(
            str(DOCS_DIR),
            glob=pattern,
            loader_cls=loader_cls,
            loader_kwargs=loader_kwargs,
        )
        documents.extend(loader.load())
    return documents


def split_documents(documents):
    """Break the documents into smaller overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(documents)


def index_documents(chunks):
    """Embed each chunk and persist it into the Chroma vector store."""
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(STORAGE_DIR),
    )
    return vector_store


def run_ingest():
    """Full offline pipeline: load docs, split into chunks, embed and index."""
    documents = load_documents()
    print(f"Loaded {len(documents)} document(s) from {DOCS_DIR}")

    chunks = split_documents(documents)
    print(f"Split into {len(chunks)} chunk(s)")

    print(f"\nIndexing {len(chunks)} chunk(s) into Chroma at {STORAGE_DIR} ...")
    index_documents(chunks)
    print("Done. Vector store persisted.")


if __name__ == "__main__":
    run_ingest()
