#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
# test comment 
# from transformers import pipeline, set_seed
import logging
import os
import pickle
from logging import FileHandler, Formatter

from flask import Flask, render_template, request, send_file
from flask_wtf import FlaskForm
# from transformers import (BartForConditionalGeneration, AutoTokenizer,
#                           T5ForConditionalGeneration)
# from transformers import BartForConditionalGeneration, BartTokenizer
from transformers import T5ForConditionalGeneration, T5Tokenizer
from user_definition import *
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from yelp_scraper import *
from dashboard import *

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
PATH = 'kayhanliao/yelpGPTv1.2'
# PATH = 'facebook/bart-base'
CHECKPOINT = 't5-base'
tokenizer = T5Tokenizer.from_pretrained(CHECKPOINT)
model = T5ForConditionalGeneration.from_pretrained(PATH)

cities = pd.read_csv('data/uscities.csv')
cities = cities[cities['state_id']=='CA']['city'].to_list()

@application.route('/', methods=['POST', 'GET'])
def home():
    form = BasicForm()
    return render_template('pages/placeholder.home.html',
                            form=form,
                            items=cities)


@application.route('/search', methods=['POST', 'GET'])
def search():
    form = BasicForm()
    query = request.args.get('query')

    if len(query) == 0:
        return render_template('pages/placeholder.home.error.html',
                        form=form)
    
    cat = request.args.get('category')
    location = request.args.get('location')
    print()

    try:
        tool = YelpScraper(url, api_key)
        revs = tool.search_single_restaurant(term=query, cond=cat,location=location).groupby('review_type').sum()    
        input_text = revs.iloc[0,0]
    
    except:

        return render_template('pages/placeholder.home.error.html',
                            form=form)
    

    encoded_text = tokenizer.encode(input_text,return_tensors='pt',max_length=2048)
    outputs = model.generate(input_ids=encoded_text, max_length=80)
    result = tokenizer.decode(outputs[0],skip_special_tokens=True)
    
    if result.endswith("."):
        pass

    elif result.endswith('?') or result.endswith('!'):
        pass

    elif result.endswith(','):
        result = result[:-1] + '..'

    else:
        result += '..'

    restaurant_name = tool.get_name() 

    return render_template('pages/placeholder.home.result.html',
                           form=form,
                           input_query=restaurant_name,
                           selected_cond=cat,
                           comm=result,
                           items=cities)

@application.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

@application.route('/dashboard')
def dashboard():
    form = BasicForm()
    query = request.args.get('query')
    dashboard_path = 'data/reviews_san_francisco_nlp_labels.csv'
    dashboard = DashBoard(dashboard_path,restaurant_name=query)
    dashboard.visualize()
    return render_template('pages/placeholder.dashboard.html', plot='visualization.png')

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