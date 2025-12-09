# nbacontractpredictor

## Retrieval-Augmented LLM Chat
The Streamlit "LLM Chat" page now has two tabs:
- **SQL over Data** keeps the existing natural-language-to-SQL workflow.
- **RAG Knowledge Chat** demonstrates retrieval-augmented generation for product or database documentation questions. A lightweight, Chroma-style in-memory vector store is built from dataset metadata, cap rules, and sample records. The chatbot shows which documents were retrieved (with similarity scores) before composing a contextual answer.

This setup is self-contained for demos and does not require external services—embeddings rely on simple bag-of-words vectors and cosine similarity. Use it to explain how the dashboard works or to surface key salary-cap rules that guide contract and trade analysis.
