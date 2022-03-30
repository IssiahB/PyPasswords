# PyPasswords
This application is useful for storing passwords as well as password descriptions, making it easier to access and remember
your credentials for any given site you use them on. **PyPasswords** also allows for creating multiple users, giving the ability
for multiple people to have their own set of stored passwords.

## How To Install
**Prerequisites**
- 'Git Bash' must be installed or something alike, visit: [here](https://git-scm.com/downloads)
- 'Python' must be installed, visit: [here](https://www.python.org/downloads/)
- Internet connection

Using your command line tool create a new file. For Windows, Linux, and Mac the command should be: `mkdir mydirname`. Using *Git Bash* navigate to
that directory and clone this repository with the command `git clone https://github.com/IssiahB/pyContacts.git`. Back to your command line tool with
python setup correctly run `env\Scripts\activate`, this will activate the virtual environment that has the necessary packages installed. Finally
you can run this application in the terminal using `py app.py`.

## How To Use
Once the application is running and if it's your first time using the app you'll likely see something like:
```
      Python Password Generator

 Please Create A New User!
 Enter Username: 
```
Simply create a new user with a username and a password. The username must be at least 3 characters long and the password must be at least 5.
Once done it'll ask you to login. Finally you'll be greeted with the commands that are available to a user:
```
 Loggin Successful

-Usage-
    For keeping track of passwords and what
    they are used for.

-Options-
    -g          Generate a new password

    -c          Create a new user

    -r          Remove current user

    -l          List all the previously
                  generated passwords and
                  their usages

    -d          Delete a password

    -h          Prints this help message

    -i          Login as different user

    -q          Quit the program



  > 
```
Next time you startup the application it'll just ask you to login. Now that your in, play around a bit and try out the options.

## Options
* g - Generate a new password
* c - Create a new user
* r - Remove current user
* l - List all the previously generated passwords and their usages
* d - Delete a password
* h - Prints this help message
* i - Login as different user
* q - Quit the program

> Generate a new password

Generating a new password consists of providing the length for the password, providing the amount of special characters to be distributed throughout the
password, and providing the amount of digit character to be distributed throughout the password. Once generated you can give a discription for the use
of the password, finally you can choose whether or not you would like to save the password. The passwords are encrypted and saved in the sqlite database
file.

> Create a new user

Creating a new user consists of the same actions described in the begining of the **How To Use** section. The users' passwords are hashed using *SHA256*
and provided a randomly generated salt.

> Remove current user

To remove the current user you must provide the user's password as well as accept the acknowledgment. If you accept the acknowledgment all the data saved
with it the user, such as the passwords and their descriptions will be removed also.

> List all the previously generated passwords and their usages

This option will automatically retrieve and decrypt the passwords in the database as well as their descriptions and neatly print them out for you to review.

> Delete a password

This option will print out the passwords with their respective IDs and descriptions, then prompt the user to enter the ID of the password to be deleted.
Once deleted the password cannot be retrieved.

> Prints this help message

Prints the help message.

> Login as different user

Prompts the user to enter the username and password of a user, then logs them in as that user.

> Quit the program

Immediatly closes the program.

## Contributing
