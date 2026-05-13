#!/usr/bin/env python
import os
import sys

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Try importing modules
try:
    import torch
    print(f"Torch version: {torch.__version__}")
except ImportError as e:
    print(f"Torch import error: {e}")

try:
    import transformers
    print(f"Transformers version: {transformers.__version__}")
except ImportError as e:
    print(f"Transformers import error: {e}")

try:
    import sentence_transformers
    print(f"Sentence-transformers imported successfully")
    print(f"Sentence-transformers version: {sentence_transformers.__version__}")
except ImportError as e:
    print(f"Sentence-transformers import error: {e}")
