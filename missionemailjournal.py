import sys
import RegistrationForm
from flask import Flask, request
from flask import render_template
from pymongo import MongoClient
from flask.ext.mongokit import MongoKit, Document
from wtforms import TextField, PasswordField, validators

app = Flask(__name__)
client = MongoClient('107.170.214.197', 27017)
db = client.MyMissionJournal

@app.route('/register', methods=['GET', 'POST'])
def register():
	msg=''
	if request.method == 'POST':
		msg = request.form['username']
		if not '@' in request.form['username']:
			msg = "Please enter a valid email address." 
		elif not request.form['password'] == request.form['password_confirm']:
			msg = "The passwords you enetered do not match. Please try again."
		elif len(request.form['password']) < 8 or len(request.form['password']) > 20:
			msg = "Please choose a password that is between 8 and 20 characters long."
	return render_template('registration.html', message=msg)

@app.route('/')
@app.route('/index')
def index():
	return render_template('landing.html')

if __name__ == '__main__':
	app.run()


