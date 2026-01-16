import os

BASE_DIR = os.getcwd()
CHROMA_BASE_DIR = os.path.join(BASE_DIR, "chroma")

os.makedirs(CHROMA_BASE_DIR, exist_ok=True)
