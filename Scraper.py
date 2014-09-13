from Database import Database
from Nyaa import Nyaa, NyaaEntry
import getopt
import os
import sys

def load_settings():
	class Configuration(object):
		def __init__(self):
			self.db_dir = os.path.dirname(os.path.realpath(__file__))
			self.db_name = None
			self.mode = None
			self.nyaa_url = None
			self.start_entry = None

	config = Configuration()

	arguments = sys.argv[1:]
	optlist, args = getopt.getopt(arguments, '', ['start='])
	if len(optlist) > 0:
		for opt, arg in optlist:
			if opt == '--start':
				self.start_entry = arg

	if len(args) == 0:
		print('Please supply arguments.')
		exit(code=1)
	elif len(args) == 1:
		if args[0] == 'nyaa':
			config.nyaa_url = 'http://www.nyaa.se/'
			config.db_name = 'nyaa'
		elif args[0] == 'sukebei':
			config.nyaa_url = 'http://sukebei.nyaa.se/'
			config.db_name = 'sukebei'
		else:
			print('Invalid url.')
			exit(code=1)
		config.mode = 'new'
	else:
		if args[0] == 'nyaa':
			config.nyaa_url = 'http://www.nyaa.se/'
			config.db_name = 'nyaa'
		elif args[0] == 'sukebei':
			config.nyaa_url = 'http://sukebei.nyaa.se/'
			config.db_name = 'sukebei'
		else:
			print('Invalid url.')
			exit(code=1)
	
		if args[1] == 'new':
			config.mode = 'new'
		elif args[1] == 'missed':
			config.mode = 'missed'
		else:
			print('Invalid option.')
			exit(code=1)

	return config

config = load_settings()
nt = Nyaa(config.nyaa_url)
db = Database(config.db_dir, config.db_name)

if config.mode == 'new' and config.start_entry == None:
	config.start_entry = db.last_entry + 1
elif config.mode == 'missed' and config.start_entry == None:
	config.start_entry = 1

for i in range(config.start_entry, nt.last_entry + 1):
	if config.mode == 'missed':
		if db.entry_exists(i):
			continue

	entry = NyaaEntry(nt.info_url + str(i))
	if entry.exists == True:
		if entry.category in db.categories and entry.sub_category in db.sub_categories:
			if entry.hash == 0:
				continue
			print('Entry: {}, Name: {}'.format(i, entry.name))
			try:
				torrent_hash = entry.magnet_link(nt.dl_url + str(i))
			except:
				torrent_hash = entry.hash(nt.dl_url + str(i))
			db.write_torrent((i, entry.name, torrent_hash, db.categories[entry.category],
				db.sub_categories[entry.sub_category], db.status[entry.status]))

db.c.close()