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


global SaveData
SaveData = namedlist(
	'SaveData',
	'server port username password message sentLog')

global DayLogEntry
DayLogEntry = namedlist('DayLogEntry', 'attempts successes', default=0)

global _defaultData
_defaultData = SaveData(
	server='smtp.gmail.com',
	port=465,
	username=None,
	password=None,
	message=MIMEText(
		("Hi!  I'd like to request my {attempt} free code of the day.")),
	sentLog={})
_defaultData.message['Subject'] = "Free Sweepstakes Entry"
_defaultData.message['From'] = None
_defaultData.message['To'] = None


global defaultFilename
defaultFilename = "emailerData.p"


def namedListToTuple(nl):
	"""Given a named list function, returns a named tuple function."""
	return namedtuple(nl.__name__, nl.__slots__)


def saveData(filename, data, params='wb'):
	file = open(filename, params)
	pickle.dump(data, file)
	file.close()


def openFile(filename):
	try:
		file = open(filename, 'r+b')
		return file
	except FileNotFoundError as e:
		print("couldn't find config file!  Making a new one.")
		# here we should ask the user for their stuff
		saveData(filename, defaultData, 'x+b')
		return openFile(filename)


def loadData(filename):
	f = openFile(filename)
	try:
		return pickle.load(f)
	except TypeError as e:
		print("TypeError encountered when loading config file.")
		raise
	finally:
		f.close()


def sendEmail():
	for _ in range(3):  # try three times in case of errors
		s = smtplib.SMTP_SSL(data.server, data.port)
		s.ehlo()
		s.login(data.username, data.password)
		if s.sendmail(data.fromA, data.toA, data.message.as_string().format(
			attempt=ordinal(data.sentLog[currentDate].attempts + 1))):
			data.sentLog[currentDate].attempts += 1
			print("email sending failed")
			saveData(defaultFilename, data)
		else:
			data.sentLog[currentDate].attempts += 1
			data.sentLog[currentDate].successes += 1
			print("email {0} of {1} attempts sent".format(
				data.sentLog[currentDate].attempts,
				data.sentLog[currentDate].successes))
			saveData(defaultFilename, data)
			break


def ordinal(n):
	""" Returns an ordinal abbreviation like 1st, 2nd, etc. Thanks codegolf """
	return "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])


def main():
	# actually being run from command line
	# right now most of the above functions only work when run from the command
	# line.  Fix that pls so this can be used interactively (over SSH, likely)

	currentDate = date.today()
	data = loadData(defaultFilename)

	try:
		lastDate = max(data.sentLog.keys())
	except ValueError:
		# nothing in sentLog; make a dummy val to initialize it
		lastDate = date.min
	if currentDate > lastDate:
		data.sentLog[currentDate] = DayLogEntry()
	if currentDate > lastDate or data.sentLog[lastDate].successes < 5:
		cLogEntry = data.sentLog[currentDate]
		time.sleep(61 * randint(5, 20))  # ~ between 5 and 20 minutes, but uneven
		while True:
			if cLogEntry.attempts - cLogEntry.successes > 5:
				sys.exit("Too many attempts: {0}".format(data.sentLog[currentDate].attempts))
			if cLogEntry.successes == 5:
				sys.exit()
			delay = randint(20, 40)
			print("Waiting {0}s to send the next email".format(delay))
			time.sleep(delay)
			sendEmail()
	else:
		print("Already sent emails today; nothing to do.")


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Terminated.')
		sys.exit(0)
