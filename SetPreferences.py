"""This file should allow you to set preferences for the SweepstakesEmailer."""

import sys
import time
import SweepstakesEmailer
import getpass
import copy
import os


class NoValidInputException(Exception):
	pass


class NoChoiceMade(Exception):
	pass


def editExistingPreferences():
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
	pass

def newPreferences():
	"""Create a new preferences file and overwrite the old one."""
	workingPrefs = copy.deepcopy(SweepstakesEmailer._defaultData)
	editServer(workingPrefs)
	editPort(workingPrefs)
	editUsername(workingPrefs)
	editPassword(workingPrefs)
	editMessageText(workingPrefs)
	editSubject(workingPrefs)
	editFrom(workingPrefs)
	editTo(workingPrefs)
	savePrompt(workingPrefs)


def editMessageText(workingPrefs):
	try:
		newMessageBody = getNewAndConfirm(
			currentV=workingPrefs.message._payload,
			defaultV=SweepstakesEmailer._defaultData.message._payload,
			fieldname="message text")
	except NoChoiceMade:
		print("[{f}] is \"{v}\" (unchanged).".format(
			f="message text", v=SweepstakesEmailer._defaultData.message._payload))
	else:
		workingPrefs.message._payload = newMessageBody
		print("[{f}] set to \"{v}\".".format(f="message text", v=newMessageBody))
	time.sleep(1)
	clear()


def editPassword(data):
	message = "\nEnter a new password? "
	while True:
		if confirm(message):
			newPassA = getpass.getpass()
			newPassB = getpass.getpass("Password (confirm): ")
			if newPassA == newPassB:
				data.password = newPassA
				print("Password set.")
				break
			message = "Passwords didn't match.  Try again? "
		else:
			print("Password not set.")
			break
	time.sleep(1)
	clear()


def editFrom(workingPrefs):
	if (workingPrefs.port == SweepstakesEmailer._defaultData.port and
		workingPrefs.server == SweepstakesEmailer._defaultData.server):
		del(workingPrefs.message['From'])  # otherwise it'll just add another
		workingPrefs.message['From'] = str(workingPrefs.username) + "@gmail.com"
	_editMessageField(workingPrefs, 'From')


def editPort(workingPrefs):
	_editL1Field(workingPrefs, 'port')
	try:
		workingPrefs.port = int(workingPrefs.port)
	except TypeError:  # if it's None for some reason, let it go
		pass


def editServer(workingPrefs):
	_editL1Field(workingPrefs, 'server')


def editUsername(workingPrefs):
	_editL1Field(workingPrefs, 'username')


def editSubject(workingPrefs):
	_editMessageField(workingPrefs, 'Subject')


def editTo(workingPrefs):
	_editMessageField(workingPrefs, 'To')


def _editL1Field(workingPrefs, field):
	"""Internal function - edit top-level preference"""
	try:
		newValue = getNewAndConfirm(
			currentV=getattr(workingPrefs, field),
			defaultV=getattr(SweepstakesEmailer._defaultData, field),
			fieldname=field)
	except NoChoiceMade:
		print("[{f}] is \"{v}\" (unchanged).".format(
			f=field, v=getattr(workingPrefs, field)))
	else:
		setattr(workingPrefs, field, newValue)
		print("[{f}] set to \"{v}\".".format(f=field, v=newValue))
	time.sleep(1)
	clear()


def _editMessageField(workingPrefs, field):
	try:
		newValue = getNewAndConfirm(
			currentV=workingPrefs.message[field],
			defaultV=SweepstakesEmailer._defaultData.message[field],
			fieldname=field,
			retry=True)
	except NoChoiceMade:
		print("[{f}] is \"{v}\" (unchanged).".format(
			f=field, v=workingPrefs.message[field]))
	else:
		del(workingPrefs.message[field])
		workingPrefs.message[field] = newValue
		print("[{f}] set to \"{v}\".".format(f=field, v=newValue))
	time.sleep(1)
	clear()


def getNewAndConfirm(
	fieldname, currentV=None, defaultV=None, retry=True, serious=False):
	"""Prompt the user for a value, optionally showing the current and default
	as options,	and return their chosen value.  The user may do nothing,
	throwing an exception (so you can use try: x = get() except: pass."""
	if defaultV or currentV:
		prompt = "".join((
			"\nWould you like to",
			"\n(d) use the default value for [{f}] ({dv})" if defaultV else "",
			"\n(c) use the existing value for [{f}] ({cv})" if currentV else "",
			" or\n(n) use a new value for [{f}]"))
		print(prompt.format(
			f=fieldname, dv=shorten(defaultV), cv=shorten(currentV)))
		user_input = inputHandler('d c n', retry=True, error_msg="Try again. ")
	else:
		user_input = 'n'  # hacky
	if user_input == 'd' and defaultV:
		return defaultV
	elif user_input == 'c' and currentV:
		return currentV
	elif user_input == 'n':
		user_input = input("Enter a new value for [{f}]".format(f=fieldname))
		if confirm(serious=serious):
			return user_input
		else:
			if retry:
				return getNewAndConfirm(fieldname, currentV, defaultV, retry, serious)
			else:
				raise NoChoiceMade()


def savePrompt(workingPrefs):
	while True:
		if confirm(prompt="Write changes to disk?", serious=True):
			SweepstakesEmailer.saveData(
				SweepstakesEmailer.defaultFilename,
				workingPrefs)
			print('Data saved.')
			break
		else:
			if confirm(prompt='Quit without saving changes?', serious=True):
				break


def shorten(string, maxlength=29):
	"""Would call it 'trim' but that's taken.  Shortens strings for display."""
	string = str(string)  # let's make sure
	if len(string) > maxlength - 3:
		return string[:maxlength - 3] + "..."
	return string


def clear():
	if os.name == ('nt', 'dos'):
		os.system("cls")
	elif os.name == ('linux', 'osx', 'posix'):
		os.system("clear")
	else:
		print("\n" * 120)

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
		i = inputHandler(go + nogo, prompt + (" (y/N)" if serious else " (Y/n)"))
	except NoValidInputException:
		return not serious
	if serious:
		return i in go  # only affirmative continues
	else:
		return i not in nogo  # anything but negative is okay


def main():
	clear()
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


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Terminated.')
		sys.exit(0)
