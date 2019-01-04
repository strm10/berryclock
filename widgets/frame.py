from . import WidgetBase
from PIL import Image, ImageDraw, ImageFont

class Frame(WidgetBase):
    def draw(self):
        images = [Image.new('1', self.expected_size, 255) for i in range(2)]
        draw = ImageDraw.Draw(images[0])
        for line in self.settings.get('lines', []):
            draw.line(line)
        return images
