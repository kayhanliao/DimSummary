#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from transformers import pipeline, set_seed
#from google.cloud import storage
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
import os
import pickle

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
class BasicForm(FlaskForm):
    ids = StringField("ID",validators=[DataRequired()])
    submit = SubmitField("Submit")

def summarizer(restaraunt_name):
    # storage_client = storage.Client()

    # bucket = storage_client.bucket('your-gcs-bucket')
    # blob = bucket.blob('dictionary.pickle')
    # pickle_in = blob.download_as_string()
    # loaded_model= pickle.loads(pickle_in)

    loaded_model = pickle.load(open('model.pkl', 'rb'))
    result = loaded_model.predict(restaraunt_name)
    return result[0], result[1], result[2], result[3]

@app.route('/', methods=['POST', 'GET'])
def home():
    form = BasicForm()
    generator = pipeline('text-generation', model='openai-gpt')
    set_seed(42)
    if request.method == 'POST':
        # restaraunt_name = Flask.request.form['restaraunt_name']
        # top, low, newest, elite = summarizer(restaraunt_name) 
        pred = generator("Hello, I'm a language model,",
                         max_length=50, num_return_sequences=1)[0]['generated_text']
        top, low, newest, elite = pred, pred, pred, pred        
        return render_template('pages/placeholder.home.html',
                               form=form, top_comm=top,
                               bottom_comm=low, newest_comm=newest,
                               elite_comm=elite)
    return render_template('pages/placeholder.home.html',
                           form=form)

@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
