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
from yelp_scraper import *
from user_definition import *

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

# def summarizer(restaraunt_name):
#     # storage_client = storage.Client()

#     # bucket = storage_client.bucket('your-gcs-bucket')
#     # blob = bucket.blob('dictionary.pickle')
#     # pickle_in = blob.download_as_string()
#     # loaded_model= pickle.loads(pickle_in)

#     loaded_model = pickle.load(open('model.pkl', 'rb'))
#     result = loaded_model.predict(restaraunt_name)
#     return result[0], result[1], result[2], result[3]

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.route('/', methods=['POST', 'GET'])
def home():
    form = BasicForm()
    return render_template('pages/placeholder.home.html',
                               form=form)

@app.route('/search', methods=['POST', 'GET'])
def search():
    form = BasicForm()
    query = request.args.get('query')
    tool = YelpScraper(url, api_key)
    revs = tool.search_single_restaurant(query).groupby('review_type').sum()
    result = pd.DataFrame(index=revs.index, columns=['review summary'])
    for i in range(revs.shape[0]):
        tmp = revs.iloc[i,0][:4000]
        result.iloc[i,0] = summarizer(tmp, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return render_template('pages/placeholder.home.result.html',
                           form=form,
                           input_query=query,
                           top_comm=result.loc['top_rated', 'review summary'],
                           bottom_comm=result.loc['low_rated', 'review summary'],
                           newest_comm=result.loc['newest_rated', 'review summary'],
                           elite_comm=result.loc['elite_rated', 'review summary'])


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
