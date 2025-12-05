import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

# Configuration
DATA_DIR = "../新闻传播学理论知识库"
DB_PATH = "./chroma_db"
COLLECTION_NAME = "journalism_knowledge"

def ingest_data():
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Delete collection if exists to start fresh (optional, good for dev)
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception:
        pass

    # Create collection
    # Use a better Chinese embedding model
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="shibing624/text2vec-base-chinese")
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    documents = []
    metadatas = []
    ids = []
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx')]
    print(f"Found {len(files)} Excel files.")

    for filename in files:
        file_path = os.path.join(DATA_DIR, filename)
        print(f"Processing {filename}...")
        
        try:
            df = pd.read_excel(file_path)
            
            # Determine file type and extract content
            for index, row in df.iterrows():
                content = ""
                meta = {"source": filename, "row": index}
                
                # Type 1: Q&A Style
                if '问题' in df.columns and '答案' in df.columns:
                    q = str(row.get('问题', '')).strip()
                    a = str(row.get('答案', '')).strip()
                    if q and a and q != 'nan' and a != 'nan':
                        content = f"问题：{q}\n答案：{a}"
                        meta['type'] = 'qa'
                
                # Type 2: Theory Style (Content Reference)
                elif '原文内容引用' in df.columns:
                    text = str(row.get('原文内容引用', '')).strip()
                    if text and text != 'nan':
                        content = text
                        meta['type'] = 'theory'
                
                # Fallback: specific column names observed in file list
                # e.g. "传播学教程 智能体.xlsx" might have different structure
                # We can try to concat all text columns if specific ones aren't found
                if not content:
                    # Naive fallback: join all string columns
                    parts = []
                    for col in df.columns:
                        val = str(row[col]).strip()
                        if val and val != 'nan' and len(val) > 10: # heuristic
                            parts.append(f"{col}: {val}")
                    if parts:
                        content = "\n".join(parts)
                        meta['type'] = 'general'

                if content:
                    documents.append(content)
                    metadatas.append(meta)
                    ids.append(f"{filename}_{index}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Add to ChromaDB in batches
    batch_size = 100 # Small batch size to be safe
    total_docs = len(documents)
    print(f"Total documents to ingest: {total_docs}")

    for i in range(0, total_docs, batch_size):
        end = min(i + batch_size, total_docs)
        print(f"Upserting batch {i} to {end}...")
        collection.add(
            documents=documents[i:end],
            metadatas=metadatas[i:end],
            ids=ids[i:end]
        )

    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_data()
