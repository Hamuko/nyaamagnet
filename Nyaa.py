from bencodepy import decode_from_file, encode, DecodingError
from bs4 import BeautifulSoup
import base64
import hashlib
import os
import re
import requests
import tempfile

class Nyaa(object):
	def __init__(self, url):
		self.url = url
		self.info_url = url + '?page=view&tid='
		self.dl_url = url + '?page=download&tid='

	@property
	def last_entry(self):
		soup = BeautifulSoup(requests.get(self.url).text)
		link = soup.find('tr', class_='tlistrow').find('td', class_='tlistname').a['href']
		return int(re.search('tid=([0-9]*)', link).group(1))

class NyaaEntry(object):
	def __init__(self, url):
		self.url = url
		self.id = re.search(r'nyaa.se/\?page=view&tid=([0-9]*)', url).group(1)
		r = requests.get(url)
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

	def magnet_link(self, url):
		r = requests.head(url)
		return re.search(r'magnet:\?xt=urn:btih:(.*)&tr=', r.headers['Location']).group(1).upper()

	def hash(self, url):
		torrent_f, torrent_path = tempfile.mkstemp()
		r = requests.get(url, stream=True)
		f = os.fdopen(torrent_f, 'wb')
		for chunk in r.iter_content(128):
			f.write(chunk)
		f.close()
		try:
			metadata = decode_from_file(torrent_path)
		except DecodingError:
			return 0
		os.unlink(torrent_path)
		hashcontents = encode(metadata[b'info'])
		digest = hashlib.sha1(hashcontents).digest()
		b32hash = base64.b32encode(digest)
		return b32hash.decode()
	