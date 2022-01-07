# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from collections import OrderedDict


class dfsSpider(scrapy.Spider):

	name = "worlddutyfree"

	use_selenium = True
	domain = 'http://uk.worlddutyfree.com'
	total_count = 0
	categories_data = None
	result_data_list = {}
	# custom_settings = {
	#     'CONCURRENT_REQUESTS': 8,
	#     'DOWNLOAD_DELAY': 0.3,
	#     'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
	#     'CONCURRENT_REQUESTS_PER_IP': 4
	# }

	headers = ['PageUrl', 'ProductLink', 'ImageLink', 'Rarity', 'ProductTitle', 'NewQty', 'NewPrice', 'NewContent', 'NearMintQty', 'NearMintPrice', 'NearMintContent',
			   'FoilNearMintQty', 'FoilNearMintPrice', 'FoilNearMintContent',
			   'PlayedQty', 'PlayedPrice', 'PlayedContent', 'FoilPlayedQty', 'FoilPlayedPrice', 'FoilPlayedContent', 'SetName']


###########################################################

	def __init__(self, *args, **kwargs):
		super(dfsSpider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		n = 1
		yield scrapy.Request(url='http://uk.worlddutyfree.com', callback=self.parse_category)

	def parse_category(self, response):
		cats = response.xpath('//nav[@id="nav"]//ul[@class="sub-menucon level1"]/li/a/@href').extract()
		if len(cats) > 0:
			# for url in cats:
			# 	yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': url})

			###############---- test ------------------##################
			# url = '/en/hong-kong/brands/giorgio-armani'
			yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProductList, dont_filter=True, meta={'basic_url': cats[0], 'next_count': 1})
			#############################################################################

	def parseProductList(self, response):
		cats = response.xpath('//div[@class="product-list"]//li[@class="item"]//a[@class="product-image"]/@href').extract()
		if len(cats) > 0:
			# for cat in cats:
			# 	yield scrapy.Request(url=response.urljoin(cat), callback=self.parseProduct, dont_filter=True)

			###############---- test ------------------##################
			# test_url = '/en/hong-kong/brands/giorgio-armani/38043931/lip-maestro-405-sultan?q=:blprelevance&page=4&text='
			# yield scrapy.Request(url=response.urljoin(test_url), callback=self.parseProduct)
			#############################################################################
			next_count = response.meta['next_count'] + 1
			next_url = response.meta['basic_url'] + '#esp_pg={}'.format(str(next_count))
			yield scrapy.Request(url=response.urljoin(next_url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': response.meta['basic_url'], 'next_count': next_count})


	def parseProduct(self, response):
		item = OrderedDict()
		self.total_count += 1
		item['Serial'] = self.total_count
		item['Platform URL'] = self.domain
		item['Product Name'] = response.xpath('//div[@itemprop="name title="]/text()').extract_first()

		item['Product Price'] = ''
		price_temp = response.xpath('//span[@itemprop="price"]/text()').extract_first()
		item['Product Price'] = price_temp.split(' ')[-1].replace(',', '')
		item['Product Price Currency'] = price_temp.split(' ')[0]

		item['Product Description'] = ''
		desc = response.xpath('//div[@itemprop="description"]/text()').extract_first()
		if desc:
			desc = desc.strip()
			item['Product Description'] = desc

		item['Product Category'] = ''
		# item['Product Category2'] = ''
		# item['Product Category3'] = ''

		cat_list = response.xpath('//li[@itemprop="itemListElement"]/a/span/text()').extract()
		item['Product Category'] = cat_list[-1]
		# for i, val in enumerate(cat_list):
		# 	item['Product Category{}'.format(str(i + 1))] = val

		img_url = response.xpath('//div[@id="ido"]//picture/img/@src').extract_first()
		item['Image URL'] = ''
		if img_url:
			item['Image URL'] = response.urljoin(img_url)

		item['Image URI'] = ''
		if img_url:
			img_url = img_url.split('?')[0]
			item['Image URI'] = img_url.split('/')[-1]
		item['Product URL'] = response.url

		print('\nTotal Count: {}\n'.format(str(item['Serial'])))

		yield item







