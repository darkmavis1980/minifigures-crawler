import scrapy
import requests
import os
import json

class BrickSetSpider(scrapy.Spider):
    name = "brickset_spider"
    start_urls = ['https://brickset.com/sets/theme-Collectable-Minifigures/page-1']

    custom_settings = {
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'USER_AGENT': 'custom-parser (https://160iso.com)'
    }

    def start_requests(self):
        urls = ['https://brickset.com/sets/theme-Collectable-Minifigures/page-{}'.format(x) for x in range(1, 32)]
        # urls = [
        #     'https://brickset.com/sets/theme-Collectable-Minifigures/page-1',
        #     'https://brickset.com/sets/theme-Collectable-Minifigures/page-2',
        # ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        SET_SELECTOR = '.set'
        for brickset in response.css(SET_SELECTOR):
            NAME_SELECTOR = 'h1 a::text'
            name = brickset.css(NAME_SELECTOR).get()
            if not name.startswith(' LEGO Minifigures', ' Collectable Minifigures series'):
                image = brickset.css('.mainimg img').attrib['src']
                link = "https://brickset.com{}".format(brickset.css('h1 a').attrib['href'])
                tags = brickset.css('.col .tags a::text').get()
                minifigId = brickset.css('.meta .tags a::text').get()
                series = brickset.css('.meta .tags .subtheme::text').get()
                year = brickset.css('.meta .tags .year::text').get()

                imageFileName = image.split('?')[0].split('/')[-1]
                '''
                Save Image file
                '''
                imageDir = "images/{}".format(series.strip())
                imageRequest = requests.get(image)

                if not os.path.exists(imageDir):
                    os.makedirs(imageDir)

                with open("{}/{}-{}".format(imageDir, tags, imageFileName), 'wb') as imageFile:
                    imageFile.write(imageRequest.content)
                '''
                Save JSON file
                '''
                dataDir = "data/{}".format(series.strip())
                if not os.path.exists(dataDir):
                    os.makedirs(dataDir)
                minifigSet = {
                    'name': name,
                    'minifigId': minifigId,
                    'link': link,
                    'image': image,
                    'imageFileName': imageFileName,
                    'tags': tags,
                    'series': series,
                    'year': year
                }

                minifigJson = json.dumps(minifigSet)

                with open("{}/{}-{}.json".format(dataDir, tags, minifigId), 'w') as outJson:
                    outJson.write(minifigJson)

                yield {
                    'name': name,
                    'minifigId': minifigId,
                    'link': link,
                    'image': image,
                    'imageFileName': imageFileName,
                    'tags': tags,
                    'series': series,
                    'year': year
                }
