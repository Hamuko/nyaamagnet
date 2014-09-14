from bs4 import BeautifulSoup
import re
import requests
import sys

class Nyaa(object):
	def __init__(self, url):
		self.url = url
		self.info_url = url + '?page=view&tid='
		self.dl_url = url + '?page=download&tid='

	@property
	def last_entry(self):
		r = requests.get(self.url)
		if r.status_code not in range(100, 399):
			print('Fetching error, nyaa may have blocked your IP or be down', file=sys.stderr)
			sys.exit(1)

		soup = BeautifulSoup(r.text)
		link = soup.find('tr', class_='tlistrow').find('td', class_='tlistname').a['href']
		return int(re.search('tid=([0-9]*)', link).group(1))

class NyaaEntry(object):
	def __init__(self, nyaa, nyaa_id):
		self.info_url = '{}{}'.format(nyaa.info_url, nyaa_id)
		self.download_url = '{}{}&magnet=1'.format(nyaa.dl_url, nyaa_id)

		r = requests.get(self.info_url)
		setattr(r, 'encoding', 'utf-8')
		self.page = BeautifulSoup(r.text)
		if self.page.find('div', class_='content').text == '\xa0The torrent you are looking for does not appear to be in the database.':
			self.exists = False
		else:
			self.exists = True

	@property
	def category(self):
		return self.page.find('td', class_='viewcategory').find_all('a')[0].text

	@property
	def sub_category(self):
		return self.page.find('td', class_='viewcategory').find_all('a')[1].text

	@property
	def name(self):
		return self.page.find('td', class_='viewtorrentname').text

	@property
	def time(self):
		return self.page.find('td', class_='vtop').text.split(', ')

	@property
	def status(self):
		_status = self.page.find('div', class_=re.compile('content'))['class']
		if 'trusted' in _status:
			return 'trusted'
		elif 'remake' in _status:
			return 'remake'
		elif 'aplus' in _status:
			return 'a+'
		else:
			return 'normal'

	@property
	def hash(self):
		r = requests.head(self.download_url)
		if 'Location' in r.headers:
			return re.search(r'magnet:\?xt=urn:btih:(.*)&tr=', r.headers['Location']).group(1).upper()
		else:
			return None
