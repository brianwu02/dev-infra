"""Skill 5: Retrieval-Augmented Generation (RAG)

Demonstrates:
- Loading local documents as context
- Chunking text for context windows
- Answering questions grounded in retrieved documents
- Citation tracking

No vector DB required — uses simple keyword matching for retrieval.
For production, swap in a real embedding + vector search.
"""

import os
import re
import anthropic

client = anthropic.Anthropic()


def load_documents(directory: str) -> list[dict]:
    """Load all .txt and .md files from a directory."""
    docs = []
    if not os.path.isdir(directory):
        return docs
    for fname in sorted(os.listdir(directory)):
        if fname.endswith((".txt", ".md")):
            path = os.path.join(directory, fname)
            with open(path) as f:
                docs.append({"filename": fname, "content": f.read()})
    return docs


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def simple_retrieve(query: str, docs: list[dict], top_k: int = 3) -> list[dict]:
    """Keyword-based retrieval — scores by word overlap. Replace with embeddings for production."""
    query_words = set(re.findall(r'\w+', query.lower()))
    scored = []
    for doc in docs:
        for i, chunk in enumerate(chunk_text(doc["content"])):
            chunk_words = set(re.findall(r'\w+', chunk.lower()))
            score = len(query_words & chunk_words)
            scored.append({"filename": doc["filename"], "chunk_index": i, "text": chunk, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def ask(question: str, context_chunks: list[dict]) -> str:
    """Answer a question using retrieved context."""
    context = "\n\n---\n\n".join(
        f"[Source: {c['filename']}, chunk {c['chunk_index']}]\n{c['text']}"
        for c in context_chunks
    )
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "Answer the question using ONLY the provided context. "
            "Cite sources as [filename]. If the context doesn't contain the answer, say so."
        ),
        messages=[{
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        }],
    )
    return response.content[0].text


def main():
    # Use the parent project's docs as sample documents
    doc_dir = os.path.join(os.path.dirname(__file__), "..", "..", ".")
    docs = load_documents(doc_dir)

    if not docs:
        print("No documents found. Create some .txt or .md files to query against.")
        print("Example: echo 'Docker uses namespaces for isolation.' > docs/docker.txt")
        return

    print(f"Loaded {len(docs)} document(s): {[d['filename'] for d in docs]}\n")

    question = "What services are included and what ports do they use?"
    print(f"Q: {question}\n")

    chunks = simple_retrieve(question, docs)
    print(f"Retrieved {len(chunks)} chunks\n")

    answer = ask(question, chunks)
    print(f"A: {answer}")


if __name__ == "__main__":
    main()
