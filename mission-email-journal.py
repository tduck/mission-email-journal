from flask import Flask
app = Flask(__name__)

from flask import render_template

@app.route('/post/<username>')
def show_user_profile(username):
	return 'User %s' % username

@app.route('/')
@app.route('/index')
def index():
	return render_template('layout.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0')
