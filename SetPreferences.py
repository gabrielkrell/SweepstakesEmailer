"""This file should allow you to set preferences for the SweepstakesEmailer."""

import smtplib
from datetime import date
import pickle
import sys
from random import randint
from namedlist import namedlist
from namedlist import namedtuple
from email.mime.text import MIMEText
import time
import math
import SweepstakesEmailer
import getpass
import copy


# currentDate = date.today()
# defaultFilename = "emailerData.p"

# defaultData = SaveData(
# 	server='smtp.gmail.com',
# 	port=465,
# 	username='(redacted)'
# 	password='(redacted)',
# 	fromA='(redacted)',
# 	toA='(redacted)',
# 	message=MIMEText(
# 		("Hi!  I'd like to request my {attempt} free code of the day." "\n" "\n"
# 			"Thanks," "\n"
# 			"Gabriel")),
# 	sentLog={})

# defaultData.message['Subject'] = "(redacted)"
# defaultData.message['From'] = defaultData.fromA
# defaultData.message['To'] = defaultData.toA

class NoValidInputException(Exception):
	pass


def editExistingPreferences():
	# implement me
	pass


def newPreferences():
	"""Create a new preferences file and overwrite the old one."""
	workingPrefs = copy.deepcopy(SweepstakesEmailer._defaultData)
	getNewMailServer(workingPrefs)


def getNewMailServer(data):
	"""Prompt the user for the server's address and store it in data.  The user
	may change it or do nothing."""
	temp_address = copy.copy(data.server)
	if temp_address == SweepstakesEmailer._defaultData.server:
		dialog = (
			"Are you using Gmail? Type 'g' for Gmail, 'c' to cancel, or enter "
			"your server's hostname.")
	else:
		dialog = (
			"Your server is still {0}. Type 'y' to confirm, 'g' to use gmail, "
			"or enter a new hostname.")

	user_input = input(dialog)
	if user_input.lower() in 'y yes c':
		pass
	elif user_input.lower() in 'g gmail':
		# for now, let's not confirm this since user can't make typos here
		temp_address = SweepstakesEmailer._defaultData.server
		data.server = temp_address
		print("Address set to gmail ({0}).".format(temp_address))
	else:
		temp_address = user_input
		if confirm(
			prompt="Is {0} the address of your mail server?".format(temp_address),
			serious=True):
			data.server = temp_address
		else:
			getNewMailServer(data)


def main():
	print("""\
Setting preferences for sweepstakes emailer. This is a program to automatically
send out a limited number of emails every day.  Schedule it to run daily with
cron, etc.

Exit at any time with Ctrl+C.
""")
	key = inputHandler(
		options='e n E N',
		prompt="Would you like to edit (e) preferences or start a new (n) file?",
		error_msg="Please enter 'e' or 'n'. Hit Ctrl+C to quit.",
		retry=True)

	options = {'e': editExistingPreferences, 'n': newPreferences}
	options[key]()


# We need to fill up our data store, a SaveData object, with:
# - server address
# - server port
# - username
# - password
# - a MIMEText object with
#  | - a message
#  | - a subject
#  | - a "from" address
#  | - a "to" address


def inputHandler(
	options, prompt="", error_msg=None, retry=False, caseSensitive=False):
	"""\
	Get the user's input.  You can specify the prompt text, a response to
	show if they do not choose, whether to keep retrying, and whether to look
	for and return case-sensitive entry.  Raises NoValidInputException."""
	while True:
		i = input(prompt)
		if i:
			if not caseSensitive:
				i = i.lower()
			if i in options:
				return i
		if error_msg:
			print(error_msg)
		if not retry:
			raise NoValidInputException(
				"Input invalid: {0}".format(i) if i else "No valid input.")


def confirm(prompt=" Are you sure?", serious=True):
	go = 'y yes'
	nogo = 'n no'
	try:
		i = inputHandler([go, nogo], prompt + (" (y/N)" if serious else "(Y/n)"))
	except NoValidInputException:
		return not serious
	if serious:
		return i in go  # only affirmative continues
	else:
		return i not in nogo  # anything but negative is okay


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Terminated.')
		sys.exit(0)
