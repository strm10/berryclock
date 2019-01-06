"""
Widgets using Direction API on Google Maps Platform
"""

from . import WidgetBase
from PIL import Image, ImageDraw, ImageFont
import requests
import json
import logging

log = logging.getLogger('googlemaps_direction')

class RouteDuration(WidgetBase):
    """
    setting parameters:
    - api_key (required)
    - origin (required)
    - destination (required)
    - font (required)
    - font_size (optional)
    - mode (optional), either of ['driving', 'walking', 'bicycling', 'transit']
    - destinaion_label (optional)
    """
    def draw(self):
        origin = self.settings.get('origin', '')
        destination = self.settings.get('destination', '')
        api_key = self.settings.get('api_key', '')
        # either of ['driving', 'walking', 'bicycling', 'transit']
        mode = self.settings.get('mode', 'driving')
        if len(origin) == 0 or len(destination) == 0 or len(api_key) == 0:
            log.warning('one or more parameters are missing: "origin", "destination", "api_key"')
            return None
        
        url = 'https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&key=%s&mode=%s&departure_time=now' % (origin, destination, api_key, mode)
        response = requests.get(url)
        data = response.json()
        # data['routes'][i]['legs'][j]['duration_in_traffic']['value']
        duration_list = [[leg['duration_in_traffic']['value'] for leg in route['legs']] for route in data['routes']]
        min_duration = round(min([min(tmp) for tmp in duration_list])/60)
        min_duration_str = str(min_duration)
        
        destination_label = self.settings.get('destination_label', '')
        if len(destination_label) > 0:
            destination_label = ' to ' + destination_label
        post_str = ' min' + destination_label
            
        images = [Image.new('1', self.expected_size, 255) for i in range(2)]
        draw = ImageDraw.Draw(images[0])

        font_size_duration = self.settings.get('font_size', int(self.expected_size[1]*0.8))
        font_size_unit = int(font_size_duration*0.67)
        font_duration = ImageFont.truetype(self.settings.get('font', ''), font_size_duration)
        font_unit = ImageFont.truetype(self.settings.get('font', ''), font_size_unit)
        w0, h0 = draw.textsize(min_duration_str, font=font_duration)
        w1, h1 = draw.textsize(post_str, font=font_unit)
        draw.text((0, 0), min_duration_str, font=font_duration)
        draw.text((w0, font_size_duration-font_size_unit), post_str, font=font_unit)
        
        return images
