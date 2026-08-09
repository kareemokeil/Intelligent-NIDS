"""
utils/rag_utils.py
--------------------
FAISS RAG retrieval — matches Kareem's real pipeline exactly
(5_LLM_Integration.ipynb, section 8):

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

import os
from pathlib import Path
import streamlit as st
from huggingface_hub import hf_hub_download

RAG_DIR = Path(__file__).resolve().parent.parent / "artifacts" / "faiss_index"
MODEL_REPO = os.getenv("HF_MODEL_REPO", "KareemOkeil/nids-artifacts")
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"


def ensure_faiss_downloaded():
    ARTIFACTS_DIR = RAG_DIR.parent
    RAG_DIR.mkdir(parents=True, exist_ok=True)
    for fname in ["index.faiss", "index.pkl"]:
        if not (RAG_DIR / fname).exists():
            try:
                hf_hub_download(repo_id=MODEL_REPO, filename=f"faiss_index/{fname}", local_dir=str(ARTIFACTS_DIR))
            except Exception as e:
                pass


def rag_is_configured() -> bool:
    ensure_faiss_downloaded()
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


def retrieve_documents(query_text: str, attack_filter: str = None, k: int = 2):
    """
    Returns a list of {"title", "content", "score", "attack"} dicts, or an
    empty list if the FAISS index isn't configured yet.
    """
    if not rag_is_configured():
        return []

    vector_db = _load_vector_db()
    filter_kwargs = {"attack": attack_filter} if attack_filter else None
    results = vector_db.similarity_search_with_score(query_text, k=k, filter=filter_kwargs)

    docs = []
    for doc, score in results:
        source = doc.metadata.get("source", "Unknown")
        docs.append({
            "title": Path(source).stem if source != "Unknown" else "Knowledge Base Entry",
            "content": doc.page_content,
            "score": float(score),
            "attack": doc.metadata.get("attack", attack_filter or "Unknown"),
        })
    return docs


def build_query_from_prediction(pred_class: str, shap_top_features: list = None) -> str:
    """Same retrieval query template used in the notebook."""
    return (
        f"{pred_class} attack description, indicators of compromise, "
        f"detection methods, MITRE ATT&CK mapping, "
        f"recommended mitigation, and incident response"
    )
