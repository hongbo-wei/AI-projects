from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import load_dataset
import os

# 1. 加载 tokenizer & 模型
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")

# 添加 padding token
tokenizer.pad_token = tokenizer.eos_token

# 创建输出目录
os.makedirs("output/sft", exist_ok=True)

# 2. 加载 JSONL 数据并 tokenize，加入 eos_token 分隔
raw_dataset = load_dataset("json", data_files="data/sft.jsonl", split="train")
def preprocess_fn(examples):
    prompts = [p + tokenizer.eos_token for p in examples["prompt"]]
    responses = [r + tokenizer.eos_token for r in examples["response"]]
    inputs = tokenizer(prompts, truncation=True, padding="max_length", max_length=128)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(responses, truncation=True, padding="max_length", max_length=128)
    inputs["labels"] = labels["input_ids"]
    return inputs

dataset = raw_dataset.map(preprocess_fn, batched=True, remove_columns=["prompt","response"])
dataset.set_format(type="torch", columns=["input_ids","attention_mask","labels"])

# 3. Trainer 配置
trainer = Trainer(
    model=model,
    args=TrainingArguments(
        output_dir="output/sft",
        per_device_train_batch_size=2,
        num_train_epochs=2,
        fp16=True,
    ),
    train_dataset=dataset,
)

# 4. 开始训练 & 保存
trainer.train()
model.save_pretrained("output/sft")
tokenizer.save_pretrained("output/sft")
