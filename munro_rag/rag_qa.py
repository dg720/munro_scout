from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from retriever import get_retriever

llm = ChatOpenAI(temperature=0, model="gpt-4")  # Use GPT-3.5 if preferred
retriever = get_retriever()

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",  # could switch to "map_reduce" or "refine"
    return_source_documents=True
)

while True:
    query = input("\nAsk about a Munro: ")
    if query.lower() in {"exit", "quit"}:
        break

    result = qa_chain(query)
    print("\nAnswer:\n", result["result"])
    print("\nSources:")
    for doc in result["source_documents"]:
        print("-", doc.metadata["name"], "—", doc.metadata["url"])
