import os
from qdrant_client import QdrantClient
from fastembed import TextEmbedding

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "corporate_policies"

# Initialize a global client to reuse connections
try:
    try:
        client = QdrantClient(url=QDRANT_URL)
        client.get_collections()
    except Exception as e:
        print(f"Server unavailable ({e}), falling back to local file-based Qdrant...")
        client = QdrantClient(path=os.path.join(os.path.dirname(__file__), "qdrant_db"))
        
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
except Exception as e:
    client = None
    print(f"Failed to initialize QdrantClient in retriever: {e}")

def search_policies(query: str, customer_id: str = None, document_type: str = None, limit: int = 2) -> list[str]:
    """
    Searches the Qdrant database for corporate policies matching the query and metadata filters.
    Returns a list of markdown chunks.
    """
    if not client:
        return ["RAG Error: Qdrant client not initialized."]
        
    try:
        try:
            client.get_collection(COLLECTION_NAME)
        except Exception:
            return ["RAG Error: Collection does not exist. Run ingest.py first."]
            
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        query_vector = list(embedding_model.embed([query]))[0].tolist()
        
        must_conditions = []
        if customer_id:
            must_conditions.append(FieldCondition(key="customer_id", match=MatchValue(value=customer_id)))
        if document_type:
            must_conditions.append(FieldCondition(key="document_type", match=MatchValue(value=document_type)))
            
        qdrant_filter = Filter(must=must_conditions) if must_conditions else None
        
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=qdrant_filter,
            limit=limit
        ).points
        
        # Format the result clearly for the agent
        formatted_results = []
        for res in results:
            doc_type = res.payload.get("document_type", "policy")
            source = res.payload.get("source", "unknown")
            text = res.payload.get("text", "")
            
            header = f"[{doc_type.upper()}] Source: {source}"
            if "customer_id" in res.payload:
                header += f" (Customer: {res.payload['customer_id']})"
                
            formatted_results.append(f"{header}\n{text}\n")
            
        return formatted_results
        
    except Exception as e:
        return [f"RAG Error during search: {str(e)}"]

def search_historical_decisions(query: str, limit: int = 3) -> list[str]:
    if not client: return []
    try:
        try:
            client.get_collection("historical_decisions")
        except: return []
        
        query_vector = list(embedding_model.embed([query]))[0].tolist()
        results = client.query_points(
            collection_name="historical_decisions",
            query=query_vector,
            limit=limit
        ).points
        
        return [f"Past Human Decision [{res.payload.get('resolution')}]:\n{res.payload.get('text', '')}" for res in results]
    except Exception:
        return []

def insert_historical_decision(text: str, resolution: str, hitl_id: str):
    if not client: return
    try:
        import uuid
        from qdrant_client.models import PointStruct, VectorParams, Distance
        
        # Ensure collection exists
        try:
            client.get_collection("historical_decisions")
        except:
            print("Creating historical_decisions collection...")
            client.create_collection(
                collection_name="historical_decisions",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            
        vector = list(embedding_model.embed([text]))[0].tolist()
        client.upsert(
            collection_name="historical_decisions",
            points=[PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": text, "resolution": resolution, "hitl_id": hitl_id}
            )]
        )
    except Exception as e:
        print(f"Failed to insert historical decision: {e}")
