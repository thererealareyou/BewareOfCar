import os
from PIL import Image
from argparse import ArgumentParser


def process_image(input_path, output_path, target_size=(400, 400)):
    try:
        with Image.open(input_path) as img:
            width, height = img.size
            min_dim = min(width, height)
            left = (width - min_dim) // 2
            top = (height - min_dim) // 2
            right = (width + min_dim) // 2
            bottom = (height + min_dim) // 2

            cropped_img = img.crop((left, top, right, bottom))
            resized_img = cropped_img.resize(target_size, Image.LANCZOS)
            resized_img.save(output_path)

    except Exception as e:
        print(f"Ошибка при обработке {input_path}: {str(e)}")


def process_folder(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    supported_formats = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            process_image(input_path, output_path)
            print(f"Обработано: {filename}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Обработчик изображений 400x400")
    parser.add_argument("-i", "--input", required=True, help="Входная папка")
    parser.add_argument("-o", "--output", required=True, help="Выходная папка")
    args = parser.parse_args()

    process_folder(args.input, args.output)
    print("Обработка завершена!")