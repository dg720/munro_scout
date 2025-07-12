import os
from langchain_community.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings


def get_retriever(k=8):
    """
    Loads the FAISS vector store retriever from disk and returns a retriever object.
    """
    # Resolve full path to the index directory
    index_path = os.path.join(os.path.dirname(__file__), "munro_faiss_index")

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(
        index_path, embeddings, allow_dangerous_deserialization=True
    )

    return vectorstore.as_retriever(search_kwargs={"k": k})
