from . import WidgetBase
from PIL import Image, ImageDraw, ImageFont
import datetime
import io
import requests


class ShutokoTraffic(WidgetBase):
    palette = [
        140, 140, 140,  # road
        3, 130, 40,  # road id sign
        210, 210, 210,  # Yaesu line
        50, 140, 200,  # sea
        230, 230, 230,  # land
        245, 165, 0,  # traffic
        245, 0, 0,  # heavy traffic
    ]
    palette += [255] * (256*3 - len(palette))
    
    def draw(self):
        response = requests.get('https://stkengstorage.blob.core.windows.net/kiseimap/kisei-sp.gif')
        
        src = Image.open(io.BytesIO(response.content))
        #src = Image.open('kisei-sp.gif')
        size = (326, 306)
        origin = (48, 163)
        src = src.crop((origin[0], origin[1], origin[0]+size[0], origin[1]+size[1]))

        srcP = Image.new('P', src.size)
        srcP.putpalette(ShutokoTraffic.palette)
        srcP = src.convert('RGB').quantize(method=0, palette=srcP)
        srcP = srcP.resize(tuple(self.expected_size))

        draw = ImageDraw.Draw(srcP)
        draw.rectangle([0, 260, 73, 325], fill=7)
        draw.rectangle([0, 0, 20, 20], fill=7)
        
        # black and red
        images = [Image.new('1', self.expected_size, 255) for i in range(2)]
        images[0] = srcP.point(lambda x: 0 if x in [0, 1] else 255, mode='1')
        images[1] = srcP.point(lambda x: 0 if x in [5, 6] else 255, mode='1')

        return images
