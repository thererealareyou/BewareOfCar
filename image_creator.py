def draw_meme(filename, top_text, bot_text):
    from PIL import Image, ImageDraw, ImageFont
    import uuid
    import random
    import os

    def calculate_font_size(img, text, font_path, max_width, min_font_size=20):
        width, height = img.size
        min_font_size = int((width + height) / 30)

        if not text or not isinstance(text, str):
            return min_font_size

        font_size = min_font_size
        font = ImageFont.truetype(font_path, font_size)
        random_multiplier = random.uniform(1.5, 2.0)

        while font.getlength(text) < max_width and font_size < 300:
            font_size += 1
            font = ImageFont.truetype(font_path, int(font_size * random_multiplier))

        return font_size - 1 if font_size > min_font_size else min_font_size

    def wrap_text(text, font, max_width):
        if not text or not isinstance(text, str):
            return []

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

    def draw_text_with_outline(canvas, text, position, font, fill, stroke_width, stroke_fill):
        if not text or not isinstance(text, str):
            return

        x, y = position

        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                canvas.text((x + dx, y + dy), text, font=font, fill=stroke_fill)

        canvas.text((x, y), text, font=font, fill=fill)

    def fill_meme(filename, top_text="", bottom_text="", font_path='impact.ttf', stroke_width=2, stroke_fill='black',
                  fill='white', min_font_size=50):
        with Image.open(filename) as img:
            canvas = ImageDraw.Draw(img)
            max_width = int(img.width * 0.8)

            if top_text and isinstance(top_text, str):
                font_size = calculate_font_size(img, top_text, font_path, max_width, min_font_size)
                font = ImageFont.truetype(font_path, font_size)

                wrapped_lines = wrap_text(top_text.upper(), font, max_width)

                line_height = font.size + 5
                y = 10
                for line in wrapped_lines:
                    x = (img.width - font.getlength(line)) / 2
                    draw_text_with_outline(canvas, line, (x, y), font, fill, int(font_size / 10), stroke_fill)
                    y += line_height

            if bottom_text and isinstance(bottom_text, str):
                font_size = calculate_font_size(img, bottom_text, font_path, max_width, min_font_size)
                font = ImageFont.truetype(font_path, font_size)

                wrapped_lines = wrap_text(bottom_text.upper(), font, max_width)

                line_height = font.size + 5
                y = img.height - (line_height * len(wrapped_lines)) - 10
                for line in wrapped_lines:
                    x = (img.width - font.getlength(line)) / 2
                    draw_text_with_outline(canvas, line, (x, y), font, fill, int(font_size / 10), stroke_fill)
                    y += line_height

            output_filename = make_unique_filename(filename)
            img.save('memes/'+output_filename)
            return output_filename

    def make_unique_filename(filename):
        unique_id = uuid.uuid4().hex
        base, ext = filename.rsplit('.', 1)
        return f"{base}_{unique_id}.{ext}"

    return fill_meme(filename=filename, top_text=top_text, bottom_text=bot_text)