import datetime
from . import WidgetBase
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import xml.etree.ElementTree as ET


class Rss(WidgetBase):
    @staticmethod
    def get_rss(url):
        title = None
        pub_date = None
        item_list = []
        
        response = requests.get(url)
        root = ET.fromstring(response.content)
        if root.tag != 'rss':
            log.warning('retrieved RSS data with unexpected root tag: %s' % root.tag)
            return None
        for child in root.getchildren():
            if child.tag != 'channel':
                continue
            for child2 in child.getchildren():
                if child2.tag == 'title':
                    title = child2.text
                elif child2.tag == 'pubDate':
                    pub_date = child2.text
                elif child2.tag == 'item':
                    for child3 in child2.getchildren():
                        if child3.tag == 'title':
                            item_list.append(child3.text)
        
        return {'title': title, 'pub_date': pub_date, 'item_list': item_list}
        
    
    def draw(self):
        images = [Image.new('1', self.expected_size, 255) for i in range(2)]
        rss = Rss.get_rss('https://news.yahoo.co.jp/pickup/rss.xml')

        num_max_items = self.settings.get('num_max_items', 10)
        line_height = int(self.expected_size[1] / (num_max_items+1))
        font_size = int(line_height*0.6)
        num_items = min(len(rss['item_list']), num_max_items)
        
        if rss is None:
            return images

        # black and red
        draw = ImageDraw.Draw(images[0])
        font = ImageFont.truetype(self.settings.get('font', ''), font_size)
        draw.text((0, 0), self.settings.get('title', rss['title'] if rss['title'] is not None else ''), font=font)
        font = ImageFont.truetype(self.settings.get('content_font', self.settings.get('font', '')), font_size)
        for i, item in enumerate(rss['item_list'][:num_items]):
            draw.text((0, (i+1)*line_height), ' - ' + item, font=font)

        return images
