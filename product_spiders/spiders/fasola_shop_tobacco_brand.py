# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from collections import OrderedDict


class dfsSpider(scrapy.Spider):

	name = "fasola_shop_tobacco_brand"

	# use_selenium = False
	domain = 'http://www.fasola-shop.com'
	total_count = 0
	categories_data = None
	result_data_list = {}
	custom_settings = {
	    'CONCURRENT_REQUESTS': 8,
	    'DOWNLOAD_DELAY': 0.2,
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
		n = 1
		urls = ['http://www.fasola-shop.com/en/brand', 'http://www.fasola-shop.com/en/alcohol_brand', 'http://www.fasola-shop.com/en/tobacco_brand']
		yield scrapy.Request(url='http://www.fasola-shop.com/en/tobacco_brand', callback=self.parse_category)

	def parse_category(self, response):
		cats = response.xpath('//ul[@class="brands"]/li/a/@href').extract()
		if len(cats) > 0:
			for url in cats:
				yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': url, 'next_count': 0})

			###############---- test ------------------##################
			# url = '/en/hong-kong/brands/giorgio-armani'
			# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProductList, dont_filter=True, meta={'next_count': 0})
			#############################################################################

	def parseProductList(self, response):
		cats = response.xpath('//ul[@id="products"]/li//a[@itemprop="url"]/@href').extract()
		if len(cats) > 0:
			for cat in cats:
				yield scrapy.Request(url=response.urljoin(cat), callback=self.parseProduct, dont_filter=True)

			###############---- test ------------------##################
			# test_url = '/en/hong-kong/brands/giorgio-armani/38043931/lip-maestro-405-sultan?q=:blprelevance&page=4&text='
			# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProduct)
			# yield scrapy.Request(url=response.urljoin('http://www.fasola-shop.com/en/products/DOM-PERIGNON-ROSE-VTG-2003'), callback=self.parseProduct)
			#############################################################################

			next_count = response.meta['next_count'] + 1
			next_url = response.xpath('//nav[@class="pagination"]/span[@class="next"]/a/@href').extract_first()
			if next_url:
				yield scrapy.Request(url=response.urljoin(next_url), callback=self.parseProductList, dont_filter=True, meta={'next_count': next_count})


	def parseProduct(self, response):
		item = OrderedDict()
		self.total_count += 1
		item['Serial'] = self.total_count
		item['Platform URL'] = self.domain
		item['Product Name'] = response.xpath('//h1[@itemprop="name"]/text()').extract_first().encode('utf-8')

		item['Product Price'] = ''
		price_temp = response.xpath('//span[@itemprop="price"]/text()').re(r'[\d.,]+')
		item['Product Price'] = price_temp[0].replace(',', '')
		item['Product Price Currency'] = response.xpath('//span[@itemprop="priceCurrency"]/@content').extract_first()

		item['Product Description'] = ''
		desc = response.xpath('//div[@class="detail-spec"]/p//text()').extract()
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

		cat_list = response.xpath('//div[@class="detail-spec"]/dl//li/a/text()').extract()

		new_cats = []
		for i, c in enumerate(cat_list):
			new_cats.append(c)
		item['Product Category'] = '/'.join(new_cats)

		# new_cats = ''
		# for i, c in enumerate(cat_list):
		# 	new_cats += c.encode('utf-8')
		# 	if i < (len(cat_list) - 1):
		# 		new_cats += '/'
		# item['Product Category'] = new_cats
		# for i, val in enumerate(cat_list):
		# 	item['Product Category{}'.format(str(i + 1))] = val

		img_url = response.xpath('//div[@id="product-images"]/div/img/@src').extract_first()
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







