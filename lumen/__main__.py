import argparse

from lumen.generate import answer
from lumen.ingest import run_ingest


def main():
    parser = argparse.ArgumentParser(
        prog="lumen",
        description="Lumen — semantic search over technical documentation (RAG).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Offline flow: (re)build the vector store from docs/.
    subparsers.add_parser("ingest", help="Index the documentation into the vector store.")

    # Online flow: answer a question using the indexed docs.
    ask_parser = subparsers.add_parser("ask", help="Ask a question about the docs.")
    ask_parser.add_argument("question", help="The question to answer.")
    ask_parser.add_argument(
        "-k", type=int, default=4, help="Number of chunks to retrieve (default: 4)."
    )

    args = parser.parse_args()

    if args.command == "ingest":
        run_ingest()
    elif args.command == "ask":
        text, sources = answer(args.question, k=args.k)
        print(text)
        print("\nSources:")
        for source in sources:
            print(f"- {source}")


if __name__ == "__main__":
    main()
