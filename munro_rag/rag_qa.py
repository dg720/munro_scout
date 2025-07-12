from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from retriever import get_retriever
import os

retriever = get_retriever()

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",  # could switch to "map_reduce" or "refine"
    return_source_documents=True,
)

print("🔍 Munro Assistant Ready. Type your question or type 'exit' to quit.\n")

while True:
    query = input("Ask about a Munro: ").strip()
    if query.lower() in {"exit", "quit"}:
        print("👋 Exiting. Goodbye!")
        break

    result = qa_chain(query)
    print("\n🧭 Answer:\n", result["result"])
    print("\n📚 Sources:")
    for doc in result["source_documents"]:
        print(
            "-",
            doc.metadata.get("name", "Unknown"),
            "—",
            doc.metadata.get("url", "No URL"),
        )
