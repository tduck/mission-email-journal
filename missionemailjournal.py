import sys, hashlib, uuid
from flask import Flask, request, render_template
from pymongo import MongoClient
from flask.ext.mongokit import MongoKit, Document

app = Flask(__name__)
client = MongoClient('107.170.214.197', 27017)
db = client.myMissionJournal

@app.route('/register', methods=['GET', 'POST'])
def register():
	msg=''
	if request.method == 'POST':
		if not '@' in request.form['username']:
			msg = "Please enter a valid email address." 
		elif not request.form['password'] == request.form['password_confirm']:
			msg = "The passwords you entered do not match. Please try again."
		elif len(request.form['password']) < 8 or len(request.form['password']) > 20:
			msg = "Please choose a password that is between 8 and 20 characters long."
		elif len(request.form['given_name']) == 0 or len(request.form['last_name']) == 0:
			msg = "Please fill out all required fields."
		else:
			findUser = db.users.find_one({"email": request.form['username']})
                        if findUser:
				msg = "An account for the user " + request.form['username'] + " already exists."
		        else:
				salt = uuid.uuid4().hex
				hash_pass = hashlib.sha256(request.form['password'] + salt).hexdigest()
				user = {"email": request.form['username'], "firstName": request.form['given_name'], "LastName": request.form['last_name'], "mission": request.form['mission_name'], "title": request.form['missionary_title'], "salt": salt, "password": hash_pass}				
				db.users.save(user)
				msg = "Account for " + request.form['username'] + " registered successfully."
	return render_template('registration.html', message=msg, 
							given_name = request.form['given_name'],
							last_name = request.form['last_name'], 
							mission_name = request.form['mission_name'], 
							username = request.form['username'])

@app.route('/')
@app.route('/index')
def index():
	return render_template('landing.html')

if __name__ == '__main__':
	app.run()


