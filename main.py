import argparse
import text_generator
import trainer
import image_creator
import os
import random


def mode_a(args):  # finetune
    trainer.train_model(args.model, args.file, args.save_loc)


def mode_b(args):  # generate
    print(f"Генерация: Модель={args.model}, Количество предложений={args.amount}")
    texts = text_generator.use_trained_model(model_name=args.model, amount_of_sentences=args.amount)

    IMAGE_FOLDER = "cropped_originals/"
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    images = [
        f for f in os.listdir(IMAGE_FOLDER)
        if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    ]

    for text in texts:
        try:
            image_creator.draw_meme(os.path.join(IMAGE_FOLDER, random.choice(images)), text[0], text[1])
        except FileNotFoundError:
            ...

def mode_b_manual(model, amount):  # generate
    print(f"Генерация: Модель={model}, Количество предложений={amount}")
    texts = text_generator.use_trained_model(model_name=model, amount_of_sentences=amount)

    IMAGE_FOLDER = "cropped_originals/"
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    images = [
        f for f in os.listdir(IMAGE_FOLDER)
        if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    ]

    for text in texts:
        try:
            image_creator.draw_meme(os.path.join(IMAGE_FOLDER, random.choice(images)), text[0], text[1])
        except FileNotFoundError:
            ...


def mode_c(args):  # make
    text = text_generator.split_sentence(args.text)
    IMAGE_FOLDER = "cropped_originals/"
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    images = [
        f for f in os.listdir(IMAGE_FOLDER)
        if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    ]
    image_creator.draw_meme(os.path.join(IMAGE_FOLDER, random.choice(images)), text[0], text[1])


def main():
    parser = argparse.ArgumentParser(description="Программа для генерации текстов и мемов."
                                                 "\nТекущая SotA: fine_tuned_model_nietzcshe_neural_main")

    # Субпарсеры для разных режимов
    subparsers = parser.add_subparsers(dest="mode", help="Режимы работы программы")

    # Режим A
    parser_a = subparsers.add_parser("finetune", help="Файнтьюн выбранной модели на выбранном корпусе")
    parser_a.add_argument("-m", "--model", type=str, required=True, help="Модель-база")
    parser_a.add_argument("-f", "--file", type=str, required=True, help="Корпус текстов (.csv, первая строка - text)")
    parser_a.add_argument("-s", "--save_loc", type=str, required=True, help="Имя итоговой модели")
    parser_a.set_defaults(func=mode_a)

    # Режим B
    parser_b = subparsers.add_parser("generate", help="Генерация мемов")
    parser_b.add_argument("-m", "--model", type=str, required=True, help="Модель-база")
    parser_b.add_argument("-a", "--amount", type=int, required=True, help="Количество мемов")
    parser_b.set_defaults(func=mode_b)

    # Режим C
    parser_c = subparsers.add_parser("make", help="Создание своего мема")
    parser_c.add_argument("-t", "--text", type=str, required=True, help="Текст")
    parser_c.set_defaults(func=mode_c)

    # Парсинг аргументов
    args = parser.parse_args()

    # Вызов соответствующей функции в зависимости от режима
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    mode_b_manual(model='nietzcshe_neural_nausea', amount=15)
