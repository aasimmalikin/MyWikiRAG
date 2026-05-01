import os
import json
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()  
#LLM Groq
from langchain_groq import ChatGroq
llm = ChatGroq(
    model="openai/gpt-oss-120b",   
    temperature=0
)

INDEX_PATH = "faiss_wikipedia_index"


with open("rag_corpus_nlp.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

print(f"Loaded {len(corpus)} documents from rag_corpus_nlp.json")

documents = []

for items in corpus:
    doc = Document(
        page_content = items['text'],
        metadata = items['metadata']
    )
    documents.append(doc)

print(f"Converted to {len(documents)} LangChain Document objects")

#Choose embedding model

embeddings = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

#Embedding AND Storing

if os.path.exists(INDEX_PATH):
    print(f"Existing index found at {INDEX_PATH}")
    print("Skipping embedding - loading directly from disk")

    vectorstore = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization = True
    )
    print("Vector store loaded successfully\n")

else:
    print(f"No index found at {INDEX_PATH}")
    print(f"Embedding {len(documents)} documents for the first time")

    vectorstore = FAISS.from_documents(
        documents = documents, 
        embedding = embeddings
        
    )
    vectorstore.save_local(INDEX_PATH)
    print(f"Embedding complete")
    print(f" Index saved to {INDEX_PATH}/ will load from disk next time")


#Prompt template 

prompt = PromptTemplate(
    input_variables = ["context", "question"],
    template = """You are a helpful AI assistant specialised in AI and ML topics.
Use ONLY the context below to answer the question.
If the answer is not in the context, say "I don't have enough information."

Context:
{context}

Question: 
{question}

Answer:"""
)

#RAG + LLM Chain

qa_chain = RetrievalQA.from_chain_type(
    llm = llm,
    chain_type = "stuff",
    retriever = vectorstore.as_retriever(search_kwargs = {"k":5}),
    return_source_documents = True,
    chain_type_kwargs = {"prompt": prompt}
)

print("AI/ML knowledge Assistant - type 'exit' to quit")

while True:
    query = input("\n Your question:").strip()
    if not query:
        continue
    if query.lower() in ("exit", "quit"):
        print("Goodbye")
        break
    result = qa_chain.invoke({"query": query})
    print(f"\n Answer: {result['result']}")
    print(f"\n📚 Context Sources:")
    for i, doc in enumerate(result["source_documents"], 1):
        print(f"  [{i}] {doc.metadata.get('title', '—')} "
              f"| {doc.metadata.get('source', '—')}")


