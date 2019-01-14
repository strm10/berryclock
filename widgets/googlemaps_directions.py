"""
Widgets using Directions API on Google Maps Platform
"""

from . import WidgetBase
from PIL import Image, ImageDraw, ImageFont
import requests
import logging

log = logging.getLogger('googlemaps_directions')


def get_duration_in_traffic(origin, destination, key, mode):
    """
    Returns route duration in traffic in seconds.
    """
    url = 'https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&key=%s&mode=%s&departure_time=now' % (origin, destination, key, mode)
    response = requests.get(url)
    data = response.json()
    # data['routes'][i]['legs'][j]['duration_in_traffic']['value']
    duration_list = [[leg['duration_in_traffic']['value'] for leg in route['legs']] for route in data['routes']]
    return min([min(tmp) for tmp in duration_list])
    

class RouteDuration(WidgetBase):
    """
    setting parameters:
    - api_key (required)
    - origin (required)
    - destination (required)
    - font (required)
    - font_size (optional)
    - mode (optional), options: ['driving', 'walking', 'bicycling', 'transit']
    - destination_label (optional)
    """
    def draw(self):
        # read settings
        origin = self.settings.get('origin', '')
        destination = self.settings.get('destination', '')
        api_key = self.settings.get('api_key', '')
        mode = self.settings.get('mode', 'driving')
        font_size_duration = self.settings.get('font_size', int(self.expected_size[1]*0.8))
        destination_label = self.settings.get('destination_label', '')  # adds "to somewhere" after "x min"
        if len(origin) == 0 or len(destination) == 0 or len(api_key) == 0:
            log.warning('one or more parameters are missing: "origin", "destination", "api_key"')
            return None

        # duration string
        min_duration_str = str(round(get_duration_in_traffic(origin, destination, api_key, mode)/60))

        # following string
        post_str = ' min'
        if len(destination_label) > 0:
            post_str += ' to ' + destination_label
            
        # draw "x min( to blah)"
        images = [Image.new('1', self.expected_size, 255) for _ in range(2)]
        draw = ImageDraw.Draw(images[0])
        font_size_unit = int(font_size_duration*0.67)
        font_duration = ImageFont.truetype(self.settings.get('font', ''), font_size_duration)
        font_unit = ImageFont.truetype(self.settings.get('font', ''), font_size_unit)
        w0, h0 = draw.textsize(min_duration_str, font=font_duration)
        draw.text((0, 0), min_duration_str, font=font_duration)
        draw.text((w0, font_size_duration-font_size_unit), post_str, font=font_unit)
        
        return images
