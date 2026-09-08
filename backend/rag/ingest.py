import os
import glob
import uuid
import yaml
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from fastembed import TextEmbedding

# Config
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "corporate_policies"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "policies")

def extract_frontmatter_and_content(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    metadata = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1]) or {}
                content = parts[2].strip()
            except yaml.YAMLError:
                pass
    
    # Defaults
    if "document_type" not in metadata:
        metadata["document_type"] = "policy"
    
    return metadata, content

def main():
    print(f"Connecting to Qdrant at {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL)
    
    print("Loading embedding model...")
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    print(f"Recreating collection {COLLECTION_NAME}...")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    
    if not client.collection_exists(collection_name="historical_decisions"):
        client.create_collection(
            collection_name="historical_decisions",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        
    md_files = glob.glob(os.path.join(DATA_DIR, "*.md"))
    if not md_files:
        print(f"No markdown files found in {DATA_DIR}")
        return

    docs = []
    for file_path in md_files:
        print(f"Loading {file_path}...")
        metadata, content = extract_frontmatter_and_content(file_path)
        metadata["source"] = os.path.basename(file_path)
        docs.append(Document(page_content=content, metadata=metadata))
        
    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    
    print(f"Split into {len(chunks)} chunks. Embedding and uploading...")
    
    texts = [chunk.page_content for chunk in chunks]
    embeddings = list(embedding_model.embed(texts))
    
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=emb.tolist(),
            payload={"text": chunk.page_content, **chunk.metadata}
        )
        for chunk, emb in zip(chunks, embeddings)
    ]
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    
    print("Ingestion complete!")

if __name__ == "__main__":
    main()
