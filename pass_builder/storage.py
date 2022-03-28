import sqlite3
import hashlib
from cryptography.fernet import Fernet
from os import path, urandom


def _genewrite_key():
	key = Fernet.generate_key()

	if not path.exists('pass.key'):
		with open('pass.key', 'wb') as key_file:
			key_file.write(key)


def _get_key():
	key = open('pass.key', 'rb').read()
	return key


class DataStorage:
	def __init__(self, user, passw):
		self.username = user
		self.password = passw
		self.is_loggedin = False
		self.has_users = False
		self.__check_users()

	def _build_tables(self):
		with self.conn:
			self.cur.execute("""\
				CREATE TABLE IF NOT EXISTS user_passwords (
					id INTEGER PRIMARY KEY,
					pass TEXT NOT NULL,
					desc TEXT NOT NULL,
					user TEXT NOT NULL
				);""")

			self.cur.execute("""\
				CREATE TABLE IF NOT EXISTS users (
					id INTEGER PRIMARY KEY,
					userName TEXT NOT NULL UNIQUE,
					hash TEXT NOT NULL
				);""")

	def _create_hash(self, passw, salt=urandom(32)):
		key = hashlib.pbkdf2_hmac(
				'sha256',
				passw.encode('utf-8'),
				salt,
				100000
			)

		h = salt + key
		return h

	def _start(self):
		self.conn = sqlite3.connect('userdata.db')
		self.cur = self.conn.cursor()
		self._build_tables()

	def _stop(self):
		self.conn.close()
		self.is_loggedin = False

	def __check_users(self):
		self._start()
		with self.conn:
			self.cur.execute('SELECT COUNT(*) FROM users;')
			if self.cur.fetchone()[0] > 0:
				self.has_users = True
		self._stop()

	def create_user(self, user, passw):
		h = self._create_hash(passw)
		with self.conn:
			self.cur.execute("""\
				INSERT INTO users (userName, hash) VALUES(
					:user, :hash
				);""", {'user': user, 'hash': h})

	def remove_user(self, user):
		with self.conn:
			self.cur.execute('DELETE FROM users WHERE userName == ?;', (user,))
			self.cur.execute('DELETE FROM user_passwords WHERE user == ?;', (user,))

	def login(self):
		with self.conn:
			self.cur.execute("""\
					SELECT hash FROM users WHERE userName == :user;
				""", {'user': self.username})

			hash_value = self.cur.fetchone()
			if hash_value is None:
				return False

			h = self._create_hash(self.password, hash_value[0][:32])
			if h == hash_value[0]:
				return True
			else:
				return False

	def get_stored_values(self, ids_only=False):
		if not self.is_loggedin:
			return

		with self.conn:
			if not ids_only:
				self.cur.execute("""\
						SELECT pass, desc FROM user_passwords WHERE user == :user;
					""", {'user': self.username})
				values = self.cur.fetchall()
				data = []

				for pair in values:
					key = _get_key()
					a = Fernet(key)
					dec_data = a.decrypt(pair[0])
					data.append([dec_data.decode('utf_8'), pair[1]])

				return data
			else:
				self.cur.execute("""\
						SELECT * FROM user_passwords WHERE user == :user;
					""", {'user': self.username})
				return [ids[0] for ids in self.cur.fetchall()]

	def delete_password(self, ID):
		if not self.is_loggedin:
			return

		with self.conn:
			self.cur.execute("""\
						DELETE FROM user_passwords WHERE id == :id;
					""", {'id': ID})

	def store_password(self, password, desc):
		if not self.is_loggedin:
			return

		data = password.encode('utf-8')
		key = _get_key()
		a = Fernet(key)
		enc_data = a.encrypt(data)

		with self.conn:
			self.cur.execute("""\
					INSERT INTO user_passwords (pass, desc, user) VALUES (
						:pass, :desc, :user
					);""", {'pass': enc_data, 'desc': desc, 'user': self.username})

	def __enter__(self):
		_genewrite_key()
		self._start()
		self.is_loggedin = self.login()

	def __exit__(self, g, f, t):
		self._stop()
