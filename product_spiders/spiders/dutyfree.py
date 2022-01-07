# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from collections import OrderedDict


class dfsSpider(scrapy.Spider):

	name = "dutyfree"

	# use_selenium = False
	domain = 'https://www.dutyfree.com'
	total_count = 0
	categories_data = None
	result_data_list = {}
	custom_settings = {
	    'CONCURRENT_REQUESTS': 8,
	    'DOWNLOAD_DELAY': 0.3,
	    'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
	    'CONCURRENT_REQUESTS_PER_IP': 4
	}

	headers = ['PageUrl', 'ProductLink', 'ImageLink', 'Rarity', 'ProductTitle', 'NewQty', 'NewPrice', 'NewContent', 'NearMintQty', 'NearMintPrice', 'NearMintContent',
			   'FoilNearMintQty', 'FoilNearMintPrice', 'FoilNearMintContent',
			   'PlayedQty', 'PlayedPrice', 'PlayedContent', 'FoilPlayedQty', 'FoilPlayedPrice', 'FoilPlayedContent', 'SetName']


###########################################################

	def __init__(self, *args, **kwargs):
		super(dfsSpider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(url='https://www.dutyfree.com.au/en/', callback=self.parse_category)

	def parse_category(self, response):
		cats = response.xpath('//ul[@class="level0 columns1"]/li/a/@href').extract()
		if len(cats) > 0:
			cats.append('https://www.dutyfree.com.au/en/fashion')
			cats.append('https://www.dutyfree.com.au/en/promotions')
			for url in cats:
				yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'cat': url.replace('https://www.dutyfree.com.au/en/', ''), 'next_count': 1})

			###############---- test ------------------##################
			# url = 'https://www.dutyfree.com.au/en/promotions'
			# yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'next_count': 1})
			#############################################################################

	def parseProductList(self, response):
		cats = response.xpath('//a[@class="product-image product-click-enhanced"]/@href').extract()
		if len(cats) > 0:
			for cat in cats:
				yield scrapy.Request(url=response.urljoin(cat), callback=self.parseProduct, dont_filter=True, meta={'cat': response.meta['cat']})

			###############---- test ------------------##################
			# test_url = '/en/hong-kong/brands/giorgio-armani/38043931/lip-maestro-405-sultan?q=:blprelevance&page=4&text='
			# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProduct)
			# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProduct)
			#############################################################################

			next_count = response.meta['next_count'] + 1
			next_url = response.xpath('//a[@class="next i-next" and @title="Next"]/@href').extract_first()
			if next_url:
				yield scrapy.Request(url=response.urljoin(next_url), callback=self.parseProductList, dont_filter=True, meta={'cat': response.meta['cat'], 'next_count': next_count})


	def parseProduct(self, response):
		item = OrderedDict()
		self.total_count += 1
		item['Serial'] = self.total_count
		item['Platform URL'] = self.domain
		item['Product Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first()

		item['Product Price'] = ''
		price_temp = response.xpath('//div[@class="product-main-info"]//span[@itemprop="price"]/@content').extract()
		item['Product Price'] = price_temp[0].replace(',', '')
		item['Product Price Currency'] = "AUD"

		item['Product Description'] = ''
		desc = response.xpath('//div[@itemprop="description"]/text()').extract()
		if desc:
			new_desc = []
			for d in desc:
				d = d.strip()
				if d:
					new_desc.append(d)
			if new_desc:
			# desc = desc.strip()
				item['Product Description'] = '\n'.join(new_desc)

		item['Product Category'] = ''
		# item['Product Category2'] = ''
		# item['Product Category3'] = ''

		# cat_list = response.xpath('//ol[@class="breadcrumb"]/li[contains(@class,"category")]/a/span/text()').extract()
        #
		# new_cats = []
		# for i, c in enumerate(cat_list):
		# 	new_cats.append(c)
		item['Product Category'] = response.meta['cat']
		item['Brand'] = response.xpath('//div[@itemprop="brand"]/a/text()').extract_first()

		# new_cats = ''
		# for i, c in enumerate(cat_list):
		# 	new_cats += c.encode('utf-8')
		# 	if i < (len(cat_list) - 1):
		# 		new_cats += '/'
		# item['Product Category'] = new_cats
		# for i, val in enumerate(cat_list):
		# 	item['Product Category{}'.format(str(i + 1))] = val

		img_url = response.xpath('//img[@id="image"]/@src').extract_first()
		item['Image URL'] = ''
		if img_url:
			item['Image URL'] = response.urljoin(img_url)

		item['Image URI'] = ''
		if img_url:
			# img_url = img_url.split('?')[0]
			item['Image URI'] = img_url.split('/')[-1]
		item['Product URL'] = response.url

		print('\nTotal Count: {}\n'.format(str(item['Serial'])))

		yield item







