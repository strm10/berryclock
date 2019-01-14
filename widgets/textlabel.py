from . import WidgetBase
from PIL import Image, ImageDraw, ImageFont
import datetime


class TextLabel(WidgetBase):
    """
    setting parameters:
    - text (required)
    - font (required)
    - font_size (optional)
    - text_position (optional), either of ['center', 'left', 'right']
    """
    def draw(self):
        self.draw_text(self.settings.get('text', ''))

    def draw_text(self, text):
        images = [Image.new('1', self.expected_size, 255) for _ in range(2)]
        font = ImageFont.truetype(self.settings.get('font', ''),
                                  int(self.settings.get('font_size', self.expected_size[1]*0.8)))
        draw = ImageDraw.Draw(images[0])
        w, h = draw.textsize(text, font=font)
        x = int((self.expected_size[0]-w)/2)  # centering
        if self.settings.get('text_position', None) == 'left':
            x = 0
        elif self.settings.get('text_position', None) == 'right':
            x = self.expected_size[0]-w
        draw.text((x, int((self.expected_size[1]-h)/2)), text, font=font, fill=0)
        return images
        

class TimeStampLabel(TextLabel):
    """
    setting parameters:
    - text (required), placeholders for strftime() can be contained
    - font (required)
    - font_size (optional)
    - text_position (optional), either of ['center', 'left', 'right']
    """
    def draw(self):
        return self.draw_text(datetime.datetime.now().strftime(self.settings.get('text', '')))
