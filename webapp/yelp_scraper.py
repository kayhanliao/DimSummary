import json
import os
from datetime import datetime
from time import sleep

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


def retrieve_reviews(url):
    content = requests.get(url,timeout=20)
    soup = BeautifulSoup(content.content, "html.parser")
    relevant = soup.find_all('p', class_='comment__09f24__gu0rG css-qgunke')
    reviews = []
    
    for rev in relevant:
        review = rev.find('span').getText()
        reviews.append(review)

    return reviews


class YelpScraper:
    '''Custom Webscraper for Yelp API'''

    def __init__(self,url,api_key):

        self.url = url
        self.api_key = api_key

        self.params = {}
        self.api_header = {'Authorization': self.api_key,
                           'accept': 'application/json'}
        self.name = None


    def search_single_restaurant(self, term, cond='top_rated', location='San Francisco'):

        self.name = term

        self.params['location'] = location
        self.params['term'] = term
        self.params['limit'] = 1
        self.params['offset'] = 0

        response = requests.get(self.url,headers=self.api_header,params=self.params, timeout=25)

        result = json.loads(response.text)
        scrape_url = result['businesses'][0]['url'].split('?')[0]

        self.name = result['name']

        top_rated_url = os.path.join(scrape_url,'?sort_by=rating_desc')
        low_rated_url = os.path.join(scrape_url,'?sort_by=rating_asc')
        newest_rated_url = os.path.join(scrape_url,'?sort_by=date_desc')
        elite_rated_url = os.path.join(scrape_url,'?sort_by=elites_desc')

        if cond=='top rated':
            top_rated_content = retrieve_reviews(top_rated_url)
            result = pd.DataFrame({'review_type':['top_rated']*len(top_rated_content),
                                            'review':top_rated_content})
        elif cond=='low rated':
            low_rated_content = retrieve_reviews(low_rated_url)
            result = pd.DataFrame({'review_type':['low_rated']*len(low_rated_content),
                                            'review':low_rated_content})
        elif cond=='newest':
            new_rated_content = retrieve_reviews(newest_rated_url)
            result = pd.DataFrame({'review_type':['newest_rated']*len(new_rated_content),
                                            'review':new_rated_content})
        elif cond=='elite':
            elite_rated_content = retrieve_reviews(elite_rated_url)
            result = pd.DataFrame({'review_type':['elite_rated']*len(elite_rated_content),
                                            'review':elite_rated_content})

        return result
    
    def get_name(self):
        return self.name
