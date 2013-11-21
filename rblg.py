import hmac
from flask import Flask, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy


DATABASE = 'rblg.db'
DEBUG = True
SECRET_KEY = 'skeleton_key'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rblg.db'
db = SQLAlchemy(app)


def create_cookie(value):
	return "%s|%s" % (value, hmac.new(SECRET_KEY, value).hexdigest())

def validate_cookie(cookie):
	split = cookie.split('|')
	if len(split) < 2:
		return False
	value = split[0]
	value_hashed = split[1]
	return value_hashed == hmac.new(SECRET_KEY, value).hexdigest()

def parse_cookie(cookie):
	return cookie.split('|')[0]

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20))
	password = db.Column(db.Text)

	def __init__(self, username, password):
		self.username = username
		self.password = password


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)

	def __init__(self, title, content):
		self.title = title
		self.content = content


def init_db():
	db.drop_all()
	db.create_all()


@app.route('/register', methods=['POST'])
def register():
	username = request.form.get('username')
	password = request.form.get('password')
	if not username:
		return 'Invalid username'
	if not password:
		return 'Invalid password'
	user = User(username, password)
	db.session.add(user)
	db.session.commit()
	response = app.make_response('Registration successful')
	user_cookie = create_cookie(username)
	response.set_cookie('user', value=user_cookie)
	return response


@app.route('/login', methods=['POST'])
def login():
	username = request.form['username']
	password = request.form['password']
	errors = {
		'username_error':'',
		'password_error':''
	}
	user = User.query.filter_by(username=username).first()
	if not username or not user:
		errors['username_error'] = 'Invalid username'
		return render_template('index.html', session={}, errors=errors)
	if not password or password != user.password:
		errors['password_error'] = 'Invalid password'
		return render_template('index.html', session={}, errors=errors)
	response = app.make_response('Login successful')
	user_cookie = create_cookie(username)
	response.set_cookie('user', value=user_cookie)
	return response


@app.route('/logout', methods=['GET'])
def logout():
	response = app.make_response('Logout successful')
	response.set_cookie('user', expires=0)
	return response


@app.route('/blogs', methods=['POST'])
def blogs():
	user_cookie = request.cookies.get('user')
	if not user_cookie or not validate_cookie(user_cookie):
		return 'Must be logged in to post'
	username = parse_cookie(user_cookie)
	errors = {}
	post_title = request.form.get('title')
	if not post_title:
		errors['title_error'] = 'No title'
	post_content = request.form.get('content')
	if not post_content:
		errors['content_error'] = 'No content'
	if errors:
		return "title_error: %s content_error: %s" % (errors.get('title_error', ''), errors.get('content_error', ''))
	post = Post(post_title, post_content)
	db.session.add(post)
	db.session.commit()
	return 'Post created'


@app.route('/', methods=['GET'])
def index():
	session = {}
	posts = Post.query.all()
	user_cookie = request.cookies.get('user')
	if not user_cookie or not validate_cookie(user_cookie):
		return render_template('index.html', session=session, posts=posts, errors={})
	username = parse_cookie(user_cookie)
	user = User.query.filter_by(username=username).first()
	if user:
		session['logged_in'] = True
	return render_template('index.html', session=session, posts=posts, errors={})


if __name__ == '__main__':
	init_db()
	app.run(debug=DEBUG)

