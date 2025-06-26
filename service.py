import requests
import time
import logging
import os
import random
from datetime import datetime


BOT_TOKEN = '' # Вставьте свой токен
CHANNEL_ID = '' # Вставьте свой ID
SLEEP_MINUTES = 180

logging.basicConfig(
    filename='telegram_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def send_message():
    try:
        IMAGE_FOLDER = "C:/Users/Valera/PycharmProjects/FineTuneTest/memes/cropped_originals/"
        ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

        images = [
            f for f in os.listdir(IMAGE_FOLDER)
            if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
        ]

        if not images:
            logging.error("Нет изображений в указанной папке")
            return False

        random_image = random.choice(images)
        image_path = os.path.join(IMAGE_FOLDER, random_image)

        caption = f"Автоматическое изображение {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': CHANNEL_ID}  # , 'caption': caption
            response = requests.post(url, files=files, data=data)

        response.raise_for_status()

        os.remove(image_path)
        logging.info(f"Отправлено и удалено изображение: {random_image}")
        return True

    except Exception as e:
        logging.error(f"Ошибка при отправке или удалении изображения: {e}")
        return False

    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        return False


if __name__ == "__main__":
    while True:
        send_message()
        time.sleep(SLEEP_MINUTES * 60)