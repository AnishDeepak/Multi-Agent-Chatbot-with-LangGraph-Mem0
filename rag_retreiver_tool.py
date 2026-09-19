
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.tools import tool
from pydantic import BaseModel


embedding_model = OllamaEmbeddings(model="qwen3-embedding:4b")






class RagToolSchema(BaseModel):
    question: str

@tool(args_schema=RagToolSchema)
def retriever_tool(question:str):
   """Tool to Retrieve Semantically Similar documents to answer User Questions related to pdf documents.
   args:
   question (str): User question using which the similarity search happens.   
   """
   print("INSIDE RETRIEVER NODE")
   vectorstore = Chroma(
    collection_name='anish_resume',
    embedding_function=embedding_model,
    persist_directory="./chroma_db"
    )
   retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
   retriever_results = retriever.invoke(question)
   return "\n\n".join(doc.page_content for doc in retriever_results)




