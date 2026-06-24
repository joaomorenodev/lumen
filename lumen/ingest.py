from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


def load_documents():
    """Read every .md and .txt file inside the docs/ folder."""
    documents = []
    for pattern in ["**/*.md", "**/*.txt"]:
        loader = DirectoryLoader(
            str(DOCS_DIR),
            glob=pattern,
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
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


if __name__ == "__main__":
    documents = load_documents()
    print(f"Loaded {len(documents)} document(s) from {DOCS_DIR}")

    chunks = split_documents(documents)
    print(f"Split into {len(chunks)} chunk(s)")

    if chunks:
        first = chunks[0]
        print("\n--- First chunk preview ---")
        print("Source:", first.metadata.get("source"))
        print(first.page_content[:300])
