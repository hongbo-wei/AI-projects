# src/generator.py
"""
File: generator.py
Generate responses using an LLM.
"""

from transformers import AutoTokenizer, AutoModelForCausalLM

class Generator:
    def __init__(self, model_id="meta-llama/Meta-Llama-3-8B-Instruct"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
    
    def generate(self, prompt, max_new_tokens=150, temperature=0.7):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=temperature)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    gen = Generator()
    sample_prompt = "Question: What is AI?\nAnswer:"
    response = gen.generate(sample_prompt)
    print(response)
