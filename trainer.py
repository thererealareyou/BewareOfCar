import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, \
    DataCollatorForLanguageModeling
from sklearn.model_selection import train_test_split
from datasets import Dataset
import pandas as pd


def train_model_new():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_name = "fine_tuned_model_nietzcshe_2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)

    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            padding="max_length",
            truncation=True,
            max_length=256,
            return_tensors="pt"
        )

    try:
        df = pd.read_csv("neuralmachine.csv", sep='\t', on_bad_lines='warn')
        assert 'text' in df.columns
    except Exception as e:
        print(f"Data loading error: {str(e)}")
        return

    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)

    train_dataset = Dataset.from_pandas(train_df[['text']])
    val_dataset = Dataset.from_pandas(val_df[['text']])

    tokenized_train = train_dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=['text'],
        load_from_cache_file=False
    )

    training_args = TrainingArguments(
        output_dir='./results',
        evaluation_strategy='steps',
        eval_steps=500,
        save_steps=1000,
        learning_rate=3e-5,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=2,
        num_train_epochs=3,
        fp16=torch.cuda.is_available(),
        logging_dir='./logs',
        report_to="none"
    )

    with torch.device("cuda" if torch.cuda.is_available() else "cpu"):
        model = AutoModelForCausalLM.from_pretrained(model_name)

    try:
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_train,
            data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
        )
        trainer.train()
        output_dir = "./fine_tuned_model_nietzsche_neural"
        trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)
        print(f"Model saved to {output_dir}")

    except Exception as e:
        print(f"Training failed: {str(e)}")
        return


def train_model(base_model, dataset, name):
    def tokenize_function(examples):
        tokenized = tokenizer(examples['text'], padding="max_length", truncation=True, max_length=256)
        tokenized['labels'] = tokenized['input_ids'].copy()
        return tokenized

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model_name = str('fine_tuned_models/fine_tuned_model_' + base_model)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)

    df = pd.read_csv('csv_files/' + str(dataset), on_bad_lines='skip', sep='\xa0')
    t_ds, v_ds = train_test_split(df, test_size=0.1)

    train_dataset = Dataset.from_pandas(t_ds[['text']])
    val_dataset = Dataset.from_pandas(v_ds[['text']])

    tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
    tokenized_val_dataset = val_dataset.map(tokenize_function, batched=True)

    training_args = TrainingArguments(
        output_dir='./results',
        save_steps=2500,
        eval_strategy='epoch',
        learning_rate=5e-6,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        num_train_epochs=2,
        weight_decay=7e-5,
        fp16=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_val_dataset
    )

    trainer.train()

    trainer.save_model(str('fine_tuned_models/fine_tuned_model_' + name))
    tokenizer.save_pretrained(str('fine_tuned_models/fine_tuned_model_' + name))


if __name__ == '__main__':
    train_model()
