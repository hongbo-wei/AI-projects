from transformers import AutoTokenizer, AutoModelForMaskedLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
import os

# 1. 加载 tokenizer & 模型
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForMaskedLM.from_pretrained("bert-base-uncased")

# 创建输出目录
os.makedirs("output/cpt", exist_ok=True)

# 2. 加载并 tokenize 文本数据，使用 Hugging Face Datasets
raw_dataset = load_dataset("text", data_files="data/pretrain.txt", split="train")
def tokenize_fn(examples):
    return tokenizer(examples["text"], truncation=True, max_length=128)
tokenized_dataset = raw_dataset.map(tokenize_fn, batched=True, remove_columns=["text"])

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=True)

# 3. Trainer 配置
trainer = Trainer(
    model=model,
    args=TrainingArguments(
        output_dir="output/cpt",
        per_device_train_batch_size=8,
        num_train_epochs=1,
        fp16=True,
    ),
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

# 4. 开始训练 & 保存
trainer.train()
model.save_pretrained("output/cpt")
tokenizer.save_pretrained("output/cpt")
