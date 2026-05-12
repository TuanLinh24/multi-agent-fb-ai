from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer
)

from datasets import load_dataset

model_name = "Qwen/Qwen2.5-0.5B-Instruct"


tokenizer = AutoTokenizer.fr