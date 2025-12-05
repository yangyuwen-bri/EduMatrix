import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from typing import List, Optional

class RAGService:
    def __init__(self):
        # Initialize ChromaDB
        self.db_path = "./chroma_db"
        self.collection_name = "journalism_knowledge"
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="shibing624/text2vec-base-chinese")
        self.collection = None
        
        # Initialize OpenAI Client
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        self.openai_client = OpenAI(api_key=api_key, base_url=base_url) if api_key else None
        self.model_name = os.getenv("LLM_MODEL", "deepseek-chat")

    def get_collection(self):
        if self.collection:
            return self.collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name, embedding_function=self.ef)
            return self.collection
        except Exception as e:
            print(f"Warning: Collection not found ({e}).")
            return None

    def retrieve(self, query: str, n_results: int = 3, user_id: str = None, role: str = None, target_user_ids: List[str] = None):
        collection = self.get_collection()
        if not collection:
            raise Exception("Knowledge base is initializing. Please try again later.")
        
        # Query ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=n_results * 3 # Fetch more to allow for filtering
        )
        
        # Post-processing filter
        filtered_docs = []
        filtered_metas = []
        
        if results['documents']:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            
            for doc, meta in zip(docs, metas):
                doc_owner = meta.get('owner_id')
                
                # Filter Logic
                keep = False
                
                # 1. System/Public docs (no owner or "system") -> Always Keep
                if not doc_owner or doc_owner == 'system':
                    keep = True
                
                # 2. Internal Test Role
                elif role == 'internal_test':
                    # If target_user_ids is specified, only keep docs from those users
                    if target_user_ids:
                        if doc_owner in target_user_ids:
                            keep = True
                    else:
                        # If no target specified, keep everything (God View)
                        keep = True
                        
                # 3. Regular User (Teacher/Student)
                elif user_id:
                    # Only keep own docs
                    if doc_owner == user_id:
                        keep = True
                
                if keep:
                    filtered_docs.append(doc)
                    filtered_metas.append(meta)
            
            # Update results
            results['documents'][0] = filtered_docs[:n_results]
            results['metadatas'][0] = filtered_metas[:n_results]

        return results

    def list_documents(self, user_id: str = None, role: str = None):
        collection = self.get_collection()
        if not collection:
            return {}
            
        # Fetch all metadata to aggregate files
        # Note: This is inefficient for large datasets but acceptable for prototype
        all_data = collection.get(include=['metadatas'])
        metadatas = all_data['metadatas']
        
        files_map = {} # owner_id -> set(filenames)
        
        for meta in metadatas:
            owner = meta.get('owner_id', 'system')
            source = meta.get('source', 'Unknown')
            
            # Filter based on role
            if role != 'internal_test' and user_id:
                # User requested to NOT see system files in the list, only their own.
                if owner != user_id:
                    continue
            
            if owner not in files_map:
                files_map[owner] = set()
            files_map[owner].add(source)
            
        # Convert sets to lists
        return {k: list(v) for k, v in files_map.items()}

    def generate_answer(self, query: str, context: str, history: List[dict], system_prompt: str):
        if not self.openai_client:
            raise Exception("OpenAI API Key not configured.")

        user_prompt = f"""
【背景知识】：
{context}

【用户提问】：
{query}
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for msg in history[-4:]:
                messages.append(msg)
        messages.append({"role": "user", "content": user_prompt})

        completion = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7 # Default temperature, can be adjusted if needed or passed as arg
        )
        
        return completion.choices[0].message.content

    def add_document(self, content: str, filename: str, user_id: str):
        collection = self.get_collection()
        if not collection:
            raise Exception("Knowledge base is initializing.")
            
        # Simple chunking (can be improved)
        import uuid
        chunk_size = 500
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{"source": filename, "owner_id": user_id} for _ in chunks]
        
        collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        return len(chunks)

# Singleton instance
rag_service = RAGService()
