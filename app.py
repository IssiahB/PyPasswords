""" This Module is the main entry point for the
	application. It contains the main loop that
	continually gets client input and performs actions.
	It performs actions by matching client input with
	the proper commands.
"""

from Color_Console import *
from pass_builder import *
from typing import Callable


def get_action(cmd: str) -> Callable[[], None]:
	""" Matches a given command with the
		proper action.

		Args:
			cmd (str): A single character string that
					   is the command for an action to
					   be performed

		Returns:
			Callable: A function that is the proper action
					  for the command given. Returns None
					  if command does not exist
	"""
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
	""" Main loop for getting client commands
		and calling their respective actions.
	"""
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
