
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_path = "./router_model/final"
quant_path = "./router_model/awq"

model = AutoAWQForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4
}

model.quantize(tokenizer, quant_config=quant_config)

model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)

print("AWQ quantization complete")
