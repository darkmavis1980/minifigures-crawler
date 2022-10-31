import scrapy
import requests
import os

class BrickSetSpider(scrapy.Spider):
    name = "brickset_spider"
    start_urls = ['https://brickset.com/sets/theme-Collectable-Minifigures/page-1']

    custom_settings = {
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'USER_AGENT': 'custom-parser (https://160iso.com)'
    }

    def start_requests(self):
        urls = ['https://brickset.com/sets/theme-Collectable-Minifigures/page-{}'.format(x) for x in range(1, 4)]
        # urls = [
        #     'https://brickset.com/sets/theme-Collectable-Minifigures/page-1',
        #     'https://brickset.com/sets/theme-Collectable-Minifigures/page-2',
        # ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # page = response.url.split("/")[-1]
        # filename = f'quotes-{page}.html'
        # print(response.body)

        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log(f'Saved file {filename}')

        SET_SELECTOR = '.set'
        for brickset in response.css(SET_SELECTOR):
            NAME_SELECTOR = 'h1 a::text'
            name = brickset.css(NAME_SELECTOR).get()
            if not name.startswith(' LEGO Minifigures'):
                image = brickset.css('.mainimg img').attrib['src']
                tags = brickset.css('.col .tags a::text').get()
                series = brickset.css('.meta .tags .subtheme::text').get()

                imageFileName = image.split('?')[0].split('/')[-1]
                imageDir = "images/{}".format(series)
                imageRequest = requests.get(image)

                if not os.path.exists(imageDir):
                    os.makedirs(imageDir)

                with open("{}/{}-{}".format(imageDir, tags, imageFileName), 'wb') as f:
                    f.write(imageRequest.content)
                yield {
                    'name': name,
                    'image': image,
                    'imageFileName': imageFileName,
                    'tags': tags,
                    'series': series
                }
