
import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
TOP_K = int(os.getenv("TOP_K", 5))

DATA_DIR = "data"
DOCS_DIR = os.path.join(DATA_DIR, "docs")
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")
EMBEDDING_DIR = os.path.join(DATA_DIR, "embeddings")
