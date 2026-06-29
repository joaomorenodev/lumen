import sys
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from lumen.retrieve import retrieve

LLM_MODEL = "llama3.2:3b"

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are Lumen, an assistant that answers questions about technical "
            "documentation.\n"
            "Answer ONLY using the CONTEXT provided below. Do not use any prior "
            "knowledge.\n"
            "Always cite the source file(s) you used, by their path.\n"
            "If the answer is not in the context, say clearly that you could not "
            "find it in the documentation. Do not make anything up.",
        ),
        (
            "human",
            "CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer (with sources):",
        ),
    ]
)


def format_context(docs):
    """Join retrieved chunks into a single context string, tagging each source."""
    blocks = []
    for doc in docs:
        source = doc.metadata.get("source", "?")
        blocks.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n".join(blocks)


def cited_sources(answer_text, docs):
    """Return only the retrieved sources that the answer actually cites.

    Avoids listing every retrieved chunk: a source counts only if its path
    shows up in the generated text. If the model says it found nothing, no
    source is cited and the list comes back empty.
    """
    retrieved = {doc.metadata.get("source", "?") for doc in docs}
    return sorted(s for s in retrieved if s in answer_text)


def answer(question, k=4):
    """Retrieve relevant chunks and generate a grounded answer citing sources."""
    docs = retrieve(question, k=k)
    context = format_context(docs)

    llm = ChatOllama(model=LLM_MODEL, temperature=0)
    chain = PROMPT | llm
    response = chain.invoke({"context": context, "question": question})

    sources = cited_sources(response.content, docs)
    return response.content, sources


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How do I authenticate?"
    print(f"Question: {question}\n")

    text, sources = answer(question)
    print("--- Answer ---")
    print(text)
    print("\n--- Sources ---")
    for source in sources:
        print(f"- {source}")
