from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

ADAPTER_PATH = "./router_model/adapter"

OUTPUT_PATH = "./router_model/final"

print("Loading base model...")

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

print("Loading adapter...")

model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_PATH
)

print("Merging model...")

merged_model = model.merge_and_unload()

print("Saving final model...")

merged_model.save_pretrained(OUTPUT_PATH)

tokenizer.save_pretrained(OUTPUT_PATH)

print("DONE")