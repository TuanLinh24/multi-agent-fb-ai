from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM

import torch


MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto"
)


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

    model_inputs = tokenizer(
        [text],
        return_tensors="pt"
    ).to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32,
        temperature=0.1,
        do_sample=False
    )

    output_ids = generated_ids[0][
        len(model_inputs.input_ids[0]):]

    response = tokenizer.decode(
        output_ids,
        skip_special_tokens=True
    )

    return response