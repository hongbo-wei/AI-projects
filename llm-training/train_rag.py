from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration, Trainer, TrainingArguments
from datasets import load_dataset
import os

# 1. 加载 tokenizer, retriever & 模型
tokenizer = RagTokenizer.from_pretrained("facebook/rag-sequence-nq")
retriever = RagRetriever.from_pretrained(
    "facebook/rag-sequence-nq", index_name="exact", use_dummy_dataset=True)
model = RagSequenceForGeneration.from_pretrained(
    "facebook/rag-sequence-nq", retriever=retriever)

# 创建输出目录
os.makedirs("output/rag", exist_ok=True)

# 2. 加载并 preprocess 数据
raw_dataset = load_dataset("json", data_files="data/rag.jsonl", split="train")
def preprocess_fn(examples):
    inputs = tokenizer(
        examples["question"],
        truncation=True,
        padding="max_length",
        max_length=128)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            examples["answer"],
            truncation=True,
            padding="max_length",
            max_length=128)
    inputs["labels"] = labels["input_ids"]
    return inputs

dataset = raw_dataset.map(preprocess_fn, batched=True, remove_columns=["question","answer"])
dataset.set_format(type="torch", columns=["input_ids","attention_mask","labels"])

# 3. Trainer 配置
trainer = Trainer(
    model=model,
    args=TrainingArguments(
        output_dir="output/rag",
        per_device_train_batch_size=1,
        num_train_epochs=1,
        fp16=True,
    ),
    train_dataset=dataset,
)

# 4. 开始训练 & 保存
trainer.train()
model.save_pretrained("output/rag")
tokenizer.save_pretrained("output/rag")
