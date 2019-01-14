import datetime
from . import WidgetBase
from PIL import Image, ImageDraw, ImageFont


class Date(WidgetBase):
    def draw(self):
        today = datetime.date.today()
        text = today.strftime('%A, %-d %B %Y')

        font = ImageFont.truetype(self.settings.get('font', ''), int(self.expected_size[1]*0.75))

        # black and red
        images = [Image.new('1', self.expected_size, 255) for _ in range(2)]
        draw = ImageDraw.Draw(images[0 if today.weekday() < 5 else 1])
        w, h = draw.textsize(text, font=font)
        draw.text(((self.expected_size[0]-w)/2, (self.expected_size[1]-h)/2), text, font=font, fill=0)

        return images
