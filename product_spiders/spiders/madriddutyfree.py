# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from collections import OrderedDict


class dfsSpider(scrapy.Spider):

	name = "madriddutyfree"

	# use_selenium = False
	domain = 'https://www.madriddutyfree.com'
	total_count = 0
	categories_data = None
	result_data_list = {}
	custom_settings = {
	    'CONCURRENT_REQUESTS': 2,
	    'DOWNLOAD_DELAY': 0.2,
	    'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
	    'CONCURRENT_REQUESTS_PER_IP': 2
	}

	headers = ['PageUrl', 'ProductLink', 'ImageLink', 'Rarity', 'ProductTitle', 'NewQty', 'NewPrice', 'NewContent', 'NearMintQty', 'NearMintPrice', 'NearMintContent',
			   'FoilNearMintQty', 'FoilNearMintPrice', 'FoilNearMintContent',
			   'PlayedQty', 'PlayedPrice', 'PlayedContent', 'FoilPlayedQty', 'FoilPlayedPrice', 'FoilPlayedContent', 'SetName']


###########################################################

	def __init__(self, *args, **kwargs):
		super(dfsSpider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		n = 1
		yield scrapy.Request(url='https://www.madriddutyfree.com/en/', callback=self.parse_categoryShowAll)

	def parse_categoryShowAll(self, response):
		cats = response.xpath('//div[@class="see-all"]/a[text()="Show All"]/@href').extract()
		if len(cats) > 0:
			for url in cats:
				yield scrapy.Request(url=response.urljoin(url), callback=self.parse_category1, dont_filter=True)


		###############---- test ------------------##################
		# url = '/en/hong-kong/brands/giorgio-armani'
		# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parse_category1, dont_filter=True)
		#############################################################################

	def parse_category1(self, response):
		cats = response.xpath('//li[@class="amshopby-cat amshopby-cat-level-1 "]/a/@href').extract()
		if len(cats) > 0:
			for url in cats:
				yield scrapy.Request(url=response.urljoin(url), callback=self.parse_category2, dont_filter=True)


		###############---- test ------------------##################
		# url = '/en/hong-kong/brands/giorgio-armani'
		# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parse_category2, dont_filter=True)
		#############################################################################

	def parse_category2(self, response):
		cats = response.xpath('//li[@class="amshopby-cat amshopby-cat-level-1 "]/a/@href').extract()
		if len(cats) > 0:
			for url in cats:
				yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'next_count': 1})

		###############---- test ------------------##################
		# url = '/en/hong-kong/brands/giorgio-armani'
		# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProductList, dont_filter=True)

	def parseProductList(self, response):
		cats = response.xpath('//li[@class="col-xs-6 col-md-3 product "]//div[@class="amlabel-div"]/a/@href').extract()
		if len(cats) > 0:
			for cat in cats:
				yield scrapy.Request(url=response.urljoin(cat), callback=self.parseProduct, dont_filter=True)

			###############---- test ------------------##################
			# test_url = '/en/hong-kong/brands/giorgio-armani/38043931/lip-maestro-405-sultan?q=:blprelevance&page=4&text='
			# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProduct)
			#############################################################################

			next_url = response.xpath('//a[@class="next i-next" and @title="Next"]/@href').extract_first()
			if next_url:
				next_count = response.meta['next_count'] + 1
				yield scrapy.Request(url=response.urljoin(next_url), callback=self.parseProductList, dont_filter=True, meta={'next_count': next_count})


	def parseProduct(self, response):
		item = OrderedDict()
		self.total_count += 1
		item['Serial'] = self.total_count
		item['Platform URL'] = self.domain
		item['Product Name'] = response.xpath('//div[@class="product-main-info"]/h1[@itemprop="name"]/text()').extract_first().encode('utf-8')

		item['Product Price'] = ''
		price_temp = response.xpath('//div[@class="product-main-info"]//span[@itemprop="price"]/@content').extract_first()
		item['Product Price'] = price_temp.replace(',', '')
		item['Product Price Currency'] = 'EUR'

		item['Product Description'] = ''
		desc = response.xpath('//div[@id="description"]/div[@itemprop="description"]/text()').extract()
		if desc:
			new_desc = []
			for d in desc:
				d = d.strip()
				if d:
					new_desc.append(d.encode('utf-8'))
			if new_desc:
				item['Product Description'] = '\n'.join(new_desc)

		item['Product Category'] = ''
		# item['Product Category2'] = ''
		# item['Product Category3'] = ''

		cat_list = response.xpath('//ol[@class="breadcrumb"]/li[contains(@class,"category")]/a/span/text()').extract()
		cat = ''
		for i, c in enumerate(cat_list):
			cat += c.encode('utf-8')
			if i < len(cat_list) - 1:
				cat += '/'
		item['Product Category'] = cat
		# for i, val in enumerate(cat_list):
		# 	item['Product Category{}'.format(str(i + 1))] = val

		img_url = response.xpath('//img[@id="image"]/@src').extract_first()
		item['Image URL'] = ''
		if img_url:
			item['Image URL'] = response.urljoin(img_url)

		item['Image URI'] = ''
		if img_url:
			item['Image URI'] = img_url.split('/')[-1]
		item['Product URL'] = response.url

		print('\nTotal Count: {}\n'.format(str(item['Serial'])))

		yield item







