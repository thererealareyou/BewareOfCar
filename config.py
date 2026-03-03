import os

# ==========================================
# 1. РЕЖИМ ЗАПУСКА (IDE CONTROL)
# ==========================================
# Опции: 'cli' (командная строка), 'finetune', 'generate', 'make_meme', 'process_images'
# Если стоит 'cli', то программа будет ждать аргументы из консоли.
# Если другое - возьмет параметры из этого файла.
RUN_MODE = 'make_meme'


# ==========================================
# 2. ПУТИ К ФАЙЛАМ И ПАПКАМ
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Папки
DIR_RAW_IMAGES = os.path.join(BASE_DIR, "raw_images")          # Куда кидать сырые картинки
DIR_PROCESSED_IMAGES = os.path.join(BASE_DIR, "cropped_originals") # Откуда брать готовые фоны
DIR_OUTPUT_MEMES = os.path.join(BASE_DIR, "generated_memes")   # Куда сохранять мемы
DIR_CSV = os.path.join(BASE_DIR, "csv_files")
DIR_MODELS = os.path.join(BASE_DIR, "fine_tuned_models")

# Файлы
FONT_PATH = os.path.join(BASE_DIR, "impact.ttf")


# ==========================================
# 3. ПАРАМЕТРЫ ОБУЧЕНИЯ (FINETUNE)
# ==========================================
TRAIN_BASE_MODEL = os.path.join(DIR_MODELS, "fine_tuned_model_nietzcshe_neural_main_diary")
TRAIN_DATASET_FILE = "memes.csv"  # Имя файла в папке csv_files
TRAIN_OUTPUT_NAME = "my_custom_model_v1"
TRAIN_EPOCHS = 3
TRAIN_BATCH_SIZE = 4
TRAIN_LEARNING_RATE = 2e-5


# ==========================================
# 4. ПАРАМЕТРЫ ГЕНЕРАЦИИ (GENERATE)
# ==========================================
GEN_MODEL_PATH = "fine_tuned_model_nietzcshe_neural_main_diary" # Можно имя папки или путь
GEN_AMOUNT = 50
GEN_PROMPT_FILE = None     # Откуда брать идеи (если None, то рандом)
GEN_BASE_PROMPT = None         # Если нужно начать с фразы, например "Когда ты"
GEN_ADD_RANDOM_WORD = False            # Добавлять ли случайное слово к промпту
GEN_TEMP_RANGE = (1.2, 1.8)           # Диапазон креативности
GEN_SAVE_IMAGES = False                # Сразу рисовать картинки?


# ==========================================
# 5. ПАРАМЕТРЫ РУЧНОГО СОЗДАНИЯ (MAKE MEME)
# ==========================================
MANUAL_TEXT = "У тебя есть сердце. У меня тоже есть сердце, и я люблю тебя.|С уважением, твой друг-сюрреализм." # Разделитель |
MANUAL_IMAGE = None # Имя файла (например 'cat.jpg') или None (случайный)


# ==========================================
# 6. ПАРАМЕТРЫ ОБРАБОТКИ (PROCESS IMAGES)
# ==========================================
PROC_TARGET_SIZE = (400, 400)
