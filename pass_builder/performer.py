import inspect
from Color_Console import *
from .builder import PasswordBuilder as Builder
from .storage import DataStorage
from getpass import getpass


def _get_proper_value(msg='', min_value=0, max_value=100):
	value_given = -1
	def in_range():
		return (min_value <= value_given <= max_value)

	while not in_range():
		try:
			value_given = int(get_input(msg))
		except:
			value_given = -1

		if (not in_range()):
			error_msg = f'Sorry the value must be between {min_value} and {max_value}'
			print_error(error_msg)
	return value_given


def get_input(option=''):
	cmd = input(f' {option} > ')
	return cmd


def print_error(msg):
	ctext(f' {msg}\n', 'red')


def login_action():
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


def print_help_action():
	ctext(inspect.cleandoc("""\
			-Usage-
			    For keeping track of passwords and what
			    they are used for.

			-Options-
			    -g		Generate a new password

			    -c		Create a new user

			    -r		Removes current user

			    -l		List all the previously
					  generated passwords and
					  their usages

			    -d		Delete a password

			    -h		Prints this help message

			    -i		Login as different user

			    -q		Quits the program
		"""), 'green')
	print('\n\n')


def generate_password_action(is_recure=False):
	global storage
	length = _get_proper_value('Enter Password Length', 5, 100)
	special_amount = _get_proper_value('Enter The Amount Of Special Characters', 2, int(length*.4))
	num_amount = _get_proper_value('Enter The Amount Of Digit Characters', 1, int(length*.4))

	build = Builder(length, special_amount, num_amount)
	password = build()

	if password is False:
		print_error('Password was an incorrect length')
		password = generate_password_action(True)

	# Return correctly made password up call stack
	if is_recure:
		return password

	ctext(f'\n\t {password}', 'magenta')
	desc = get_input('\tDescribe Password Usage')
	print('')

	should_save = get_input('Save Password (y/n)')
	if should_save == 'y':
		with storage:
			storage.store_password(password, desc)
	else:
		return

	ctext(' Saved Successfully\n', 'cyan')


def create_user_action(anonymous_user=False):
	global storage
	user = input(' Enter Username: ')
	password = getpass(' Enter Password: ')
	valid = (getpass(' Retype Password: ') == password)
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


def remove_user_action():
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


def list_password_action(with_ids=False):
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

def delete_password_action():
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

def quit_action():
	exit(0)
