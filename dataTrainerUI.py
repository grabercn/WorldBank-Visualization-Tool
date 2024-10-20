# dataTrainerUI.py will be extensible off the main ui and used to train the data using a transformer model

import transformers
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer, DataCollatorForSeq2Seq, Trainer, TrainingArguments
from datasets import Dataset, load_metric
import pandas as pd

# Load the CSV data
data = pd.read_csv("C:/Users/cgrab/OneDrive/Documents/{ } Documents/Data Sets/Popular_Baby_Names.csv")
print(data.columns)  # Print column names to verify

# Convert pandas DataFrame to HuggingFace Dataset
dataset = Dataset.from_pandas(data)

# Load the pre-trained tokenizer
tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-small")

# Preprocessing function
def preprocess_function(examples):
    source = examples["source"]
    target = examples["target"]
    
    # Tokenize inputs and targets
    inputs = tokenizer(source, padding="max_length", truncation=True, max_length=128)
    targets = tokenizer(target, padding="max_length", truncation=True, max_length=128)
    
    # Replace padding token id's in the labels by -100
    targets["input_ids"] = [
        [(t if t != tokenizer.pad_token_id else -100) for t in target]
        for target in targets["input_ids"]
    ]

    return {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"],
        "labels": targets["input_ids"],
    }

# Apply preprocessing to the dataset
tokenized_dataset = dataset.map(preprocess_function, batched=True)

# Split the dataset into training and validation sets
train_test_split = tokenized_dataset.train_test_split(test_size=0.2)
train_dataset = train_test_split['train']
eval_dataset = train_test_split['test']

# Load the pre-trained model
model = AutoModelForSeq2SeqLM.from_pretrained("google/t5-small")

# Data collator
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./output_dir",
    evaluation_strategy="steps",
    eval_steps=1000,
    save_steps=1000,
    num_train_epochs=5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_steps=100,
    save_total_limit=2,
    load_best_model_at_end=True,
    predict_with_generate=True,
)

# Create and train the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

# Train the model
trainer.train()

# Save the trained model
trainer.save_model("./trained_model")
