""" The performer module implements all the available actions
	the can be performed.
"""


import inspect
from Color_Console import *
from .builder import PasswordBuilder as Builder
from .storage import DataStorage
from getpass import getpass


def _get_proper_value(msg: str, min_value: int, max_value: int) -> int:
	""" Used for getting proper values in regards
		to the amount of different characters used in
		generating a password.

		For example when asking for the amount of digit
		characters that should be present in a generated
		password, you can us this function to prompt the client
		with a message asking for the value, specify a
		minimum value that the client can give, and
		specify a maximum value that the client can give.

		If the client enters a value that does not satisfy both
		the mimimum and maximum requirements, the client will be
		asked to reenter the value till both are satisfied.

		Args:
			msg (str): The message to prompt the client with
			min_value (int): The mimimum value reqirement
			max_value (int): The maximum value reqirement

		Returns:
			int: The number entered by the client that satifies
				 all reqirments
	"""
	value_given = -1
	def in_range():
		return (min_value <= value_given <= max_value)

	while not in_range():
		try:
			value_given = int(get_input(msg))
		except:
			# if the user enters a non integer value
			value_given = -1 # continually causes value to be out of range

		if (not in_range()):
			error_msg = f'Sorry the value must be between {min_value} and {max_value}'
			print_error(error_msg)
	return value_given


def get_input(option: str='') -> str:
	""" Gets user input with the option to
		prompt the client with a message.

		Args:
			option (str): A message to prompt the client with.
						  Not necessary

		Returns:
			str: The client's input
	"""
	cmd = input(f' {option} > ')
	return cmd


def print_error(msg: str) -> None:
	""" Formats and prints a message to imply it being
		an error. Mainly gives it a left margin, a color
		of red, and provides a blank line after it is printed.

		Args:
			msg (str): The error message to print
	"""
	ctext(f' {msg}\n', 'red')


def login_action() -> None:
	""" The login action handles logging a client into
		the program so that they can access, use, and
		manipulate the passwords they have stored under
		their user.

		Can also handle the event when there are no
		users in the database.
	"""
	global storage
	if DataStorage('', '').has_users:
		user = input(' Enter Username: ')
		password = getpass(' Enter Password: ')
		storage = DataStorage(user, password)
		with storage:
			if not storage.is_loggedin:
				print_error('Loggin Failed')
				quit_action()
			else:
				ctext(' Loggin Successful \n', 'green')
	else:
		# Build New User Without being logged in
		ctext(' Please Create A New User! ', 'cyan')
		user_created = create_user_action(anonymous_user=True)
		if not user_created:
			quit_action()

		ctext(' Now Please Login ', 'cyan')
		login_action()


def print_help_action() -> None:
	""" This action is for printing the help data
		to the console. The help data consists of
		the overall usage of the program, as well
		as the command options and their descriptions.
	"""
	ctext(inspect.cleandoc("""\
			-Usage-
			    For keeping track of passwords and what
			    they are used for.

			-Options-
			    -g		Generate a new password

			    -c		Create a new user

			    -r		Remove current user

			    -l		List all the previously
					  generated passwords and
					  their usages

			    -d		Delete a password

			    -h		Prints this help message

			    -i		Login as different user

			    -q		Quit the program
		"""), 'green')
	print('\n\n')


def generate_password_action(is_recure=False):
	""" Generate a new password by allowing the client
		to specify the password length, the number of
		special characters, and the number of digit 
		characters.

		All the values entered are used to generate a
		random password. The length of the password can
		be between 5 and 100. The number of special
		characters allowed is between 2 and 40% of the
		length. Finally the number of digit characters
		allowed is between 1 and 40% of the length.

		Once generated this action allows the client to 
		provide a description of how the password will
		be used. As well as wether or not the password
		should be saved under the logged in user.
	"""
	global storage
	length = _get_proper_value('Enter Password Length', 5, 100)
	special_amount = _get_proper_value('Enter The Amount Of Special Characters', 2, int(length*.4))
	num_amount = _get_proper_value('Enter The Amount Of Digit Characters', 1, int(length*.4))

	build = Builder(length, special_amount, num_amount)
	password = build()

	if password is False: # Not needed because use of only 40% of length
		ctext(' Error Generating Passord ', 'red')
		return

	ctext(f'\n\t {password}', 'magenta')
	desc = get_input('\tDescribe Password Usage')
	print('') # Extra Space

	should_save = get_input('Save Password (y/n)')
	if should_save == 'y':
		with storage:
			storage.store_password(password, desc)
			ctext(' Saved Successfully\n', 'cyan')


def create_user_action(anonymous_user: bool=False) -> bool:
	""" Used for creating users that can store passwords.
		Each user can store an unlimited amount of passwords
		and each password has it's own description.

		To create a user the client must provide a username that is
		unique and at least 3 characters long. As well as
		provide a password that is at least 5 characters long.

		Normally to create a new user the client must be logged
		in. This provides extra security for who is allowed to
		create a user. However if there hasn't been a user created or
		if all users have been removed, this action provides
		the ability to create a user using an anonymous user.

		Params:
			anonymous_user (bool): Whether or not to create an
								   user using an anonymous user

		Returns:
			bool: Whether or not the user was created successfully
	"""
	global storage
	user = input(' Enter Username: ')
	if len(user) < 3:
		print_error('Username too short must be 3 characters')
		return create_user_action(anonymous_user)

	password = getpass(' Enter Password: ')
	valid = ((getpass(' Retype Password: ') == password) and (len(password) >= 5))
	if valid is True:
		if not anonymous_user:
			with storage:
				storage.create_user(user, password)
		else:
			anonymous_storage = DataStorage('', '')
			with anonymous_storage:
				anonymous_storage.create_user(user, password)
			del anonymous_storage

		ctext(' Successfully Created \n', 'green')
		return True
	else:
		print_error('Unsuccessful - password retyped incorrectly')
		return False


def remove_user_action() -> None:
	""" Removes the user that is currently logged in.
		The user's passwords and password descriptions
		will also be removed. The client will be asked
		to enter their password as well as an
		acknowledgement to verify that they are sure they
		want to remove the password.

		This action validates the password given with the
		password of the logged in user. As well as handles
		calling the login_action() after the user has been
		removed successfully.
	"""
	global storage
	password = getpass(' Enter Password: ')
	acknowledgement = get_input('Are You Sure (y/n)')
	if not acknowledgement == 'y':
		print('')
		return

	correct_password = (password == storage.password)

	if correct_password:
		with storage:
			storage.remove_user(storage.username)
			ctext(' User Removed Successfully\n', 'green')
			login_action()
	else:
		print_error('Incorrect Password')


def list_password_action(with_ids: bool=False) -> bool:
	""" Lists all the available passwords and descriptions
		stored under the currently logged in user. If
		there are no passwords stored, function will
		print out 'No Values' to the client.

		Can also be used to print out the passwords
		along side their respective IDs.

		Params:
			with_ids (bool): Whether or not to print
							 passwords with their respective
							 IDs

		Returns:
			bool: True if passwords where printed False
				  otherwise
	"""
	global storage
	with storage:
		values = storage.get_stored_values()
		if len(values) < 1:
			print_error('No Values')
			return False

		if with_ids:
			IDs = storage.get_stored_values(with_ids)

		for index, pair in enumerate(values):
			if with_ids:
				print(f'\tID: {IDs[index]}')
			ctext(f'\tPassword: {pair[0]}', 'magenta')
			ctext(f'\tDesc: {pair[1]}\n', 'green')
	return True


def delete_password_action() -> None:
	""" Allows the client to delete a password from
		their stored list of passwords by entering
		the ID for that item.

		Also allows client to cancel the action by
		typing '/' instead of an ID. If the user
		has no current passwords stored, will return
		immediatly.
	"""
	global storage
	has_passwords = list_password_action(True)
	if not has_passwords:
		return

	try:
		idText = get_input("'/' to cancel\n Enter Password ID")
		ID = int(idText)
		with storage:
			available_IDs = storage.get_stored_values(ids_only=True)
			if ID in available_IDs:
				storage.delete_password(ID)
				ctext(' Successfully Deleted\n', 'green')
			else:
				print_error('Incorrect ID')
	except:
		if idText == '/':
			ctext(' Canceled\n', 'cyan')
			return
		print_error('ID must be an integer')
		return


def quit_action() -> None:
	""" Quits the program by calling 'exit(0)'
	"""
	exit(0)
