#DimSummary: Opinion Summarization of Yelp Restaurant Reviews
## Intro
This project is dedicated to create an end-to-end product providing Yelp review summarization. Our team members are 
- Kayhan Eryilmaz (kayhankubi@gmail.com)
- Chenxi Li (lichenxi1113@gmail.com)
- Brooks Diwu (brooksdiwu@gmail.com)
- Kelley Chu
- Justin Chan

The Project Presentation:[Code Link](https://github.com/kayhanliao/DimSummary/blob/main/Dim%20Summary%20Pitch.pdf)

In this project, we used **Yelp API, OpenAI API and web scraper** to retrieve restaurants' basic information and reviews. We created **MongoDB Atlas** to shard the raw data from **Google Cloud Platform (GCP)** buckets into clusters to improve the efficiency of reading and writing data. After performing data preprocessing, we trained and fine-tuned the **BART NLP model** to create review summarization for each restaurant. In order to keep our training data and model updated, we set up a pipeline and schedule to run it using **Airflow**. We created an web app using **Flask** and deployed it using **AWS** so that it can be accessed by anyone with log-in credentials.
![image](https://user-images.githubusercontent.com/82719564/233866687-2d09314c-7ad6-4d11-97ba-43a9d8048241.png)
(chart needs to be updated)

## Modeling (BART)
[Code Link](https://github.com/kayhanliao/restaurant-review-generation/tree/main/bart_experiments)

In the modern era, we’re able to fine tune existing robust pretrained models and modify them to fit our specific needs. BART stands for Bidirectional Auto-Regressive Transformers and is used for causal sequence to sequence generation. Without any fine tuning, the vanilla BART model is able to generate summaries given an input text. This is used for summarizing academic papers, news articles, etc.

In order to generate summaries, we first needed to tokenize the concatenated reviews. BART has its own tokenizer that comes with the pretrained model. In order to efficiently tokenize the dataset, we wrote a function that would map the tokenizations onto the dataset efficiently. We would make sure to add “summarize: ” in front of every review batch since this is how you prompt the generative model to generate a summary. This is done by training the AutoTokenizer function from Hugging Face which is an alias for the BART tokenizer, allowing you to change words and chars of the text into appropriate input ids. An important note is that the max input size for a BART model (and most models) is 1024 tokens, which is roughly equivalent to 4096 (4 chars per token). We also set our generation output size to be 150 tokens which is around 400-600 chars. Note a word on average is 5-7 chars.  Our resulting model had a resulting ROGUE-1 score of 0.19

*Example Output*

Here is the summarization of top-rated reviews comes out of our fine-tuned BART model for Daeho restaurant:
Daeho is a popular restaurant in Japantown, San Francisco. The food is delicious and the staff is friendly, attentive, and knowledgeable about the menu. However, some dishes are pricey, and some are not worth the wait. The restaurant is located in an industrial area, and the set up of tables is smartly placed to utilize the space. Overall, Daeho has a great atmosphere and delicious food.

## Web App
[Code Link](https://github.com/kayhanliao/restaurant-review-generation/tree/main/webapp/app.py)

[Web App Link](http://yelpgpt.us-east-1.elasticbeanstalk.com/)

### Home Page

![image](https://user-images.githubusercontent.com/82719564/233867583-73e252d8-5813-49cc-831c-6a7aaa0f7553.png)

### Search Result Page:

![image](https://user-images.githubusercontent.com/82719564/233867610-362a39f8-b193-4a64-a6e9-15a03c24c03c.png)

### About Page:

![image](https://user-images.githubusercontent.com/82719564/233867624-2327704a-d218-450d-a2e7-c5b0a46ea076.png)
