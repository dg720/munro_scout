from langchain_community.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings


def get_retriever(k=8):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(
        "munro_faiss_index", embeddings, allow_dangerous_deserialization=True
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})
