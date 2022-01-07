# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from collections import OrderedDict


class dubaidutyfreeSpider(scrapy.Spider):

	name = "dubaidutyfree"

	# use_selenium = False
	domain = 'https://online.dubaidutyfree.com'
	total_count = 0
	categories_data = None
	result_data_list = {}
	# custom_settings = {
	#     'CONCURRENT_REQUESTS': 8,
	#     'DOWNLOAD_DELAY': 1,
	#     'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
	#     'CONCURRENT_REQUESTS_PER_IP': 4
	# }

	headers = ['PageUrl', 'ProductLink', 'ImageLink', 'Rarity', 'ProductTitle', 'NewQty', 'NewPrice', 'NewContent', 'NearMintQty', 'NearMintPrice', 'NearMintContent',
			   'FoilNearMintQty', 'FoilNearMintPrice', 'FoilNearMintContent',
			   'PlayedQty', 'PlayedPrice', 'PlayedContent', 'FoilPlayedQty', 'FoilPlayedPrice', 'FoilPlayedContent', 'SetName']


###########################################################

	def __init__(self, *args, **kwargs):
		super(dubaidutyfreeSpider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(url='https://online.dubaidutyfree.com/ddf/', callback=self.parse_category)

	def parse_category(self, response):
		cats = response.xpath('//li[@class="sub-cat-list-head"]/a/@href').extract()
		for cat in cats:
			N = cat.split('-')[-1]
			yield scrapy.Request(url=response.urljoin(cat), callback=self.parseProductList, meta={'next_count': 1, 'N': N})


		####------------- test ----------------###
		# yield scrapy.Request(url=response.urljoin(cats[0]), callback=self.parseProductList, dont_filter=True, meta={'next_count': 1})
		# if subcategory_url == 'https://www.coolstuffinc.com/page/449':#?&resultsperpage=25&page=2':
		# 	yield scrapy.Request( url=subcategory_url, callback=self.parseProductList, meta={'set_name': set_name } )
		#####################################################

	def parseProductList(self, response):
		products_list = response.xpath('//li[@class="span3 gridlist"]/div/a/@href').extract()
		if len(products_list) > 0:
			for product in products_list:
				yield scrapy.Request(url=response.urljoin(product), callback=self.parseProduct)

			####------------- test ----------------###
			# yield scrapy.Request(url=response.urljoin(products_list[0]), callback=self.parseProduct)
			# if subcategory_url == 'https://www.coolstuffinc.com/page/449':#?&resultsperpage=25&page=2':
			# 	yield scrapy.Request( url=subcategory_url, callback=self.parseProductList, meta={'set_name': set_name } )
			#####################################################

			####------------- next page ----------------###
			N = response.meta['N']
			next_count = response.meta['next_count'] + 1
			tabParam = ''
			if 'tabParam' in response.meta.keys():
				tabParam = response.meta['tabParam']
			else:
				tabParam = response.xpath('//input[@class="tabRefPage"]/@value').extract_first()

			main_url = 'https://online.dubaidutyfree.com/ddf/ajaxFacet?N={}&No={}&&Nrpp=20&view=grid&Ns=productAvailableInWeb%7C1%7C%7CglobalRankL2%7C0%7C%7CsalesVolume%7C1%7C%7Cproduct.displayName%7C0&tabParam={}&Ns=productAvailableInWeb%7C1%7C%7CglobalRankL2%7C0%7C%7CsalesVolume%7C1%7C%7Cproduct.displayName%7C0&userAction=loadMore'
			next_url = main_url.format(N, str(next_count * 20), tabParam)
			yield scrapy.Request(url=next_url, callback=self.parseProductList, meta={'next_count': next_count, 'N': N, 'tabParam': tabParam})
			#####################################################

	def parseProduct(self, response):
		item = OrderedDict()
		self.total_count += 1
		item['Serial'] = self.total_count
		item['Platform URL'] = self.domain
		item['Product Name'] = response.xpath('//span[@class="big-head"]/text()').extract_first().strip()

		item['Product Price'] = ''
		price_temp = response.xpath('//div[@class="pdp-price-details"]/ul/li')
		for t in price_temp:
			if 'USD' in t.xpath('./text()').extract_first():
				price = t.xpath('./span/text()').extract_first()
				if price:
					price = price.strip().replace(',', '')
					item['Product Price'] = price
		item['Product Price Currency'] = 'USD'

		item['Product Description'] = ''
		desc = response.xpath('//div[@id="prod-pdp3"]/div[@class="span9"]/text()').extract_first()
		if desc:
			desc = desc.strip()
			item['Product Description'] = desc

		item['Product Category1'] = ''
		item['Product Category2'] = ''
		item['Product Category3'] = ''

		cat_list = response.xpath('//ul[@class="ddf-breadcrumb span12"]/li/a/text()').extract()
		try:
			cat_list.remove('\r\nHOME')
		except:
			pass
		for i, val in enumerate(cat_list):
			item['Product Category{}'.format(str(i + 1))] = val

		img_url = response.xpath('//a[@id="zoom-target"]/@href').extract_first()
		item['Image URL'] = img_url
		item['Image URI'] = ''
		if img_url:
			item['Image URI'] = img_url.split('/')[-1]
		item['Product URL'] = response.url

		print('\nTotal Count: {}\n'.format(str(item['Serial'])))

		yield item







