from random import randint


class PasswordBuilder:
	def __init__(self, length, spec, num):
		self.length = length
		self.spec_len = spec
		self.num_len = num
		# Used for generating each value
		self.character_places = {}

	def _generate_letter(self):
		value = randint(65, 90)
		lower_case = bool(randint(0, 1))
		# randomly switches between uppercase and lowercase
		return str(chr(value)).lower() if lower_case else str(chr(value))

	def _generate_special(self):
		value = randint(33, 38)
		if value == 34: # Skip the " character
			value += 1

		return str(chr(value))

	def _generate_number(self):
		value = randint(48, 57)
		return str(chr(value))

	def _fill_dict(self, amount, generate_func):
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

				- generate_func: The function that will 
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

	def _check_valid(self):
		""" Checks if the amount of special and digit characters
			can fit into the length of the password
		"""
		return not (self.spec_len + self.num_len > self.length)

	def __call__(self):
		if not self._check_valid():
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
