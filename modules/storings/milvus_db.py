import pickle
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection

# Step 1: Load chunks.pkl
with open("../../chunks.pkl", "rb") as f:
    documents = pickle.load(f)

# Step 2: Initialize embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Step 3: Extract text and metadata, and generate embeddings
texts = [doc.page_content for doc in documents]
metadatas = [doc.metadata for doc in documents]  # Metadata for each document
embeddings = model.encode(texts)

# Step 4: Connect to Milvus
connections.connect(alias="default", host="localhost", port="19530")

# Step 5: Define schema and create collection
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=len(embeddings[0])),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=500),
    FieldSchema(name="metadata", dtype=DataType.JSON),
]
schema = CollectionSchema(fields, "Collection for LangChain documents")
collection_name = "langchain_documents"
collection = Collection(name=collection_name, schema=schema)

# Step 6: Insert data into Milvus
data = {
    "embedding": embeddings.tolist(),
    "text": texts,
    "metadata": metadatas,
}
collection.insert(data)

# Step 7: Load collection for searching
collection.load()

# Example Search
search_query = ["example query text"]
search_embeddings = model.encode(search_query).tolist()
search_results = collection.search(
    search_embeddings,
    anns_field="embedding",
    param={"metric_type": "L2", "params": {"nprobe": 10}},
    limit=5,
)

# Display results
for result in search_results[0]:
    print(f"Text: {result.entity.get('text')}, Metadata: {result.entity.get('metadata')}, Distance: {result.distance}")
