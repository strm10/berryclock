#!/usr/bin/env python3

import argparse
import copy
import importlib
import json
import logging
import sys
import time
from PIL import Image, ImageOps

try:
    import epd7in5b as epd
except:
    import epddummy as epd  # for debugging on non-rpi env

NUM_COLOR_CHANNELS = 2
COLOR_LIST = [(0, 0, 0), (255, 0, 0)]
log = logging.getLogger('berryclock')


class Widget:
    __slots__ = ['module_name', 'class_name', 'origin', 'size', 'instance']
    def __init__(self, module_name, class_name, origin, size, instance):
        self.module_name = module_name
        self.class_name = class_name
        self.origin = origin
        self.size = size
        self.instance = instance

        
class BerryClock:
    def __init__(self, config, test_mode):
        self.widgets = None
        self.config = None
        self.test_mode = None
        
        self.init(config, test_mode)

    def init(self, config, test_mode):
        self.widgets = []
        self.config = config
        self.test_mode = test_mode

        # load modules
        for widget_config in self.config.get('widgets', []):
            if not widget_config.get('enabled', True):
                continue
            if len(widget_config.get('module', '')) == 0:
                log.warning('module name is not given, ignoring: %r' % widget_config)
                continue
            settings = copy.deepcopy(self.config.get('common_settings', {}))
            settings.update(widget_config.get('settings', {}))
            module_ = importlib.import_module('widgets.' + widget_config['module'])
            module_ = importlib.reload(module_)  # make sure it is the one for the channel
            class_ = getattr(module_, widget_config.get('class', ''))
            inst = class_(settings, widget_config.get('size', [0, 0]))
            widget = Widget(widget_config['module'], widget_config['class'], widget_config['origin'], widget_config['size'], inst)
            self.widgets.append(widget)
            log.info('Loaded %s.%s, origin=%r, size=%r' % (widget.module_name, widget.class_name, widget.origin, widget.size))

            
    def run(self):
        if self.test_mode:
            images = self._generate_image()
            colorImages = [ImageOps.colorize(image.convert('L'), black=color, white=(255, 255, 255)) for image, color in zip(images, COLOR_LIST)]
            image = Image.composite(colorImages[0], colorImages[1], images[1])
            image.save('test.png')
            
        else:
            update_interval = self.config.get('update_interval', 0)
            epaper = epd.EPD()
            while True:
                time_begin = time.time()
                log.info('generating image')
                images = self._generate_image()
                buf = [epaper.getbuffer(image) for image in images]
                log.info('updating e-paper')
                epaper.init()
                epaper.display(*buf)
                epaper.sleep()
                time_elapsed = time.time() - time_begin
                log.info('update done. elapsed: %f sec' % time_elapsed)
                if update_interval == -1:
                    return
                if time_elapsed < update_interval:
                    time.sleep(update_interval - time_elapsed)
                

    def _generate_image(self):
        images = [Image.new('1', (epd.EPD_WIDTH, epd.EPD_HEIGHT), 255) for _ in range(NUM_COLOR_CHANNELS)]
        for widget in self.widgets:
            widget_images = widget.instance.draw()
            if widget_images is None:
                continue
            for image, widget_image in zip(images, widget_images):
                image.paste(widget_image, (widget.origin[0], widget.origin[1], widget.origin[0]+widget.size[0], widget.origin[1]+widget.size[1]))
        return images
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, nargs=1, required=True)
    parser.add_argument('--test', dest='testmode', action='store_true')

    args = parser.parse_args()
    config = {}
    with open(args.config[0]) as f:
        config = json.load(f)
    berry_clock = BerryClock(config, args.testmode)
    berry_clock.run()
