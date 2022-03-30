""" This module holds the class responsible for building
	the semi-randomly generated passwords
"""


from random import randint
from typing import Callable


class PasswordBuilder:
	""" This class generates semi-random passwords
		that can be stored under a user. Each object
		of this class must have a length, special
		character amount, and digit character amount.

		The values given are used to generate a password
		that has the same length as the one given, that
		has the amount of special characters dispersed
		randomly throughout, and has the amount of digit
		characters dispersed randomly throughout.

		Every special character is chosen randomly, and every
		digit character is chosen randomly. The spots for each
		character are also picked randomly. This allows for a
		very secure password.
	"""

	def __init__(self, length, spec, num):
		""" Creates a PasswordBuilder object with the length,
			special character amount, and digit character amount
			initialized.
		"""
		self.length = length
		self.spec_len = spec
		self.num_len = num
		# Used to make sure character places are not taken
		self.character_places = {}

	def _generate_letter(self) -> str:
		""" Generates a random character in the english
			alphabet, and randomly has it be uppercase
			or lowercase.

			Returns:
				str: The generated character
		"""
		alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
		target = randint(0, 51)
		return alphabet[target]

	def _generate_special(self) -> str:
		""" Generates a random special character a few
			examples are '$, @, &, ...'.

			Returns:
				str: The generated character
		"""
		specials = '&%$#@!*^{}[]<>?.,'
		target = randint(0, 16)

		return specials[target]

	def _generate_number(self):
		""" Generates a random digit character between
			0 and 9.

			Returns:
				str: The generated character
		"""
		value = randint(48, 57)
		return str(chr(value))

	def _fill_dict(self, amount, generate_func: Callable[[], str]):
		""" Picks an empty spot in the password string
			and replaces it with a generated character
			from one of the _generate_***() methods.

			The empty spots that are taken by a new
			character are tracked using a dictionary.
			The dictionary stores the index of the new
			character as it's key, and the generated 
			character as it's value.

			param:
				- amount: The number of empty positions
							to be replaced by a generated
							character

				- generate_func: The method that will 
							generate the new character
		"""
		for num in range(amount):
			spot_found = False

			while not spot_found:
				# chooses a random spot to replace
				index = randint(0, self.length-1)
				if not index in self.character_places:
					self.character_places[index] = generate_func()
					spot_found = True

	def _is_valid(self) -> bool:
		""" Checks if the amount of special and digit characters
			can fit into the length of the password

			Returns:
				bool: True if the above statment is true, False
					  otherwise
		"""
		return (self.spec_len + self.num_len <= self.length)

	def __call__(self):
		""" Builds the random password
		"""
		if not self._is_valid():
			return False

		password = []
		self._fill_dict(self.spec_len, self._generate_special)
		self._fill_dict(self.num_len, self._generate_number)

		for index in range(self.length):
			value = self.character_places.get(index, None)
			if value is None:
				value = self._generate_letter()

			password.append(value)

		return  ''.join(password)
