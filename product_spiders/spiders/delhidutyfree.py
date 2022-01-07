# -*- coding: utf-8 -*-
import scrapy, time
from scrapy import Request
from collections import OrderedDict


class dfsSpider(scrapy.Spider):

	name = "delhidutyfree"

	# use_selenium = False
	domain = 'http://www.delhidutyfree.co.in'
	total_count = 0
	categories_data = None
	result_data_list = {}
	# custom_settings = {
	#     'CONCURRENT_REQUESTS': 2,
	#     'DOWNLOAD_DELAY': 0.2,
	#     'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
	#     'CONCURRENT_REQUESTS_PER_IP': 2
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
		yield scrapy.Request(url='http://www.delhidutyfree.co.in/', callback=self.parse_category)

	def parse_category(self, response):
		first_cats = response.xpath('//nav[@class="navigation"]/ul/li')

		for f_cat in first_cats:
			time.sleep(0.3)
			cat1_name = ''.join(f_cat.xpath('./a/span/text()').extract())
			second_cats = f_cat.xpath('./ul/li')
			if second_cats:
				for s_cat in second_cats:
					cat2_name = ''.join(s_cat.xpath('./a/span/text()').extract())
					third_cats = s_cat.xpath('./ul/li')
					if third_cats:
						for t_cat in third_cats:
							cat3_name = ''.join(t_cat.xpath('./a/span/text()').extract())
							url = t_cat.xpath('./a/@href').extract_first()
							yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'cat': '/'.join([cat1_name, cat2_name, cat3_name]), 'next_count': 1})
					else:
						url = s_cat.xpath('./a/@href').extract_first()
						yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'cat': '/'.join([cat1_name, cat2_name]), 'next_count': 1})
			else:
				url = f_cat.xpath('./a/@href').extract_first()
				yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'cat': cat1_name, 'next_count': 1})




		##############---- test ------------------##################
		# url = 'http://www.delhidutyfree.co.in/confectionery/chocolates/premium.html'
		# yield scrapy.Request(url=response.urljoin(url), callback=self.parseProductList, dont_filter=True, meta={'cat': 'confectionery/chocolates/premium', 'next_count': 1})
		############################################################################

	def parseProductList(self, response):
		cats = response.xpath('//ol[@class="products list items product-items"]/li/div/a/@href').extract()
		if len(cats) > 0:
			for cat in cats:
				time.sleep(0.5)
				yield scrapy.Request(url=response.urljoin(cat), callback=self.parseProduct, dont_filter=True, meta={'cat': response.meta['cat'], 'next_count': response.meta['next_count']})

			###############---- test ------------------##################
			# test_url = '/en/hong-kong/brands/giorgio-armani/38043931/lip-maestro-405-sultan?q=:blprelevance&page=4&text='
			# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProduct, meta={'cat': response.meta['cat'], 'next_count': response.meta['next_count']})
			#############################################################################


			next_url = response.xpath('//a[@class="action  next"]/@href').extract_first()
			if next_url:
				next_count = response.meta['next_count'] + 1
				yield scrapy.Request(url=response.urljoin(next_url), callback=self.parseProductList, dont_filter=True, meta={'cat': response.meta['cat'], 'next_count': next_count})


	def parseProduct(self, response):
		item = OrderedDict()
		self.total_count += 1
		item['Serial'] = self.total_count
		item['Platform URL'] = self.domain
		item['Product Name'] = response.xpath('//div[@class="page-title-wrapper product"]//span[@itemprop="name"]/text()').extract_first()

		item['Product Price'] = ''
		price_temp = response.xpath('//span[contains(@id,"product-price")]/@data-price-amount').extract_first()
		item['Product Price'] = price_temp.split(' ')[-1].replace(',', '')
		item['Product Price Currency'] = 'INR'

		item['Product Description'] = ''
		desc = response.xpath('//div[@class="product attribute description"]//text()').extract()
		if desc:
			new_desc = []
			for d in desc:
				d = d.strip()
				if d:
					new_desc.append(d)
			if new_desc:
				item['Product Description'] = '\n'.join(new_desc)

		item['Product Category'] = '/'.join(response.meta['cat'])
		# item['Product Category2'] = ''
		# item['Product Category3'] = ''

		# cat_list = response.xpath('//li[@itemprop="itemListElement"]/a/span/text()').extract()
		# item['Product Category'] = cat_list[-1]
		# for i, val in enumerate(cat_list):
		# 	item['Product Category{}'.format(str(i + 1))] = val

		img_url = response.xpath('//meta[@property="og:image"]/@content').extract_first()
		item['Image URL'] = ''
		if img_url:
			item['Image URL'] = response.urljoin(img_url)

		item['Image URI'] = ''
		if img_url:
			item['Image URI'] = img_url.split('/')[-1]
		item['Product URL'] = response.url

		print('\nTotal Count: {}\n'.format(str(item['Serial'])))

		yield item







