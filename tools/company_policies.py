import re
import requests
import numpy as np
import openai
from langchain_core.tools import tool
from langchain_openai.embeddings import OpenAIEmbeddings
from typing import List, Dict
import numpy as np


EMBEDDING_MODEL = "text-embedding-3-small"
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

response = requests.get(
        "https://storage.googleapis.com/benchmarks-artifacts/travel-db/swiss_faq.md"
)
response.raise_for_status()
faq_text = response.text

docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]

class VectorStoreRetriever:
    def __init__(self, docs: list[str], vectors: List, embeddings):
        self._arr = np.array(vectors)
        self._docs = docs
        self._embeddings = embeddings
        
    @classmethod
    def from_docs(cls, docs, embeddings):
        vectors = embeddings.embed_documents([doc["page_content"] for doc in docs])
        return cls(docs, vectors, embeddings)
    
    def query(self, query: str, k: int=5) -> list[dict]:
        embed = self._embeddings.embed_query(query)
        
        # "@" is just a matrix multiplication in python
        scores = np.array(embed) @ self._arr.T
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        return [
            {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
        ]

retriever = VectorStoreRetriever.from_docs(docs, embeddings)

@tool
def lookup_policy(query: str) -> str:
    """
    Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes performing other 'write' events.
    """
    
    docs = retriever.query(query, k=2)
    return "\n\n".join([doc["page_content"] for doc in docs])

