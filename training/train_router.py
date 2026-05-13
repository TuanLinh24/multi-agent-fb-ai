from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    BitsAndBytesConfig
)

from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training
)

from trl import SFTTrainer

from training.router_sft_dataset import get_dataset

import torch


MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"


# =========================
# TOKENIZER
# =========================

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

tokenizer.pad_token = tokenizer.eos_token


# =========================
# QUANTIZATION
# =========================

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)


# =========================
# MODEL
# =========================

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto"
)

model = prepare_model_for_kbit_training(model)


# =========================
# LORA
# =========================

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)


# =========================
# DATASET
# =========================

dataset = get_dataset()

def format_example(example):
    return example['text']


train_texts = [
    {"text": format_example(x)}
    for x in dataset
]

train_dataset = Dataset.from_list(train_texts)


# =========================
# TRAINING
# =========================

trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    dataset_text_field="text",
    tokenizer=tokenizer,
    max_seq_length=256,
    args=TrainingArguments(
        output_dir="./router_model",

        per_device_train_batch_size=1,

        gradient_accumulation_steps=4,

        learning_rate=2e-4,

        num_train_epochs=3,

        logging_steps=1,

        save_strategy="epoch",

        fp16=True,

        optim="paged_adamw_8bit",

        report_to="none"
    ),
)

trainer.train()


# =========================
# SAVE
# =========================

trainer.model.save_pretrained(
    "./router_model/final"
)

tokenizer.save_pretrained(
    "./router_model/final"
)

print("DONE TRAINING")