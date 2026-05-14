import sys
sys.path.insert(0, '.')

print("Testing imports...")

try:
    from sentence_transformers import SentenceTransformer
    print("✓ sentence_transformers imported")
except Exception as e:
    print(f"✗ sentence_transformers error: {e}")

try:
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("✓ Model loaded")
except Exception as e:
    print(f"✗ Model loading error: {e}")

try:
    result = model.encode(["test"])
    print(f"✓ Encoding works, shape: {result.shape}")
except Exception as e:
    print(f"✗ Encoding error: {e}")