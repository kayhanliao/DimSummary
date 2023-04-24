#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
# test comment 
# from transformers import pipeline, set_seed
import logging
import os
import pickle
from logging import FileHandler, Formatter

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from transformers import BartForConditionalGeneration, BartTokenizer
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from user_definition import *
from yelp_scraper import *

#----------------------------------------------------------------------------#
# application Config.
#----------------------------------------------------------------------------#

application = Flask(__name__)
application.config.from_object('config')

'''
@application.teardown_request
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

# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
PATH = 'kayhanliao/yelpGPTv1.1'
CHECKPOINT = 'facebook/bart-base'
tokenizer = BartTokenizer.from_pretrained(CHECKPOINT)
model = BartForConditionalGeneration.from_pretrained(PATH)


@application.route('/', methods=['POST', 'GET'])
def home():
    form = BasicForm()
    return render_template('pages/placeholder.home.html',
                               form=form)


@application.route('/search', methods=['POST', 'GET'])
def search():
    form = BasicForm()
    query = request.args.get('query')
    cat = request.args.get('category')
    tool = YelpScraper(url, api_key)
    revs = tool.search_single_restaurant(term=query, cond=cat).groupby('review_type').sum()
    input_text = revs.iloc[0,0]
    encoded_text = tokenizer.encode(input_text,return_tensors='pt',max_length=1024)
    outputs = model.generate(input_ids=encoded_text,max_length=150)
    result = tokenizer.decode(outputs[0],skip_special_tokens=True)
    # result = summarizer(revs.iloc[0,0][:4000], max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return render_template('pages/placeholder.home.result.html',
                           form=form,
                           input_query=query,
                           selected_cond=cat,
                           comm=result)

@application.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

# Error handlers.
@application.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@application.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not application.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    application.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    application.logger.addHandler(file_handler)
    application.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    application.run()

