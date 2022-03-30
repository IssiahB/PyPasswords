""" This module contains the class for creating and
	manipulating this applications database, as well
	the functions, and methods for hashing and encrypting passwords.
"""


import sqlite3
import hashlib
from cryptography.fernet import Fernet
from os import path, urandom


def _genewrite_key():
	""" FOR INTERNAL USE ONLY, generates a private key
		and stores it.
	"""
	key = Fernet.generate_key()

	if not path.exists('pass.key'):
		with open('pass.key', 'wb') as key_file:
			key_file.write(key)


def _get_key():
	""" FOR INTERNAL USE ONLY, retrieves the private key
	"""
	key = open('pass.key', 'rb').read()
	return key


class DataStorage:
	""" This class handles creating the database, creating
		the database tables, communicating with the database,
		and encrypting and hashing passwords. 
	"""

	def __init__(self, user: str, passw: str):
		""" Creates a DataStorage object with the username and
			password initialized. Also checks if there are any
			users available in the database.

			Params:
				user (str): The username of the user to login as
				passw (str): The password of the username to login as
		"""
		self.username = user
		self.password = passw
		self.is_loggedin = False
		self.has_users = False
		self.__check_users()

	def _build_tables(self) -> None:
		""" Creates the database tables if they
			are not already created.
		"""
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

	def _create_hash(self, passw: str, salt: bytes=urandom(32)) -> bytes:
		""" Creates a hash with a password given and the salt.

			Params:
				passw (str): The password to hash
				salt (bytes): The salt can be given or if not given
							  will make one randomly.

			Returns:
				bytes: The hash of the salt and password
		"""
		key = hashlib.pbkdf2_hmac(
				'sha256',
				passw.encode('utf-8'),
				salt,
				100000
			)

		h = salt + key
		return h

	def _start(self):
		""" Used to connect to database and build tables
		"""
		self.conn = sqlite3.connect('userdata.db')
		self.cur = self.conn.cursor()
		self._build_tables()

	def _stop(self):
		""" Used to diconnect from database and logout
		"""
		self.conn.close()
		self.is_loggedin = False

	def __check_users(self) -> bool:
		""" Checks whether or not there are any users
			currently in the database.

			Returns:
				bool: True if the database has users and
					  False otherwise
		"""
		self._start()
		with self.conn:
			self.cur.execute('SELECT COUNT(*) FROM users;')
			if self.cur.fetchone()[0] > 0:
				self.has_users = True
		self._stop()

	def create_user(self, user: str, passw: str) -> None:
		""" Creates a user with a username and password.
			hashes the password and inserts them into the
			databse.

			Params:
				user (str): The username of the new user
							must be unique
				passw (str): The password of the new user
		"""
		h = self._create_hash(passw)
		with self.conn:
			self.cur.execute("""\
				INSERT INTO users (userName, hash) VALUES(
					:user, :hash
				);""", {'user': user, 'hash': h})

	def remove_user(self, user: str) -> None:
		""" Removes the user from the database as
			well as all the passwords and descriptions
			associated with that user.

			Params:
				user (str): The user to be removed
		"""
		with self.conn:
			self.cur.execute('DELETE FROM users WHERE userName == ?;', (user,))
			self.cur.execute('DELETE FROM user_passwords WHERE user == ?;', (user,))

	def login(self) -> bool:
		""" Checks if the username and password provided
			to the class are in the database.
				
			Returns:
				bool: True if password and username given
					  matches a password and username in the
					  database
		"""
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

	def get_stored_values(self, ids_only: bool=False) -> list:
		""" Gets the values stored under the logged in user.
			Can also retrieve just the id's of the values.
			Returns immediatly if not logged in.

			Params:
				ids_only (bool): Wether or not to get just the
								 id's of the values, or the values
								 themselves

			Returns:
				list: Either a list of ids for the values, or a list
					  of tuples containing the password and description
					  as it's values.
		"""
		if not self.is_loggedin:
			return

		with self.conn:
			if not ids_only:
				self.cur.execute("""\
						SELECT pass, desc FROM user_passwords WHERE user == :user;
					""", {'user': self.username})
				values = self.cur.fetchall()
				data = []

				# decrypt passwords
				for pair in values:
					key = _get_key()
					a = Fernet(key)
					dec_data = a.decrypt(pair[0])
					data.append([dec_data.decode('utf_8'), pair[1]])

				return data
			else:
				self.cur.execute("""\
						SELECT id FROM user_passwords WHERE user == :user;
					""", {'user': self.username})
				return [ids[0] for ids in self.cur.fetchall()]

	def delete_password(self, ID: int) -> None:
		""" Deletes a password with it's description stored
			in the database. Uses the passwords id to find it.

			Params:
				ID (int): The id of the password to delete
		"""
		if not self.is_loggedin:
			return

		with self.conn:
			self.cur.execute("""\
						DELETE FROM user_passwords WHERE id == :id;
					""", {'id': ID})

	def store_password(self, password: str, desc: str) -> None:
		""" Inserts a password with it's description into
			the database, before storage encrypts password.

			Params:
				password (str): The password to be encrypted
								and stored in the database
				desc (str): The description of the password
							to be stored with the password
		"""
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
