"""
utils/rag.py
--------------
Single entry point for FAISS retrieval: `retrieve_context(predicted_attack)`.
Pages never touch FAISS, embeddings, or query construction directly —
those are implementation details owned entirely by this module.

Matches Kareem's real pipeline (5_LLM_Integration.ipynb, section 8):

    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5",
                                        encode_kwargs={"normalize_embeddings": True})
    vector_db = FAISS.load_local("faiss_index", embeddings,
                                  allow_dangerous_deserialization=True)
    results = vector_db.similarity_search(query, k=2, filter={"attack": attack})

EXPECTED ON DISK:
    artifacts/faiss_index/index.faiss
    artifacts/faiss_index/index.pkl
(these are the two files LangChain's FAISS.save_local() produces — just
copy your existing "faiss_index" folder into artifacts/)
"""

from pathlib import Path
import streamlit as st

RAG_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "faiss_index"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
DEFAULT_K = 2


def rag_is_configured() -> bool:
    return (RAG_DIR / "index.faiss").exists() and (RAG_DIR / "index.pkl").exists()


@st.cache_resource
def _load_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        encode_kwargs={"normalize_embeddings": True},
    )


@st.cache_resource
def _load_vector_db():
    from langchain_community.vectorstores import FAISS
    embeddings = _load_embeddings()
    return FAISS.load_local(str(RAG_DIR), embeddings, allow_dangerous_deserialization=True)


def _build_query(predicted_attack: str) -> str:
    """Same retrieval query template used in the notebook."""
    return (
        f"{predicted_attack} attack description, indicators of compromise, "
        f"detection methods, MITRE ATT&CK mapping, "
        f"recommended mitigation, and incident response"
    )


def retrieve_context(predicted_attack: str, k: int = DEFAULT_K) -> list:
    """
    The ONLY function pages/report_generator should call.

    Returns a list of {"title", "content", "score", "attack"} dicts, or an
    empty list if the FAISS index isn't configured yet (never raises for
    that case — the caller shows a setup hint instead).

    Raises RuntimeError on genuine retrieval failures (corrupt index,
    embedding model download failure, etc.) so the caller can show a
    clear st.error() instead of a silent empty result.
    """
    if not rag_is_configured():
        return []

    try:
        vector_db = _load_vector_db()
        query = _build_query(predicted_attack)
        results = vector_db.similarity_search_with_score(
            query, k=k, filter={"attack": predicted_attack}
        )
    except Exception as e:
        raise RuntimeError(f"FAISS retrieval failed: {e}") from e

    docs = []
    for doc, score in results:
        source = doc.metadata.get("source", "Unknown")
        docs.append({
            "title": Path(source).stem if source != "Unknown" else "Knowledge Base Entry",
            "content": doc.page_content,
            "score": float(score),
            "attack": doc.metadata.get("attack", predicted_attack),
        })
    return docs
