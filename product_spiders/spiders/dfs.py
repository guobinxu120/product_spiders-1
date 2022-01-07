# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from collections import OrderedDict


class dfsSpider(scrapy.Spider):

	name = "dfs"

	# use_selenium = False
	domain = 'https://www.dfs.com'
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
		n = 1
		yield scrapy.Request(url='https://www.dfs.com/en/hong-kong/brands', callback=self.parse_category)

	def parse_category(self, response):
		cats = response.xpath('//a[@itemprop="url"]/@href').extract()
		p_cats = response.xpath('//div[@class="lists-item"]')
		for pcat in p_cats:
			cat1 = pcat.xpath('./h4/a/text()').extract_first()
			url_tags = pcat.xpath('.//li/a')
			if url_tags:
				for tag in url_tags:
					url = tag.xpath('./@href').extract_first()
					yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': url, 'next_count': 0})
			else:
				url = pcat.xpath('./h4/a/@href').extract_first()
				if url :
					yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': url, 'next_count': 0})

		# if len(cats) > 0:
		# 	for url in cats:
		# 		yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': url, 'next_count': 0})

			###############---- test ------------------##################
			# url = '/en/hong-kong/brands/giorgio-armani'
			# yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'basic_url': url, 'next_count': 0})
			#############################################################################

	def parseProductList(self, response):
		cats = response.xpath('//a[@itemprop="url"]/@data-href').extract()
		cat_list = response.xpath('//li[@itemprop="itemListElement"]/a/span/text()').extract()
		cats_l = []
		for i,cat in enumerate(cat_list):
			if i ==0 : continue
			cats_l.append(cat)
		category = '\n'.join(cats_l)
		if len(cats) > 0:
			for cat in cats:
				yield scrapy.Request(url=response.urljoin(cat), callback=self.parseProduct, dont_filter=True, meta={'category': category})

			###############---- test ------------------##################
			# test_url = '/en/hong-kong/brands/giorgio-armani/38043931/lip-maestro-405-sultan?q=:blprelevance&page=4&text='
			# yield scrapy.Request(url=response.urljoin(test_url), callback=self.parseProduct)
			#############################################################################

			next_count = response.meta['next_count'] + 1
			next_url = response.meta['basic_url'] + '?q=:blprelevance&page={}&text='.format(str(next_count))
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

		item['Product Category'] = response.meta['category']
		# item['Product Category2'] = ''
		# item['Product Category3'] = ''

		item['Brand'] = response.xpath('//li[@itemprop="itemListElement"]/a/span/text()').extract()[-1]
		# cats = []
		# for i,cat in enumerate(cat_list):
		# 	if i ==0 : continue
		# 	cats.append(cat)
		# item['Product Category'] = '/'.join(cats)
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







