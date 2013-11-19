from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy

DATABASE = 'rblg.db'
DEBUG = True
SECRET_KEY = 'skeleton_key'
USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rblg.db'
app.config['USERNAME'] = USERNAME
app.config['PASSWORD'] = PASSWORD
db = SQLAlchemy(app)

def init_db():
	db.create_all()

@app.route('/login', methods=['POST'])
def login():
	username = request.form['username']
	errors = {
		'username_error':'',
		'password_error':''
	}
	if not username or app.config['USERNAME'] != username:
		errors['username_error'] = 'Invalid username'
		return render_template('index.html', session={}, errors=errors)
	password = request.form['password']
	if not password or app.config['PASSWORD'] != password:
		errors['password_error'] = 'Invalid password'
		return render_template('index.html', session={}, errors=errors)
	response = app.make_response('Login successful')
	response.set_cookie('user', value=username)
	return response


@app.route('/logout', methods=['GET'])
def logout():
	response = app.make_response('Logout successful')
	response.set_cookie('user', expires=0)
	return response


@app.route('/', methods=['GET'])
def index():
	session = {}
	username = request.cookies.get('user')
	if username and username == app.config['USERNAME']:
		session['logged_in'] = True
	return render_template('index.html', session=session, errors={})


if __name__ == '__main__':
	init_db()
	app.run(debug=DEBUG)
