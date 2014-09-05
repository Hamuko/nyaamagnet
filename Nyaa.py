from bencodepy import decode_from_file, encode, DecodingError
from bs4 import BeautifulSoup
import base64
import hashlib
import os
import re
import requests
import tempfile

class Nyaa(object):
	def __init__(self):
		pass

	@property
	def last_entry(self):
		soup = BeautifulSoup(requests.get('http://www.nyaa.se/').text)
		link = soup.find('tr', class_='tlistrow').find('td', class_='tlistname').a['href']
		return int(re.search('tid=([0-9]*)', link).group(1))

class NyaaEntry(object):
	def __init__(self, url):
		self.url = url
		r = requests.get(url)
		setattr(r, 'encoding', 'utf-8')
		soup = BeautifulSoup(r.text)
		if soup.find('div', class_='content').text == '\xa0The torrent you are looking for does not appear to be in the database.':
			self.exists = False
		else:
			self.exists = True
		if self.exists == True:
			self.category = soup.find('td', class_='viewcategory').find_all('a')[0].text
			self.sub_category = soup.find('td', class_='viewcategory').find_all('a')[1].text
			self.name = soup.find('td', class_='viewtorrentname').text
			self.date, self.time = soup.find('td', class_='vtop').text.split(', ')
			self.dl_link = soup.find('div', class_='viewdownloadbutton').a['href']
			_status = soup.find('div', class_=re.compile('content'))['class']
			if 'trusted' in _status:
				self.status = 'trusted'
			elif 'remake' in _status:
				self.status = 'remake'
			elif 'aplus' in _status:
				self.status = 'a+'
			else:
				self.status = 'normal'

	@property
	def magnet(self):
		torrent_f, torrent_path = tempfile.mkstemp()
		r = requests.get(self.dl_link, stream=True)
		f = os.fdopen(torrent_f, 'wb')
		for chunk in r.iter_content(128):
			f.write(chunk)
		f.close()
		try:
			metadata = decode_from_file(tf[1])
		except DecodingError:
			return 0
		os.unlink(torrent_path)
		hashcontents = encode(metadata[b'info'])
		digest = hashlib.sha1(hashcontents).digest()
		b32hash = base64.b32encode(digest)
		return 'magnet:?xt=urn:btih:{}'.format(b32hash.decode())
	