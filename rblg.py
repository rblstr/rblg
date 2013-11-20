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


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	content = db.Column(db.Text)

	def __init__(self, title, content):
		self.title = title
		self.content = content


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


@app.route('/blogs', methods=['POST'])
def blogs():
	username = request.cookies.get('user')
	if not username or username != app.config['USERNAME']:
		return 'Must be logged in to post'
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
	username = request.cookies.get('user')
	if username and username == app.config['USERNAME']:
		session['logged_in'] = True
	posts = Post.query.all()
	return render_template('index.html', session=session, posts=posts, errors={})


if __name__ == '__main__':
	init_db()
	app.run(debug=DEBUG)
