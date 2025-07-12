import json
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load dataset
with open("munros.json") as f:
    munros = json.load(f)

# Create documents with metadata
documents = []
for m in munros:
    content = f"{m['name']} — {m['summary']}\n\n{m['description']}"
    metadata = {
        "name": m["name"],
        "distance": m["distance"],
        "time": m["time"],
        "grade": m["grade"],
        "bog": m["bog"],
        "start": m["start"],
        "url": m["url"],
    }
    documents.append(Document(page_content=content, metadata=metadata))

# Optional: split longer texts
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = splitter.split_documents(documents)

# Create and save FAISS vector store
embeddings = OpenAIEmbeddings()  # or HuggingFaceEmbeddings(...)
vectorstore = FAISS.from_documents(split_docs, embeddings)
vectorstore.save_local("munro_faiss_index")
