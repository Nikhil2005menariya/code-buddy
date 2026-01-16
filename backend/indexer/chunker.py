from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = []

    for doc in documents:
        splits = splitter.split_text(doc["content"])

        for text in splits:
            chunks.append({
                "text": text,
                "path": doc["path"]
            })

    return chunks
