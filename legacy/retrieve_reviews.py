import json
import os
from datetime import datetime
from time import sleep

import numpy as np
import pandas
import pymongo
import requests

url = ""

url = os.path.join(url_base, url_business)
api_header = {'Authorization': apikey, 'accept': 'application/json'}


def get_restaurant_ids():
    """Retrives Yelp Restaurant IDS"""


url = os.path.join(url_base, url_business)
api_header = {'Authorization': apikey, 'accept': 'application/json'}

for offset in range(0, 50, 50):
    params = {
        'location': 'San Francisco',
        'term': 'restaurants',
        'limit': 50,
        'offset': offset
    }

    r = requests.get(url, headers=api_header, params=params)
    
    result = json.loads(r.text)
    busi_list = result['businesses']
    busi_df = pd.DataFrame(columns=['id', 'name', 'rating', 'url', 'review_cnt'])
    for i in range(len(busi_list)):
        busi_df.loc[i, 'id'] = busi_list[i]['id']
        busi_df.loc[i, 'name'] = busi_list[i]['name']
        busi_df.loc[i, 'rating'] = busi_list[i]['rating']
        busi_df.loc[i, 'url'] = busi_list[i]['url'].split('?')[0]
        busi_df.loc[i, 'review_cnt'] = busi_list[i]['review_count']
    
    result = pd.DataFrame(columns=['id', 'name', 'rating', 'review', 'total_review'])
    idx = 0
    error_count = 0 
    for res in range(len(busi_df)):
        new_page = "?start={}"
        base_url = busi_df.loc[res, 'url']
        cnt = busi_df.loc[res, 'review_cnt']

        # soup = BeautifulSoup(content, "html.parser")
        sleep(2)
        for i in range(0, min(cnt, 100), 10):
            new_page_url = base_url + new_page.format(i)
            try: 
                new_content = requests.get(new_page_url).content
            except Exception as e:
                with open('logs.txt','w') as f:
                    timestamp = str(datetime.now())
                    error_string = f'{timestamp} : Error while using request. Error output {e} \n'
                    f.write(error_string)
                    error_count += 1

            try:

                new_soup = BeautifulSoup(new_content, "html.parser")

                relevant= new_soup.find_all('p', class_='comment__09f24__gu0rG css-qgunke')
                for div in relevant:
                    for html_class in div.find_all('span',class_="raw__09f24__T4Ezm"):
                        text = html_class.find('span')
                        review = html_class.getText()
                        result.loc[idx, 'id'] = busi_df.loc[res, 'id']
                        result.loc[idx, 'name'] = busi_df.loc[res, 'name']
                        result.loc[idx, 'rating'] = busi_df.loc[res, 'rating']
                        result.loc[idx, 'total_review'] = busi_df.loc[res, 'review_cnt']
                        result.loc[idx, 'review'] = review

                        idx += 1
            except Exception as e:
                with open('logs.txt','w') as f:
                    timestamp = str(datetime.now())
                    error_string = f'{timestamp} : Error while parsing with BeautifulSoup. Error output {e} \n'
                    f.write(error_string)
                    error_count += 1

            if error_count > 10:
                break
            
    outfile = str(offset)+'_review_result.csv'
    result.to_csv(outfile)
