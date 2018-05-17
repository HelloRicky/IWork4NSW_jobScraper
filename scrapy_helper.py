"""
resource: https://www.scrapehero.com/how-to-rotate-proxies-and-ip-addresses-using-python-3/
get free proxie
"""
from __future__ import print_function
import requests
from lxml.html import fromstring
from itertools import cycle
import traceback


"""
	return set of available free proxies that
	Https: available to Https, Yes
	type: anonyous and elite

"""

def get_proxies():
	
	url = 'https://free-proxy-list.net/'
	accept_types = ["anonymous", "elite proxy"]			# exclude transparent
	index_https = 7						# column from table
	index_anonymity = 5				# column from table

	response = requests.get(url)
	parser = fromstring(response.text)
	proxies = set()
	for i in parser.xpath('//tbody/tr'):

		if i.xpath('.//td[%s][contains(text(),"yes")]' % (index_https)) and \
				i.xpath('.//td[%s]/text()'%(index_anonymity))[0] in accept_types:

			proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
			proxies.add(proxy)

	return proxies

"""
	return set of the very common user agent of Chrome, Firefox and safari
"""
def get_useragents():
	browser_list = [
		"https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/",
		"https://developers.whatismybrowser.com/useragents/explore/software_name/firefox/",
		"https://developers.whatismybrowser.com/useragents/explore/software_name/safari/"

	]
	useragents = set()
	for browser in browser_list:
		response = requests.get(browser)
		parser = fromstring(response.text)
		for i in parser.xpath('//tbody/tr'):
			if i.xpath('.//td[5][contains(text(), "Very")]'):
				agent = i.xpath('.//td[1]/a/text()')[0]
				useragents.add(agent)

	return useragents

if __name__ == "__main__":
	print(len(get_proxies()))

