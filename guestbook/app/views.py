from app import app
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
import dataset
import os

# Connnect to database
#db = dataset.connect('sqlite:///file.db')
db = dataset.connect('postgresql://{username}:{password}@{host}:{port}/{dbname}'.format(
                      host=os.environ.get('DB_PORT_5432_TCP_ADDR'),
                      port=os.environ.get('DB_PORT_5432_TCP_PORT'),
                      username=os.environ.get('DB_ENV_POSTGRESQL_USER'),
                      password=os.environ.get('DB_ENV_POSTGRESQL_PASSWORD'),
                      dbname=os.environ.get('DB_ENV_POSTGRESQL_DATABASE')))

# create your guests table
table = db['guests']

# when someone sends a GET to / render sign_form.html
@app.route('/', methods=['GET'])
def sign_form():
    return render_template('sign_form.html')

# when someone sends a GET to /guest_book render guest_book.html
@app.route('/guest_book', methods=['GET'])
def guest_book():
    signatures = table.find()
    return render_template('guest_book.html', signatures=signatures)

# when someone sends  POST to /submit, take the name and message from the body
# of the POST, store it in the database, and redirect them to the guest_book
@app.route('/submit', methods=['POST'])
def submit():
    signature = dict(name=request.form['name'], message=request.form['message'])
    table.insert(signature)
    return redirect(url_for('guest_book'))

