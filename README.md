nyaamagnet
==========

Scrape Nyaa as magnet links.

# REQUIREMENTS
- Python 3.2
- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
- [Requests](http://docs.python-requests.org/en/latest/)

# USAGE
Add the categories you want to scrape in categories.json. The formatting should be fairly obvious from the default configuration.

	Scraper.py nyaa|sukebei [new|missed]

There are two modes, `new` (default) and `missed`. `new` starts downloading new torrents based on the last torrent id found in the DB, while `missed` starts from ID #1, ignoring all IDs that are found in the DB.

# OTHER
- Based on my testing, Sukebei might (hopefully temporarily) IP ban you from accessing the site. Nyaa doesn't exhibit this behavior.
