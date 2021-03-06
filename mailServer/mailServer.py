
import smtpd
import asyncore
import datetime
import email

from pymongo import MongoClient


class MailServer(smtpd.SMTPServer):

	def getDB(self):
		return MongoClient("localhost", 27017).myMissionJournal

	def saveMessage(self, sender, recipients, date, fullMessage, bodyHTML, bodyText, subject):
		db = self.getDB()
		dbMessage = {"sender": sender, "recipients": recipients, "date": datetime.datetime.utcnow(), "fullMessage": fullMessage, "bodyHTML":bodyHTML, "bodyText":bodyText, "subject": subject} 
		msgID = db.messages.insert(dbMessage)

	def messageAsHTML(self, msg):
		messageHTML = ''
		messageText = ''
		maintype = msg.get_content_maintype()
		# print("maintype = "+maintype)
		if maintype == 'multipart':
			for part in msg.get_payload():
				partType = part.get_content_type()
				if partType == "text/html":
					messageHTML = part.get_payload()
					# print "========== HTML =========="
					# print messageHTML
				elif partType == "text/plain":
					messageText = part.get_payload()
					# print "========== TEXT =========="
					# print messageText
		elif maintype == 'text':
			messageText = mag.get_payload()
			#should do something to parse it into HTML but I don't have time

		return messageText, messageHTML

	def getRecipients(self, msg):
		recips=[]
		if msg.has_key("to"):
			strRecipients = msg['to']
			splitRcpts = strRecipients.split(',')
			for recipient in splitRcpts:
				if '<' in recipient:
					email = recipient[recipient.index("<")+1:recipient.index(">")]
					recips.append(email)
				elif '@' in recipient:
					recipient.replace(" ", "")
					recips.append(recipient)

		print recips
		return recips

	def getSubject(self, msg):
		if msg.has_key("subject"):
			subject = msg['subject']
			# print "subject: " + subject
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
		# print data

		if "trackme@ldsmissionjournal.com" in rcpttos:

			if self.findUser(rcpttos, mailfrom):
				msg = email.message_from_string(data)
				text, HTML = self.messageAsHTML(msg = msg)
				subject = self.getSubject(msg = msg)
				recipients = self.getRecipients(msg = msg)
				if len(recipients) == 0:
					recipients = rcpttos

				#print("---- user was found")
				# dbMessage = {"sender": mailfrom, "recipients": rcpttos, "date": datetime.datetime.utcnow(), "fullMessage": data, "bodyHTML":HTML, "bodyText":text, "subject": subject} 
				self.saveMessage(sender = mailfrom, recipients = recipients, date = datetime.datetime.utcnow(), fullMessage = data, bodyHTML = HTML, bodyText = text, subject = subject)
				#print("---- saving:")
				#print(messageObject)
		return


	def findUser(self, sentTo, sentFrom):
		toUsers = []
		fromUser = None
		users = self.getDB().users

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
	asyncore.loop()
