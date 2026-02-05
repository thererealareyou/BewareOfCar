import requests
import time
import logging
import os
import random
from datetime import datetime, timedelta

BOT_TOKEN = '123123'  
CHANNEL_ID = '@BewareOfCarNeural'
IMAGE_FOLDER = r"C:\Users\Valera\PycharmProjects\FineTuneTest\memes\cropped_originals"  
STATE_FILE = "last_run.txt"  
INTERVAL_HOURS = 48  

logging.basicConfig(
    filename='telegram_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_last_run_time():
    """Читает время последнего запуска из файла."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, 'r') as f:
            timestamp = float(f.read().strip())
            return datetime.fromtimestamp(timestamp)
    except Exception:
        return None

def save_last_run_time():
    """Сохраняет текущее время в файл."""
    with open(STATE_FILE, 'w') as f:
        f.write(str(datetime.now().timestamp()))

def send_message():
    try:
        ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

        if not os.path.exists(IMAGE_FOLDER):
            logging.error(f"Папка не найдена: {IMAGE_FOLDER}")
            return False

        images = [
            f for f in os.listdir(IMAGE_FOLDER)
            if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
        ]

        if not images:
            logging.error("Нет изображений в указанной папке")
            return False

        random_image = random.choice(images)
        image_path = os.path.join(IMAGE_FOLDER, random_image)

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

        
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': CHANNEL_ID}
            
            response = requests.post(url, files=files, data=data, timeout=30)

        response.raise_for_status()

        
        os.remove(image_path)
        save_last_run_time()
        logging.info(f"Успешно отправлено и удалено: {random_image}")
        return True

    except Exception as e:
        logging.error(f"Ошибка в процессе отправки: {str(e)}")
        return False

def main_loop():
    logging.info("Бот запущен.")
    while True:
        last_run = get_last_run_time()

        should_post = False

        if last_run is None:
            
            should_post = True
            logging.info("Первый запуск, отправка сообщения...")
        else:
            
            time_passed = datetime.now() - last_run
            if time_passed > timedelta(hours=INTERVAL_HOURS):
                should_post = True
                logging.info(f"Прошло {time_passed}, пора отправлять.")
            else:
                
                time_left = timedelta(hours=INTERVAL_HOURS) - time_passed
                
                

        if should_post:
            success = send_message()
            if not success:
                
                
                logging.warning("Отправка не удалась, повтор через 1 час.")
                time.sleep(3600)
                continue

        
        
        time.sleep(3600)

if __name__ == "__main__":
    main_loop()
