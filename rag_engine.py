import os
import shutil
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_core.documents import Document

class Brain:
    def __init__(self):
        self.db_path = "chroma_db_store"
        print("🧠 BRAIN: Initializing Local Neural Network...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        
        # Logic: Load if exists, else build
        if os.path.exists(self.db_path) and os.listdir(self.db_path):
            print("   -> Loading existing DB from disk...")
            self.vector_store = Chroma(persist_directory=self.db_path, embedding_function=self.embeddings)
        else:
            print("   -> DB not found. Building now...")
            self._build_database()

    def _build_database(self):
        documents = []

        # 1. Load Stores CSV
        if os.path.exists("data/real_stores.csv"):
            print("   -> Ingesting Real Data CSV...")
            loader = CSVLoader(file_path="data/real_stores.csv", source_column="rag_text")
            data = loader.load()
            documents.extend(data)

        # 2. Load Policy TXT
        if os.path.exists("data/store_policy.txt"):
            with open("data/store_policy.txt", "r") as f:
                for line in f:
                    if len(line.strip()) > 5:
                        documents.append(Document(page_content=f"Policy: {line.strip()}", metadata={"source": "policy"}))

        if documents:
            print(f"   -> Vectorizing {len(documents)} items. This may take a minute...")
            self.vector_store = Chroma.from_documents(documents, self.embeddings, persist_directory=self.db_path)
            print("✅ BRAIN: Database built and saved.")
        else:
            print("❌ Error: No data found.")

    def search(self, query):
        if not self.vector_store: return []
        # Fetch 10 candidates to allow strict filtering later
        results = self.vector_store.similarity_search(query, k=10)
        return [doc.page_content for doc in results]