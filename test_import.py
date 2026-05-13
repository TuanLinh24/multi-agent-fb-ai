try:
    import sentence_transformers
    print('sentence_transformers imported successfully')
except Exception as e:
    print(f'Error importing sentence_transformers: {e}')

try:
    from sentence_transformers import SentenceTransformer
    print('SentenceTransformer imported successfully')
except Exception as e:
    print(f'Error importing SentenceTransformer: {e}')