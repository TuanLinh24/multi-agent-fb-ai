import sys
sys.path.insert(0, '.')

from app.rag.embeddings import embed_text

result = embed_text('test')
print('Embeddings work:', len(result))