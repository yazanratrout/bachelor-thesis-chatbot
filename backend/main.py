import logging
from sentence_transformers import SentenceTransformer
from source.data_loader.embedding_store import load_vector_store, search_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Loading vector store and embedding model...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    index, chunks = load_vector_store()

    query = "what should I do in case I lost the access chip?"
    results = search_query(query, index, chunks, embedding_model)
    logger.info("Top matching chunks:")
    for i, chunk in enumerate(results):
        print(f"{i + 1}. {chunk}")
