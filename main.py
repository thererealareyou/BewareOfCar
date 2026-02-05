import argparse
import os
import random
import logging
from types import SimpleNamespace

import config
from trainer import MemeLLMTrainer
from text_generator import MemeGenerator
from image_creator import MemeImageProcessor
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_finetune(args):
    logging.info(f"--- РЕЖИМ ОБУЧЕНИЯ ---")
    trainer = MemeLLMTrainer(model_name=args.model, output_base_dir=config.DIR_MODELS)
    
    dataset_path = args.file
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join(config.DIR_CSV, args.file)
    try:
        dataset = trainer.load_and_prepare_data(dataset_path, sep='\t')
    except Exception as e:
        logging.error(f"Ошибка датасета: {e}")
        return
    hyperparams = {
        'learning_rate': args.lr,
        'num_train_epochs': args.epochs,
        'per_device_train_batch_size': args.batch_size
    }
    trainer.train(dataset, run_name=args.save_loc, hyperparams=hyperparams)

def run_generate(args):
    logging.info(f"--- РЕЖИМ ГЕНЕРАЦИИ ---")
    
    model_path = args.model
    if not os.path.exists(model_path):
        potential_path = os.path.join(config.DIR_MODELS, args.model)
        if os.path.exists(potential_path):
            model_path = potential_path
    try:
        generator = MemeGenerator(model_path=model_path)
    except Exception as e:
        logging.error(e)
        return
    
    prompt_file = None
    if args.file:
        prompt_file = args.file if os.path.exists(args.file) else os.path.join(config.DIR_CSV, args.file)
    texts_pairs = generator.generate_memes(
        amount=args.amount,
        prompt_file=prompt_file,
        base_prompt=args.base_prompt,
        add_random_word=args.add_random,
        temperature_range=args.temp_range
    )
    if args.save_images and texts_pairs:
        logging.info("Генерация изображений...")
        processor = MemeImageProcessor(
            font_path=config.FONT_PATH,
            output_meme_dir=config.DIR_OUTPUT_MEMES,
            processed_dir=config.DIR_PROCESSED_IMAGES
        )
        
        available_images = [f for f in os.listdir(config.DIR_PROCESSED_IMAGES)
                            if f.lower().endswith(('.jpg', '.png'))]
        if not available_images:
            logging.error(f"Нет картинок в {config.DIR_PROCESSED_IMAGES}. Запустите режим 'process'!")
            return
        for top, bottom in texts_pairs:
            src = os.path.join(config.DIR_PROCESSED_IMAGES, random.choice(available_images))
            res = processor.create_meme(src, top, bottom)
            if res: logging.info(f"Мем готов: {res}")

def run_make_manual(args):
    logging.info(f"--- РЕЖИМ РУЧНОГО СОЗДАНИЯ ---")
    processor = MemeImageProcessor(
        font_path=config.FONT_PATH,
        output_meme_dir=config.DIR_OUTPUT_MEMES,
        processed_dir=config.DIR_PROCESSED_IMAGES
    )
    
    if '|' in args.text:
        top, bottom = args.text.split('|', 1)
    else:
        words = args.text.split()
        mid = len(words) // 2
        top, bottom = " ".join(words[:mid]), " ".join(words[mid:])
    
    if args.image:
        src = os.path.join(config.DIR_PROCESSED_IMAGES, args.image)
    else:
        imgs = [f for f in os.listdir(config.DIR_PROCESSED_IMAGES) if f.lower().endswith(('.jpg', '.png'))]
        if not imgs: return
        src = os.path.join(config.DIR_PROCESSED_IMAGES, random.choice(imgs))
    res = processor.create_meme(src, top, bottom)
    if res: logging.info(f"Создан: {res}")

def run_process_images(args):
    logging.info(f"--- ОБРАБОТКА ИЗОБРАЖЕНИЙ ---")
    processor = MemeImageProcessor(
        processed_dir=config.DIR_PROCESSED_IMAGES
    )
    processor.process_folder(args.input_dir, target_size=config.PROC_TARGET_SIZE)

def main():
    
    mode = config.RUN_MODE.lower()
    if mode == 'cli':
        
        parser = argparse.ArgumentParser(description="Meme Factory AI")
        subparsers = parser.add_subparsers(dest="mode", required=True)
        
        p1 = subparsers.add_parser("finetune")
        p1.add_argument("-m", "--model", default=config.TRAIN_BASE_MODEL)
        p1.add_argument("-f", "--file", default=config.TRAIN_DATASET_FILE)
        p1.add_argument("-s", "--save_loc", default=config.TRAIN_OUTPUT_NAME)
        p1.add_argument("--epochs", type=int, default=config.TRAIN_EPOCHS)
        p1.add_argument("--lr", type=float, default=config.TRAIN_LEARNING_RATE)
        p1.add_argument("--batch_size", type=int, default=config.TRAIN_BATCH_SIZE)
        p1.set_defaults(func=run_finetune)
        
        p2 = subparsers.add_parser("generate")
        p2.add_argument("-m", "--model", default=config.GEN_MODEL_PATH)
        p2.add_argument("-a", "--amount", type=int, default=config.GEN_AMOUNT)
        p2.add_argument("-f", "--file", default=config.GEN_PROMPT_FILE)
        p2.add_argument("--base_prompt", default=config.GEN_BASE_PROMPT)
        p2.add_argument("--add_random", action="store_true", default=config.GEN_ADD_RANDOM_WORD)
        p2.add_argument("--save_images", action="store_true", default=config.GEN_SAVE_IMAGES)
        
        p2.set_defaults(func=run_generate, temp_range=config.GEN_TEMP_RANGE)
        
        p3 = subparsers.add_parser("make")
        p3.add_argument("-t", "--text", required=True)
        p3.add_argument("-i", "--image", default=None)
        p3.set_defaults(func=run_make_manual)
        
        p4 = subparsers.add_parser("process")
        p4.add_argument("-i", "--input_dir", default=config.DIR_RAW_IMAGES)
        p4.set_defaults(func=run_process_images)
        args = parser.parse_args()
        args.func(args)
    else:
        
        logging.info(f"Запуск из IDE в режиме: {mode.upper()}")
        if mode == 'finetune':
            
            args = SimpleNamespace(
                model=config.TRAIN_BASE_MODEL,
                file=config.TRAIN_DATASET_FILE,
                save_loc=config.TRAIN_OUTPUT_NAME,
                epochs=config.TRAIN_EPOCHS,
                lr=config.TRAIN_LEARNING_RATE,
                batch_size=config.TRAIN_BATCH_SIZE
            )
            run_finetune(args)
        elif mode == 'generate':
            args = SimpleNamespace(
                model=config.GEN_MODEL_PATH,
                amount=config.GEN_AMOUNT,
                file=config.GEN_PROMPT_FILE,
                base_prompt=config.GEN_BASE_PROMPT,
                add_random=config.GEN_ADD_RANDOM_WORD,
                save_images=config.GEN_SAVE_IMAGES,
                temp_range=config.GEN_TEMP_RANGE
            )
            run_generate(args)
        elif mode == 'make_meme':
            args = SimpleNamespace(
                text=config.MANUAL_TEXT,
                image=config.MANUAL_IMAGE
            )
            run_make_manual(args)
        elif mode == 'process_images':
            args = SimpleNamespace(
                input_dir=config.DIR_RAW_IMAGES
            )
            run_process_images(args)
        else:
            logging.error(f"Неизвестный режим в config.py: {mode}")

if __name__ == "__main__":
    main()
