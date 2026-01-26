import faiss, os, json, numpy as np
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
INDEX_PATH = "data/embeddings.index"
META_PATH = "data/meta.json"

def embed_texts(texts):
    r = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=texts)
    vecs = [d.embedding for d in r.data]
    return np.array(vecs).astype("float32")

def build_index():
    docs, metas = [], []
    for f in os.listdir("data/seed_docs"):
        path = os.path.join("data/seed_docs", f)
        txt = open(path, "r", encoding="utf-8").read()
        for i, chunk in enumerate(txt.split("\n\n")):
            docs.append(chunk)
            metas.append({"file": f, "chunk": i})
    vecs = embed_texts(docs)
    faiss.normalize_L2(vecs)
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    faiss.write_index(index, INDEX_PATH)
    json.dump({"docs": docs, "metas": metas}, open(META_PATH, "w"))
    print("FAISS index built.")

def search(query, k=3, filter_files=None):
    """
    Enhanced search with optional file filtering
    
    Args:
        query: Search query string
        k: Number of results to return
        filter_files: List of filenames to search within (e.g., ['fitness_advanced.txt'])
    """
    index = faiss.read_index(INDEX_PATH)
    meta = json.load(open(META_PATH))
    qv = embed_texts([query])
    faiss.normalize_L2(qv)
    
    # Get more results initially if filtering
    search_k = k * 3 if filter_files else k
    D, I = index.search(qv, min(search_k, len(meta["docs"])))
    
    results = []
    for i, idx in enumerate(I[0]):
        if idx == -1:
            continue
            
        # Apply file filtering if specified
        if filter_files:
            doc_file = meta["metas"][idx]["file"]
            if doc_file not in filter_files:
                continue
                
        results.append(meta["docs"][idx])
        
        # Stop when we have enough results
        if len(results) >= k:
            break
    
    return results

def search_fitness(query, k=3):
    """Search specifically in fitness knowledge bases"""
    return search(query, k, filter_files=['fitness_advanced.txt', 'fitness.txt'])

def search_nutrition(query, k=3):
    """Search specifically in nutrition knowledge bases"""
    return search(query, k, filter_files=['nutrition_comprehensive.txt', 'nutrition.txt'])

def search_medical(query, k=3):
    """Search specifically in medical knowledge bases"""
    return search(query, k, filter_files=['medical_comprehensive.txt', 'medical.txt', 'doctor_avatar_knowledge.txt'])

def search_mental_health(query, k=3):
    """Search specifically in mental health knowledge bases"""
    return search(query, k, filter_files=['mental_health_specialist.txt'])

def search_tracking(query, k=3):
    """Search specifically in tracking/visualization knowledge bases"""
    return search(query, k, filter_files=['tracking_visualization.txt'])
