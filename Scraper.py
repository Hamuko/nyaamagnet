from Database import Database
from Nyaa import Nyaa, NyaaEntry
import getopt
import os
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
nt = Nyaa()
db = Database(script_dir)

arguments = sys.argv[1:]
optlist, args = getopt.getopt(arguments, '', ['start='])
if len(optlist) > 0:
	for opt, arg in optlist:
		if opt == '--start':
			start_entry = int(arg)

if 'start_entry' not in globals():
	start_entry = db.last_entry + 1

for i in range(start_entry + 1, nt.last_entry + 1):
	entry = NyaaEntry('http://www.nyaa.se/?page=view&tid={}'.format(i))
	if entry.exists == True:
		if entry.category in db.categories and entry.sub_category in db.sub_categories:
			if entry.magnet == 0:
				continue
			print('Entry: {}, Name: {}'.format(i, entry.name))
			db.write_torrent((i, entry.name, entry.magnet, db.categories[entry.category],
				db.sub_categories[entry.sub_category], db.status[entry.status], entry.date, entry.time))

db.c.close()