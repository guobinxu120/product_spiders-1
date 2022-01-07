# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from collections import OrderedDict


class dfsSpider(scrapy.Spider):

	name = "heinemanndutyfree"

	# use_selenium = False
	domain = 'http://www.heinemanndutyfree.com.au'
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
		yield scrapy.Request(url='http://www.heinemanndutyfree.com.au/sydney_en/', callback=self.parse_category)

	def parse_category(self, response):
		lis = response.xpath('//ul[@class="nav__items"]/li')
		lis.pop()
		for i, li in enumerate(lis):
			if i == 0: continue
			cat1_name = li.xpath('./a/text()').extract_first()
			divs = li.xpath('./ul/li/div')
			for div in divs:
				if div.xpath('./a/text()').extract_first() == 'Shop by Brand':
					break
				cats = div.xpath('./ul/li')
				if cats:
					for cat in cats:
						cat2_name = cat.xpath('./a/text()').extract_first()
						if cat.xpath('./a/@class').extract_first() == 'new_arrow':
							continue
						url = cat.xpath('./a/@href').extract_first()
						yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': response.urljoin(url), 'cat': '/'.join([cat1_name, cat2_name]), 'next_count': 1})

		###############---- test ------------------##################
		# url = 'http://www.heinemanndutyfree.com.au/sydney_en/wine-champagne/white-wine'
		# yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': url, 'cat': 'wine-champagne/white-wine', 'next_count': 1})
		#############################################################################

	def parseProductList(self, response):
		cats = response.xpath('//div[@class="product-list"]/div/div/a/@href').extract()
		if cats[len(cats) - 1] == '#':
			cats.pop()
		if len(cats) > 0:
			for cat in cats:
				yield scrapy.Request(url=response.urljoin(cat), callback=self.parseProduct, dont_filter=True, meta={'basic_url': response.meta['basic_url'], 'cat': response.meta['cat']})

			###############---- test ------------------##################
			# test_url = '/en/hong-kong/brands/giorgio-armani/38043931/lip-maestro-405-sultan?q=:blprelevance&page=4&text='
			# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProduct, dont_filter=True, meta={'basic_url': response.meta['basic_url'], 'cat': response.meta['cat'], 'next_count': 0})
			# yield scrapy.Request(url=response.urljoin('http://www.heinemanndutyfree.com.au/sydney_en/chatelle/chatelle-napoleon-brandy-40-1l-1l.html'), callback=self.parseProduct, meta={'basic_url': response.meta['basic_url'], 'cat': response.meta['cat']})
			#############################################################################

			next_count = response.meta['next_count'] + 1
			next_url = response.meta['basic_url'] + '?dir=asc&order=brandname&p={}'.format(str(next_count))
			yield scrapy.Request(url=response.urljoin(next_url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': response.meta['basic_url'], 'cat': response.meta['cat'], 'next_count': next_count})


	def parseProduct(self, response):
		item = OrderedDict()
		self.total_count += 1
		item['Serial'] = self.total_count
		item['Platform URL'] = self.domain
		item['Product Name'] = response.xpath('//h1[@id="title-ellipsis"]/text()').extract_first().encode('utf-8')

		item['Product Price'] = ''
		price_temp = response.xpath('//span[@id="price"]/text()').re(r'[\d.,]+')
		item['Product Price'] = price_temp[0].replace(',', '')
		item['Product Price Currency'] = 'USD'

		item['Product Description'] = ''
		desc = response.xpath('//div[@class="content"]/p/text()').extract_first()
		if desc:
			item['Product Description'] = desc.strip().encode('utf-8')
			# new_desc = []
			# for d in desc:
			# 	d = d.strip()
			# 	if d:
			# 		new_desc.append(d)
			# if new_desc:
			# # desc = desc.strip()
			# 	item['Product Description'] = '\n'.join(new_desc)

		item['Product Category'] = response.meta['cat']

		brands = response.xpath('//ul[@class="breadcrumbs"]/li/a/text()').extract()
		# brands.remove('Home')
		# brands.remove('All Brands')
		item['Brand'] = ''
		if len(brands) > 2:
			item['Brand'] = brands[2]
		# item['Product Category2'] = ''
		# item['Product Category3'] = ''

		# cat_list = response.xpath('//div[@class="detail-spec"]/dl//li/a/text()').extract()
        #
		# new_cats = []
		# for i, c in enumerate(cat_list):
		# 	new_cats.append(c)
		# item['Product Category'] = ''.join(new_cats)

		# new_cats = ''
		# for i, c in enumerate(cat_list):
		# 	new_cats += c.encode('utf-8')
		# 	if i < (len(cat_list) - 1):
		# 		new_cats += '/'
		# item['Product Category'] = new_cats
		# for i, val in enumerate(cat_list):
		# 	item['Product Category{}'.format(str(i + 1))] = val

		img_url = response.xpath('//li[@class="wide slide"]/img/@src').extract_first()
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







