from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM

import asyncio
import torch


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

model.eval()


def _generate_blocking(text: str) -> str:
    model_inputs = tokenizer(
        [text],
        return_tensors="pt"
    ).to(model.device)

    with torch.inference_mode():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=12,
            temperature=0.1,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):]

    return tokenizer.decode(output_ids, skip_special_tokens=True).strip()


async def generate(prompt: str):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful Vietnamese coffee shop assistant. "
                "Reply briefly and naturally."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    return await asyncio.to_thread(_generate_blocking, text)
