from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

def get_retriever(k=4):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local("munro_faiss_index", embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": k})
