from bs4 import BeautifulSoup
import time
import re
import urllib.request


def main():

	baseurl = "https://unsplash.com/s/photos/farmer"

	getData(baseurl)


def getData(baseurl):

	html = askURL(baseurl)
	soup = BeautifulSoup(html, "html.parser")

	list = soup.find_all("figure")
	itemsList = []
		
	for i in range(len(list)):

		try:
			if "src" in list[i].img.attrs:
				itemsList.append(list[i].img.attrs["src"])
		except:
			pass

	f = open('test.csv', 'w', encoding='UTF-8')


	for item in itemsList:
		f.write(item+"\n")
		



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