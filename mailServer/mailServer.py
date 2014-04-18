from flask import flask
from flask.ext.pymongo import pymongo

app = Flask('mission-email-journal')
mongo = PyMongo(app)

import smtpd
import asyncore

class MailServer(smtpd.SMTPServer):


	#peer = the client's address, a tuple containig IP and incoming port
	#mailfrom = the "from" information out of the message envelope, given to the server by the client when the mesage is delivered. this does not necessarily match the From header in all cases
	#rcpttos = the list of recipients from the message envelope. Again, this does not always mathc the To header, especially if someone is blind carbon copied
	#data = the full RFC 2822
	def process_message(self, peer, mailfrom, rcpttos, data):
		print 'Receiving message from:', peer
		print 'Message addressed from:', mailfrom
		print 'Message addressed to  :', rcpttos
		print 'Message length        :', len(data)
		print data
		return


	def findUser(self, to, from):
		for user in to:


	def store()
if __name__ == "__main__":
	server = MailServer(("localhost", 1025), None)
	asyncore.loop()
