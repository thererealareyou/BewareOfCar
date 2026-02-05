import os
import uuid
import random
from PIL import Image, ImageDraw, ImageFont


class MemeImageProcessor:
    def __init__(self, font_path='impact.ttf', output_meme_dir='memes', processed_dir='processed_images'):
        """
        Инициализация процессора изображений.
        :param font_path: Путь к файлу шрифта (.ttf).
        :param output_meme_dir: Папка для сохранения готовых мемов.
        :param processed_dir: Папка для сохранения подготовленных (обрезанных) картинок.
        """
        self.font_path = font_path
        self.output_meme_dir = output_meme_dir
        self.processed_dir = processed_dir
        
        os.makedirs(self.output_meme_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
    
    def prepare_image(self, input_path: str, target_size: tuple = (400, 400)) -> str:
        """
        Обрезает изображение по центру и изменяет размер до target_size.
        Сохраняет результат в self.processed_dir.
        Возвращает путь к обработанному файлу.
        """
        filename = os.path.basename(input_path)
        output_path = os.path.join(self.processed_dir, filename)
        try:
            with Image.open(input_path) as img:
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                width, height = img.size
                min_dim = min(width, height)
                
                left = (width - min_dim) // 2
                top = (height - min_dim) // 2
                right = (width + min_dim) // 2
                bottom = (height + min_dim) // 2
                cropped_img = img.crop((left, top, right, bottom))
                resized_img = cropped_img.resize(target_size, Image.LANCZOS)
                resized_img.save(output_path, quality=95)
                return output_path
        except Exception as e:
            print(f"Ошибка при обработке {input_path}: {e}")
            return None
    def process_folder(self, input_dir: str, target_size: tuple = (400, 400)):
        """
        Пакетная обработка всех изображений в папке.
        """
        if not os.path.exists(input_dir):
            print(f"Папка {input_dir} не найдена.")
            return
        supported_formats = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
        processed_count = 0
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(supported_formats):
                input_path = os.path.join(input_dir, filename)
                if self.prepare_image(input_path, target_size):
                    processed_count += 1
        print(f"Обработано изображений: {processed_count}")
    
    def create_meme(self, image_path: str, top_text: str = "", bottom_text: str = "") -> str:
        """
        Создает мем из изображения, накладывая текст сверху и снизу.
        Возвращает путь к сохраненному файлу мема.
        """
        if not os.path.exists(image_path):
            print(f"Файл не найден: {image_path}")
            return None
        try:
            with Image.open(image_path) as img:
                
                
                img = img.convert('RGB')
                canvas = ImageDraw.Draw(img)
                max_width = int(img.width * 0.9)  
                if top_text:
                    self._draw_text_block(img, canvas, top_text, max_width, position='top')
                if bottom_text:
                    self._draw_text_block(img, canvas, bottom_text, max_width, position='bottom')
                
                output_filename = self._make_unique_filename(os.path.basename(image_path))
                output_path = os.path.join(self.output_meme_dir, output_filename)
                img.save(output_path)
                return output_path
        except Exception as e:
            print(f"Ошибка при создании мема: {e}")
            return None
    
    def _draw_text_block(self, img, canvas, text, max_width, position='top'):
        """Рисует блок текста (верхний или нижний)."""
        if not text: return
        
        font_size = self._calculate_font_size(img, text, max_width)
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except IOError:
            
            print(f"Шрифт {self.font_path} не найден, используется стандартный.")
            font = ImageFont.load_default()
        
        wrapped_lines = self._wrap_text(text.upper(), font, max_width)
        
        line_height = font.size + 5  
        total_text_height = line_height * len(wrapped_lines)
        if position == 'top':
            y = 10
        else:  
            y = img.height - total_text_height - 10
        stroke_width = max(2, int(font_size / 15))  
        
        for line in wrapped_lines:
            
            text_width = font.getlength(line)
            x = (img.width - text_width) / 2
            self._draw_text_with_outline(canvas, line, (x, y), font, stroke_width)
            y += line_height
    def _calculate_font_size(self, img, text, max_width):
        """Подбирает размер шрифта, чтобы текст влезал (упрощенная и ускоренная логика)."""
        
        base_size = int(img.height / 8)
        if len(text) > 20: base_size = int(img.height / 12)
        if len(text) > 50: base_size = int(img.height / 18)
        
        
        
        font_size = base_size
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except:
            return 20
        
        
        return font_size
    def _wrap_text(self, text, font, max_width):
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            
            test_line = f"{current_line} {word}".strip()
            if font.getlength(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines
    def _draw_text_with_outline(self, canvas, text, position, font, stroke_width):
        x, y = position
        fill_color = "white"
        stroke_color = "black"
        
        canvas.text((x - stroke_width, y - stroke_width), text, font=font, fill=stroke_color)
        canvas.text((x + stroke_width, y - stroke_width), text, font=font, fill=stroke_color)
        canvas.text((x - stroke_width, y + stroke_width), text, font=font, fill=stroke_color)
        canvas.text((x + stroke_width, y + stroke_width), text, font=font, fill=stroke_color)
        
        
        
        canvas.text((x, y), text, font=font, fill=fill_color)
    def _make_unique_filename(self, filename):
        unique_id = uuid.uuid4().hex[:8]  
        base, ext = os.path.splitext(filename)
        return f"{base}_{unique_id}{ext}"
