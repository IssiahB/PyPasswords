from Color_Console import *
from pass_builder import *


def get_action(cmd):
	switch = {
		'g': generate_password_action,
		'l': list_password_action,
		'd': delete_password_action,
		'c': create_user_action,
		'r': remove_user_action,
		'h': print_help_action,
		'i': login_action,
		'q': quit_action
	}

	action = switch.get(cmd, None)
	return action


def main():
	ctext('\n\n\tPython Password Generator\n', 'green')
	login_action()
	print_help_action()

	while True:
		cmd = get_input()
		action = get_action(cmd)

		if action is None:
			ctext(' Invalid Option\n', 'red')
			continue

		action()

if __name__ == '__main__':
	main()
