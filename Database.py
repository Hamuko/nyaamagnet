import json
import os
import sqlite3

class Database(object):
	"""docstring for Database"""
	def __init__(self, path):
		self.path = path
		if os.path.exists(path + '/db.sqlite'):
			self.file_exists = True
		else:
			self.file_exists = False
		self.c = sqlite3.connect(path + '/db.sqlite')
		if not self.file_exists:
			self.create_database()
		self.verify_database()
		self.check_categories()
		self.check_status()
		self.load_values()

	@property
	def last_entry(self):
		cur = self.c.cursor()
		cur.execute('SELECT * FROM torrents ORDER BY torrent_id DESC LIMIT 1;')
		try:
			return cur.fetchone()[0]
		except:
			return 0

	def create_database(self):
		print('Creating database...')
		self.c.execute('CREATE TABLE categories (category_id INTEGER NOT NULL, category_name TEXT NOT NULL, PRIMARY KEY (category_id))')
		self.c.execute('CREATE TABLE sub_categories (sub_category_id INTEGER NOT NULL, sub_category_name TEXT NOT NULL, PRIMARY KEY (sub_category_id))')
		self.c.execute('CREATE TABLE status (status_id INTEGER NOT NULL, status_name TEXT NOT NULL, PRIMARY KEY (status_id))')
		self.c.execute('CREATE TABLE torrents \
			(torrent_id INTEGER NOT NULL, torrent_name TEXT NOT NULL, \
			torrent_magnet TEXT NOT NULL, category_id INTEGER NOT NULL, \
			sub_category_id INTEGER NOT NULL, status_id INTEGER NOT NULL, \
			PRIMARY KEY (torrent_id), \
			FOREIGN KEY (category_id) REFERENCES categories(category_id), \
			FOREIGN KEY (sub_category_id) REFERENCES sub_categories(sub_category_id), \
			FOREIGN KEY (status_id) REFERENCES status(status_id))')

	def check_categories(self):
		with open(self.path + '/categories.json') as f:
			category_json = json.load(f)
		cur = self.c.cursor()
		cur.execute('SELECT * FROM categories')
		categories = cur.fetchall()
		if len(categories) == 0:
			for i, cat in enumerate(category_json, start=1):
				self.write_category((i, cat))
		elif len(categories) > 0:
			t1, t2 = zip(*categories)
			next_id = len(categories) + 1
			for cat in category_json:
				if cat not in t2:
					self.write_category((next_id, cat))
					next_id += 1
		cur.execute('SELECT * FROM sub_categories')
		sub_categories = cur.fetchall()
		try:
			t1, t2 = zip(*sub_categories)
		except:
			t2 = ()
		next_id = len(sub_categories) + 1
		for cat in category_json:
			for sub_cat in category_json[cat]:
				if sub_cat not in t2:
					self.write_subcategory((next_id, sub_cat))
					cur.execute('SELECT * FROM sub_categories')
					t1, t2 = zip(*cur.fetchall())
					next_id += 1

	def check_status(self):
		cur = self.c.cursor()
		cur.execute('SELECT * FROM status')
		status = ['normal', 'remake', 'trusted', 'a+']
		db_status = cur.fetchall()
		if len(db_status) == 0:
			for i, stat in enumerate(status, start=1):
				self.write_status((i, stat))
		elif len(db_status) > 0:
			t1, t2 = zip(*db_status)
			next_id = len(db_status) + 1
			for stat in status:
				if stat not in t2:
					self.write_status((next_id, stat))

	def load_values(self):
		cur = self.c.cursor()
		self.categories = {}
		self.sub_categories = {}
		self.status = {}
		cur.execute('SELECT * FROM categories')
		for t1, t2 in cur.fetchall():
			self.categories[t2] = t1
		cur.execute('SELECT * FROM sub_categories')
		for t1, t2 in cur.fetchall():
			self.sub_categories[t2] = t1
		cur.execute('SELECT * FROM status')
		for t1, t2 in cur.fetchall():
			self.status[t2] = t1

	def verify_database(self):
		print('Verifying database...')
		cur = self.c.cursor()

		comparison = [(0, 'category_id', 'INTEGER', 1, None, 1), (1, 'category_name', 'TEXT', 1, None, 0)]
		cur.execute('PRAGMA table_info(categories);')
		if cur.fetchall() == comparison:
			print('Table \'categories\' verified.')
		else:
			print('Table \'categories\' broken.')
			exit()

		comparison = [(0, 'sub_category_id', 'INTEGER', 1, None, 1), (1, 'sub_category_name', 'TEXT', 1, None, 0)]
		cur.execute('PRAGMA table_info(sub_categories);')
		if cur.fetchall() == comparison:
			print('Table \'sub_categories\' verified.')
		else:
			print('Table \'sub_categories\' broken.')
			exit()

		comparison = [(0, 'status_id', 'INTEGER', 1, None, 1), (1, 'status_name', 'TEXT', 1, None, 0)]
		cur.execute('PRAGMA table_info(status);')
		if cur.fetchall() == comparison:
			print('Table \'status\' verified.')
		else:
			print('Table \'status\' broken.')
			exit()

		comparison = [(0, 'torrent_id', 'INTEGER', 1, None, 1), (1, 'torrent_name', 'TEXT', 1, None, 0), (2, 'torrent_magnet', 'TEXT', 1, None, 0), (3, 'category_id', 'INTEGER', 1, None, 0), (4, 'sub_category_id', 'INTEGER', 1, None, 0), (5, 'status_id', 'INTEGER', 1, None, 0)]
		cur.execute('PRAGMA table_info(torrents);')
		if cur.fetchall() == comparison:
			print('Table \'torrents\' verified.')
		else:
			print('Table \'torrents\' broken.')
			exit()

	def write_category(self, data):
		print('Writing category \'{}\' into database...'.format(data[1]))
		self.c.execute('INSERT INTO categories VALUES (?, ?)', data)
		self.c.commit()

	def write_subcategory(self, data):
		print('Writing subcategory \'{}\' into database...'.format(data[1]))
		self.c.execute('INSERT INTO sub_categories VALUES (?, ?)', data)
		self.c.commit()

	def write_status(self, data):
		print('Writing status \'{}\' into database...'.format(data[1]))
		self.c.execute('INSERT INTO status VALUES (?, ?)', data)
		self.c.commit()

	def write_torrent(self, data):
		'''id, name, magnet, category, sub_category, status'''
		self.c.execute('INSERT INTO torrents VALUES (?, ?, ?, ?, ?, ?)', data)
		self.c.commit()
