from transformers import pipeline
from app.config import MODEL_NAME

pipe = pipeline(
    "text-generation",
    model=MODEL_NAME,
    device_map="auto"
)

async def generate(prompt: str, max_new_tokens=128):

    result = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=False
    )

    return result[0]["generated_text"]