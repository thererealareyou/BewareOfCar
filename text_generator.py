import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import pandas as pd
import random
import re
import deprecated
import csv


def split_sentence(sentence):
    last_punctuation_index = max(sentence[:-4].rfind('.'), sentence[:-4].rfind('!'), sentence[:-4].rfind('?'))

    if last_punctuation_index != -1:
        part1 = sentence[:last_punctuation_index + 1].strip()
        part2 = sentence[last_punctuation_index + 1:].strip()
        if part2.startswith('» ') or part2.startswith('" '):
            part1 = part1 + part2[0:2]
            part2 = part2[2:]
        if part2.startswith('— '):
            part2 = part2[2:]
        return part1, part2
    else:
        return sentence, ""


@deprecated.deprecated
def use_trained_model_old(model):
    model_directory = str('fine_tuned_models/fine_tuned_model_'+model)
    tokenizer = AutoTokenizer.from_pretrained(model_directory)
    model = AutoModelForCausalLM.from_pretrained(model_directory)

    df = pd.read_csv("corpus.csv", on_bad_lines='skip', sep=' ')
    words = df['text'].dropna().tolist()

    for i in range(50):
        random_word = random.choice(words)
        sentence = ('Валерий Капустин ')
        print("Начальное слово:", random_word)
        input_ids = tokenizer.encode(sentence, return_tensors="pt")

        while True:
            with torch.no_grad():
                outputs = model(input_ids)
                logits = outputs.logits
                last_token_logits = logits[:, -1, :]
                probabilities = torch.softmax(last_token_logits, dim=-1)
                top_two_indices = torch.topk(probabilities, 4).indices[0]
                next_token_id = top_two_indices[random.randint(0, 3)].item()
                input_ids = torch.cat((input_ids, torch.tensor([[next_token_id]])), dim=1)
                current_sentence = tokenizer.decode(input_ids[0], skip_special_tokens=True)

                print(current_sentence)
                if len(current_sentence) > 400 or ('\n' in current_sentence) or ('/' in current_sentence):
                    break

        print(current_sentence, '\n\n')


def use_trained_model(model_name, amount_of_sentences):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model_directory = str('fine_tuned_models/fine_tuned_model_'+model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_directory)
    model = AutoModelForCausalLM.from_pretrained(model_directory).to(device)

    df = pd.read_csv('csv_files/anek_mixed.csv', on_bad_lines='skip', sep='\t')
    texts = df['text'].tolist()

    text_array = []

    sentence_counter = 0
    chars_to_remove = '«»".,]!?)'
    iter = False
    fixed_text = ''
    translation_table = str.maketrans('', '', chars_to_remove)
    filtered_words = [
        word.translate(translation_table)
        for text in texts
        for word in text.split(' ')
        if len(word) > 2 and word[0].istitle() and "Зарат" not in word
    ]

    with open('csv_files/phrases.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        phrases = [row['text'] for row in reader]

    filtered_words = ["Давид грустно посмотрел на Мирру и сказал: 'С днём рождения. "]

    print(f"Количество отфильтрованных слов: {len(filtered_words)}")
    print('### НАЧАЛО ГЕНЕРАЦИИ ###')

    while True:
        for temp in [1.2, 1.5, 1.8]:
            iter = not iter

            # print(iter)

            if iter:
                fixed_text = ''

            if len(fixed_text) < 2:
                fixed_text = ''

            random_word = random.choice(filtered_words) if (iter or fixed_text == '') else fixed_text
            # print('random word: ', random_word)
            input_ids = tokenizer.encode(random_word, return_tensors="pt").to(device)

            # print('Начальное слово', random_word)

            # Использование функции generate
            outputs = model.generate(
                input_ids,
                max_length=random.randint(15 + int(len(fixed_text) / 2), 40 + int(len(fixed_text) / 2)),
                temperature=temp,
                top_k=200,
                top_p=0.60,
                repetition_penalty=6.0,
                do_sample=True,
                num_return_sequences=2,
                num_beams=2,
                early_stopping=True
            )

            possible_outputs = []

            for output in outputs:
                generated_text = tokenizer.decode(output, skip_special_tokens=True)
                fixed_text = (generated_text.replace('\n', ' ').replace('&raquo;', '')
                                  .replace('&laquo;', '').replace('&mdash;', '-')
                                  .replace('&quot;', '').replace('&nbsp;', '')
                                  .replace('&ndash;', '-')
                                  )

                raquo = fixed_text.count('»')
                laquo = fixed_text.count('«')

                if laquo > raquo:
                    indices = [i for i, char in enumerate(fixed_text) if char == '«']
                    fixed_text = ''.join(
                        [char for i, char in enumerate(fixed_text) if i not in indices[:laquo - raquo]])

                if laquo < raquo:
                    indices = [i for i, char in enumerate(fixed_text) if char == '»']
                    fixed_text = ''.join(
                        [char for i, char in enumerate(fixed_text) if i not in indices[:raquo - laquo]])

                digits = re.findall(r'\d', fixed_text)
                letters = re.findall(r'[a-zA-Z]', fixed_text)
                weirdos = re.findall(r'[«»".()&—]', fixed_text)

                if len(digits) > 30 or len(letters) > 70 or len(weirdos) + len(digits) > 70:
                    # print('Слишком много цифр, английских букв или рандомных символов, пропускаю предложение')
                    fixed_text = ''
                    continue

                last_punctuation_index = max(
                    idx for idx in (0, fixed_text.rfind('.'), fixed_text.rfind('!'), fixed_text.rfind('?'), fixed_text.rfind('»')) if idx != -1
                )

                if last_punctuation_index != 0:
                    fixed_text = fixed_text[:last_punctuation_index + 1]
                    possible_outputs.append(fixed_text)

            try:
                fixed_text = min(possible_outputs)
            except ValueError:
                # print('Обработал ошибку')
                iter = False
                continue

            fixed_text = fixed_text[:last_punctuation_index + 1]
            '''print(f"\n"
                  f"Начальное слово: {random_word}, \n"
                  f"Температура: {temp}, \n"
                  f"Сгенерированное предложение: {generated_text}\n"
                  f"Исправленное предложение: {fixed_text}")'''

            if (not iter and len(fixed_text) > 20):
                sentence_counter += 1
                text_array.append(fixed_text)
                print(f'{fixed_text}\n Количество предложений: {sentence_counter}/{amount_of_sentences}\n')

                if sentence_counter >= amount_of_sentences:
                    break
        if sentence_counter >= amount_of_sentences:
            break

    return [split_sentence(sentence) for sentence in text_array]



# Ещё более устаревший, но возможно нужный код

''' 

import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import re

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Функция для проверки, является ли токен эмодзи
    def is_emoji(token):
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F700-\U0001F77F"  # alchemical symbols
            u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U0001FA00-\U0001FA6F"  # Chess Symbols
            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            u"\U00002702-\U000027B0"  # Dingbats
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        return bool(emoji_pattern.search(token))

    # Функция для подсчёта количества эмодзи в тексте
    def count_emojis(text):
        return sum(is_emoji(char) for char in text)

    # Загрузка модели и токенизатора
    model_directory = 'fine_tuned_model_nietzcshe_2'
    tokenizer = AutoTokenizer.from_pretrained(model_directory)
    model = AutoModelForCausalLM.from_pretrained(model_directory).to(device)

    df = pd.read_csv('n.csv', on_bad_lines='skip', sep='\t')
    texts = df['text'].tolist()

    filtered_words = []
    for text in texts:
        for word in text.split(' '):
            if len(word) > 2:
                if word[0].istitle() and ("Зарат" not in word):
                    filtered_words.append(word.replace('«', '').replace('»', '').replace('"', '')
                                          .replace('.', '').replace(']', '').replace(')', '')
                                          .replace(',', ''))

    print(len(filtered_words))

    print('### НАЧАЛО ГЕНЕРАЦИИ ###')

    for i in range(15):
        temperature_values = [1.2, 1.5, 1.8]

        for temp in temperature_values:
            punctuation_marks = 0
            random_word = random.choice(filtered_words)
            sentence = random_word
            print("Начальное слово:", random_word)
            input_ids = tokenizer.encode(sentence, return_tensors="pt").to(device)

            while True:
                with torch.no_grad():
                    outputs = model(input_ids)
                    logits = outputs.logits / temp
                    last_token_logits = logits[:, -1, :]
                    probabilities = torch.softmax(last_token_logits, dim=-1)
                    top_indices = torch.topk(probabilities, 3).indices[0]
                    decoded_indices = [tokenizer.decode(top_indices[0], skip_special_tokens=True),
                                       tokenizer.decode(top_indices[1], skip_special_tokens=True),
                                       tokenizer.decode(top_indices[2], skip_special_tokens=True)]
                    next_token_id = top_indices[random.randint(0, 2) if (not ' ' in decoded_indices[0]) else 0].item()
                    input_ids = torch.cat((input_ids, torch.tensor([[next_token_id]]).to(device)), dim=1).to(device)
                    current_sentence = tokenizer.decode(input_ids[0], skip_special_tokens=True)

                    if ('.' in current_sentence) or ('?' in current_sentence) or ('!' in current_sentence):
                        punctuation_marks += 1

                    if len(current_sentence) > 300 or ('\n' in current_sentence):
                        break

            print(f"Температура: {temp}, Сгенерированное предложение: {current_sentence}\n")

'''

'''

    for i in range(50):
        random_word = random.choice(words)
        sentence = "Всероссийское военное историческое общество"
        print("Начальное слово:", sentence)
        input_ids = tokenizer.encode(sentence, return_tensors="pt")

        while True:
            with torch.no_grad():
                outputs = model(input_ids)
                logits = outputs.logits
                last_token_logits = logits[:, -1, :]
                probabilities = torch.softmax(last_token_logits, dim=-1)
                top_two_indices = torch.topk(probabilities, 3).indices[0]
                next_token_id = top_two_indices[0].item()
                next_token = tokenizer.decode(next_token_id, skip_special_tokens=True)
                print('"', next_token, '"', sep='')

                input_ids = torch.cat((input_ids, torch.tensor([[next_token_id]])), dim=1)
                current_sentence = tokenizer.decode(input_ids[0], skip_special_tokens=True)

                if count_emojis(current_sentence) > 3:
                    print("Превышено количество эмодзи. Генерация остановлена.")
                    break

                if len(current_sentence) > 200 or ('\n' in current_sentence) or ('/' in current_sentence):
                    break

'''
