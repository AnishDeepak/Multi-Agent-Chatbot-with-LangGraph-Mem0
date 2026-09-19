# ingestion.py

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


class DocumentIngestion:

    def __init__(self, folder_path):
        self.folder_path = folder_path
        #self.collection_name = collection_name

        self.embedding_model = OllamaEmbeddings(model="qwen3-embedding:4b")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def load_documents(self):
        loader = DirectoryLoader(
            self.folder_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )

        documents = loader.load()

        print(f"Loaded {len(documents)} documents")

        return documents

    def split_documents(self, documents):
        splits = self.text_splitter.split_documents(documents)

        print(f"Split documents into {len(splits)} chunks")

        return splits

    def create_vectorstore(self, splits):
        vectorstore = Chroma.from_documents(
            collection_name='anish_resume',
            documents=splits,
            embedding=self.embedding_model,
            persist_directory="./chroma_db"
        )

        print("Documents successfully stored in Chroma")

        return vectorstore

    def run(self):
        documents = self.load_documents()

        splits = self.split_documents(documents)

        vectorstore = self.create_vectorstore(splits)

        return vectorstore