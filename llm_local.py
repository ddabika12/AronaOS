# llm_local.py
from llama_cpp import Llama

llm = Llama(
    model_path="models/phi.gguf",  # Update model here
    n_ctx=4096,           # Phi-3 supports 4k context
    n_threads=4           # Adjust threads to your CPU capability
)

def run_local_llm(prompt):
    output = llm(
        prompt=prompt,
        max_tokens=512,
        stop=["<|end|>", "<|assistant|>", "<|user|>"],
        temperature=0.7,
    )
    return output["choices"][0]["text"].strip()
