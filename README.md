nyaamagnet
==========

Scrape Nyaa as magnet links.

# REQUIREMENTS
- Python 3.4 (haven't tested on any lower versions of Python 3)
- [Requests](http://docs.python-requests.org/en/latest/)
- [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/)

# USAGE
Add the categories you want to scrape in categories.json. The formatting should be fairly obvious from the default configuration.

	Scraper.py nyaa|sukebei [new|missed]

There are two modes, `new` (default) and `missed`. `new` starts downloading new torrents based on the last torrent id found in the DB, while `missed` starts from ID #1, ignoring all IDs that are found in the DB.
