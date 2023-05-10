import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import re
import string 

nltk.download('stopwords')
nltk.download('punkt')

food_stop_words = ['food','restaurant','order','table']
stop_words = set(stopwords.words('english'))

class DashBoard:

    def __init__(self,path,restaurant_name=None,review_type=None):

        self.df = pd.read_csv(path)
        
        self.restaurant_name = 'All Restaurants'
        self.review_type = 'All Reviews'

        if restaurant_name is not None:
            self.df = self.df[self.df['name'] == restaurant_name]
            self.restaurant_name = restaurant_name
        
        if review_type is not None:
            self.df = self.df[self.df['review_type'] == review_type]
            self.review_type = review_type


    def create_subplot(self,figsize_width=16,figsize_height=8):

        fig, ax = plt.subplots(nrows=2,ncols=2,figsize=(figsize_width,
                                                        figsize_height))
        self.fig = fig
        self.ax = ax

        if self.restaurant_name is not None:
            restaurant_name_title_str = self.restaurant_name
        else:
            restaurant_name_title_str = 'All Restaurants'

        if self.review_type is not None:
            split_rev = self.review_type.split('_')
            split_rev = [i.capitalize() for i in split_rev]
            review_type_title_str = ' '.join(split_rev)
        else:
            review_type_title_str = 'All'
        title = f'NLP Insights of {restaurant_name_title_str} with {review_type_title_str} Reviews'
        self.fig.suptitle(title,fontsize=20)

    def create_word_cloud(self):
        
        wc_df = self.df
        text = wc_df.groupby('name')['review'].apply(lambda x : '\n'.join(x))[0]
        text = text.lower()

        ctrl_chars = '\x00-\x1f'
        regex = re.compile(r'[' + ctrl_chars + string.punctuation + '0-9\r\t\n]')

        nopunct = regex.sub(" ", text)  # delete stuff but leave at least a space to avoid clumping together
        tokens = nltk.word_tokenize(nopunct)
        tokens = [w for w in tokens if len(w) > 2]  # ignore a, an, to, at, be, ...
        tokens = [w.lower() for w in tokens]

        filtered_text = [word for word in tokens if word not in stop_words]
        filtered_text = [word for word in filtered_text if word not in food_stop_words]
        filtered_text = ' '.join(filtered_text)

        wc = WordCloud(background_color='white', min_font_size=10,
                        colormap='turbo').generate(filtered_text)

        self.ax[1,1].imshow(wc,interpolation='bilinear')
        
        self.ax[1,1].set_title('Word Cloud',pad=20,y=-0.3)
        self.ax[1,1].axis("off")
                
        
    def create_toxic_pie_chart(self):
        
        toxic_df = self.df
        
        data = pd.DataFrame(toxic_df['toxic_label'].value_counts()).reset_index()
        
        self.ax[0,1].pie(data['toxic_label'],labels=data['index'],autopct='%.0f%%')
        self.ax[0,1].set_title('Review Toxicity', pad=20, y=-0.3)


    def create_word_count_chart(self):
        wc_df = self.df
        
        text = wc_df.groupby('name')['review'].apply(lambda x : '\n'.join(x))[0]
        text = text.lower()
        
        ctrl_chars = '\x00-\x1f'
        regex = re.compile(r'[' + ctrl_chars + string.punctuation + '0-9\r\t\n]')
        
        nopunct = regex.sub(" ", text)  # delete stuff but leave at least a space to avoid clumping together
        tokens = nltk.word_tokenize(nopunct)
        tokens = [w for w in tokens if len(w) > 2]  # ignore a, an, to, at, be, ...
        tokens = [w.lower() for w in tokens]

        filtered_text = [word for word in tokens if word not in stop_words]
        filtered_text = [word for word in filtered_text if word not in food_stop_words]

        freq_df = pd.DataFrame(np.unique(filtered_text,return_counts=True)).T
        freq_df = freq_df.sort_values(by=[1],ascending=False)
        freq_df = freq_df.head(20)
        

        sns.barplot(x=freq_df[0], y=freq_df[1],palette='tab20c',ax=self.ax[1,0])
        self.ax[1,0].xaxis.set_tick_params(rotation=65)
        self.ax[1,0].set_ylabel('')
        self.ax[1,0].set_xlabel('Distribution of Keywords',fontsize='large')

        
    def create_sentiment_plot(self):
        categories = ['neutral','negative','positive']
        
        sentiment_df = self.df
        
        sns.countplot(data=sentiment_df,x='label',palette='pastel',
                      order=categories,ax=self.ax[0,0])
        self.ax[0,0].set_xlabel('')
        self.ax[0,0].set_ylabel('')

        self.ax[0,0].set_title('Sentiment Analysis', pad=20, y=-0.3)

    
    def visualize(self):

        self.create_subplot(figsize_width=16,figsize_height=8)
        if len(self.df) == 0:
            self.fig.suptitle('No Reviews found for this Restaurant with this Review Type',fontsize=20)
        else:
            self.create_word_count_chart()
            self.create_toxic_pie_chart()
            self.create_sentiment_plot()
            self.create_word_cloud()

            plt.subplots_adjust(hspace=0.4)
            plt.show()
            
        self.fig.savefig('visualization.jpg')
