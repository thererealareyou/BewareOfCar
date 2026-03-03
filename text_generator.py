import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import pandas as pd
import random
import re
import os


class MemeGenerator:
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if not os.path.exists(model_path):
            potential_path = os.path.join('fine_tuned_models', f'fine_tuned_model_{model_path}')
            if os.path.exists(potential_path):
                model_path = potential_path

        print(f"Загрузка модели из: {model_path}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)
            self.model.eval()

            # Настройка фильтрации нежелательных токенов
            forbidden_strs = ["http", "https", "www", ".com", ".ru", "://", ".net", ".org", "Бросай", "Бр"]
            self.bad_words_ids = [self.tokenizer.encode(word, add_special_tokens=False) for word in forbidden_strs]

        except Exception as e:
            raise RuntimeError(f"Не удалось загрузить модель: {e}")

    def generate_memes(self, amount: int, prompt_file: str = None, base_prompt: str = None,
                       add_random_word: bool = False, min_length: int = 20,
                       temperature_range: tuple = (1.2, 1.8)) -> list:

        prompts = []
        if (not base_prompt or add_random_word) and prompt_file:
            prompts = self._prepare_prompts(prompt_file)

        print(prompts)

        generated_sentences = []

        gen_params = {
            'max_new_tokens': random.randint(15, 100),
            'top_k': 2000,
            'repetition_penalty': 2.5,
            'top_p': 0.98,
            'do_sample': True,
            'num_return_sequences': 1,
            'num_beams': 6,
            'early_stopping': True
        }

        print(f"Начинаю генерацию {amount} мемов...")

        attempts = 0
        max_attempts = amount * 2

        while len(generated_sentences) < amount and attempts < max_attempts:
            attempts += 1
            current_temp = random.uniform(temperature_range[0], temperature_range[1])

            # --- Выбор промпта ---
            start_phrase = ""
            if base_prompt:
                start_phrase = base_prompt
            elif prompts:
                start_phrase = self._select_random_word(prompts)

            if add_random_word and prompts:
                second_word = self._select_random_word(prompts)
                if second_word:
                    if not start_phrase:
                        start_phrase = second_word
                    elif second_word.lower().strip() not in start_phrase.lower():
                        start_phrase += " " + second_word

            if not start_phrase or not start_phrase.strip():
                start_phrase = self.tokenizer.bos_token if self.tokenizer.bos_token else " "
            # ---------------------

            input_ids = self.tokenizer.encode(start_phrase.capitalize(), return_tensors="pt").to(self.device)

            try:
                # Генерация напрямую через transformers без кастомных процессоров
                outputs = self.model.generate(
                    input_ids,
                    temperature=current_temp,
                    pad_token_id=self.tokenizer.eos_token_id,
                    bad_words_ids=self.bad_words_ids,
                    **gen_params
                )
            except Exception as e:
                print(f"Ошибка при генерации: {e}")
                continue

            for output in outputs:
                text = self.tokenizer.decode(output, skip_special_tokens=True)
                cleaned = self._clean_text(text)

                if self._is_noisy(cleaned): continue

                last_punct = self._find_last_punctuation(cleaned)
                if last_punct > 0:
                    candidate = cleaned[:last_punct + 1]

                    if len(candidate) > min_length and candidate not in generated_sentences:
                        generated_sentences.append(candidate)
                        print(f"[{len(generated_sentences)}/{amount}] {candidate}")
                        if len(generated_sentences) >= amount:
                            break

        return [self._split_sentence_by_tag(s) for s in generated_sentences]

    @staticmethod
    def _prepare_prompts(file_path: str) -> list:
        unique_words = set()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    unique_words.update(line.strip().split())

        return list(unique_words)

    @staticmethod
    def _clean_text(text: str) -> str:
        cleaned = text.replace('\n', ' ').replace('  ', ' ')
        cleaned = cleaned.replace('#NAME?', '')
        return cleaned.strip()

    @staticmethod
    def _is_noisy(text: str) -> bool:
        digits = len(re.findall(r'\d', text))
        letters = len(re.findall(r'[a-zA-Z]', text))
        return (digits > 30 or letters > 70)

    @staticmethod
    def _find_last_punctuation(text: str) -> int:
        indices = [text.rfind(c) for c in ['.', '!', '?', '»']]
        valid = [i for i in indices if i != -1]
        return max(valid) if valid else -1

    @staticmethod
    def _split_sentence_by_tag(text: str) -> list:
        if not text: return ["", ""]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences: return [text, ""]
        if len(sentences) == 1:
            return [sentences[0], ""] if random.random() > 0.5 else ["", sentences[0]]
        else:
            mid = len(sentences) // 2
            return [" ".join(sentences[:mid]), " ".join(sentences[mid:])]

    @staticmethod
    def _select_random_word(words: list) -> str:
        if not words: return ""
        return random.choice(words)
