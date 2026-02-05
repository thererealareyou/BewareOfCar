import torch
import pandas as pd
import os
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset


class MemeLLMTrainer:
    def __init__(self, model_name: str, output_base_dir: str = "./results"):
        """
        Инициализация тренера.

        :param model_name: Название модели или путь к ней (например, 'gpt2', 'ai-forever/rugpt3small_based_on_gpt2').
        :param output_base_dir: Базовая папка для сохранения результатов.
        """
        self.model_name = model_name
        self.output_base_dir = output_base_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                print("Установлен pad_token = eos_token")
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки токенизатора: {e}")

    def load_and_prepare_data(self, csv_path: str, text_column: str = 'text', sep: str = ',', max_length: int = 256):
        """
        Загружает CSV, проверяет данные и токенизирует их.
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Файл не найден: {csv_path}")

        try:
            
            df = pd.read_csv(csv_path, sep=sep, on_bad_lines='skip')
            df = df.dropna(subset=[text_column])  

            if text_column not in df.columns:
                raise ValueError(f"Колонка '{text_column}' не найдена в файле. Доступные: {df.columns.tolist()}")

            print(f"Загружено {len(df)} строк из {csv_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения данных: {e}")

        
        dataset = Dataset.from_pandas(df[[text_column]])

        
        def tokenize_function(examples):
            tokenized = self.tokenizer(
                examples[text_column],
                padding="max_length",
                truncation=True,
                max_length=max_length
            )
            
            tokenized['labels'] = tokenized['input_ids'].copy()
            return tokenized

        print("Начинаю токенизацию...")
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=[text_column]  
        )
        return tokenized_dataset

    def train(self, train_dataset, run_name: str, hyperparams: dict = None):
        """
        Запуск обучения с динамическими гиперпараметрами.

        :param train_dataset: Подготовленный датасет (результат load_and_prepare_data).
        :param run_name: Имя текущего запуска (используется для названия папки вывода).
        :param hyperparams: Словарь с настройками обучения (lr, epochs, batch_size и т.д.).
        """

        
        default_params = {
            'learning_rate': 2e-5,
            'num_train_epochs': 3,
            'per_device_train_batch_size': 4,
            'gradient_accumulation_steps': 1,
            'save_steps': 1000,
            'logging_steps': 100,
            'fp16': torch.cuda.is_available(),  
            'warmup_steps': 0,
            'weight_decay': 0.01
        }

        
        if hyperparams:
            default_params.update(hyperparams)

        output_dir = os.path.join(self.output_base_dir, run_name)

        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            **default_params  
        )

        
        model = AutoModelForCausalLM.from_pretrained(self.model_name)
        model.to(self.device)

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=DataCollatorForLanguageModeling(self.tokenizer, mlm=False)
        )

        print(f"Запуск обучения '{run_name}' с параметрами: {default_params}")
        trainer.train()

        
        final_save_path = os.path.join(output_dir, "final_model")
        trainer.save_model(final_save_path)
        self.tokenizer.save_pretrained(final_save_path)
        print(f"Модель сохранена в: {final_save_path}")
