from bs4 import BeautifulSoup
import time
import re
import urllib.request


def main():

	baseurl = "https://www.carrefour.fr/s?filters%5Bproduct.categories.sub_node.id%5D%5B0%5D=28129&%20filters%5Bproduct.categories.sub_node.id%5D%5B1%5D=28130&q=fromage&sq=fromage&noRedirect"

	getData(baseurl)


def getData(baseurl):

	html = askURL(baseurl)
	soup = BeautifulSoup(html, "html.parser")

	list = soup.find_all("ul", class_="product-grid")
	items = list[0].find_all("article")
	itemsList = []

	for item in items:
		origin = ""
		price = ""
		try:
			origin = item.find_all("div", class_="product-card__origin")[0].string.replace(" ", "")
			origin = origin.strip('\t\r\n')
		except Exception as e:
			pass

		try:
			price = item.find_all("div", class_="product-card-per-unit-label")[0].string.replace(" ", "")
			price = price.strip('\t\r\n')
		except Exception as e:
			pass

		url = item.find_all("div", class_="ds-product-card--vertical-image")[0].img.attrs['data-src']

		itemsDict = {}

		itemsDict["product"] = item.a.attrs['title'].strip()
		itemsDict["origin"] = origin
		itemsDict["price"] = price
		itemsDict["url"] = "https://www.carrefour.fr" + url

		itemsList.append(itemsDict)
		

	f = open('test.csv', 'w', encoding='UTF-8')


	for item in itemsList:
		line = ""
		for key in item:
			line = line + item[key] + ","
		f.write(line[:-1]+"\n")
		



def askURL(url):

	head = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:85.0) Gecko/20100101 Firefox/85.0"
	}

	request = urllib.request.Request(url, headers=head)
	html = ""
	try:
		response = urllib.request.urlopen(request)
		time.sleep(2)
		html = response.read().decode("utf-8")
	except urllib.error.URLError as e:
		if hasattr(e, "code"):
			print(e.code)
		if hasattr(e, "reason"):
			print(e.reason)
	
	return html

if __name__ == '__main__':
    main()
