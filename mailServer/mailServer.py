
import smtpd
import asyncore
import datetime
import email

from pymongo import MongoClient


class MailServer(smtpd.SMTPServer):
	def initDB(self):
		client = MongoClient("localhost", 27017)
		self.db = client.myMissionJournal

	def messageAsHTML(self, msg):
		maintype = msg.get_content_maintype()
		print("maintype = "+maintype)
		if maintype == 'multipart':
			for part in msg.get_payload():
				partType = part.get_content_maintype()
				print partType
				print part
		elif maintype == 'text':
			print msg.get_payload()

	def getSubject(self, msg):
		if msg.has_key("subject"):
			subject = msg['subject']
			print "subject: " + subject
			return subject
		return ''

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

		if "trackme@ldsmissionjournal.com" in rcpttos:

			if self.findUser(rcpttos, mailfrom):
				msg = email.message_from_string(data)
				HTML = self.messageAsHTML(msg = msg)
				subject = self.getSubject(msg = msg)

				#print("---- user was found")
				dbMessage = {"sender": mailfrom, "recipients": rcpttos, "date": datetime.datetime.utcnow(), "message": data} 
				#print("---- saving:")
				#print(messageObject)
				messageID = self.db.messages.insert(dbMessage)

		print self.db.collection_names()
		return


	def findUser(self, sentTo, sentFrom):
		toUsers = []
		fromUser = None
		users = self.db.users

		#self.db.users.insert({"email": "adamsonlance@gmail.com", "firstName": "Lance", "lastName":  "Adamson", "mission": "Mexico, Tuxtla-Gutierrez"})

		for address in sentTo:
			#print("---- searching for: " + address)
			user = users.find_one({"email": address})
			if user:
				#print ("------ foud!!")
				toUsers.append(user)

		fromUser = users.find_one({"email": sentFrom})
		
		if len(toUsers) > 0 or fromUser:
			return True
		else:
			return False

if __name__ == "__main__":
	server = MailServer(("ldsmissionjournal.com", 25), None)
	server.initDB()
	asyncore.loop()
