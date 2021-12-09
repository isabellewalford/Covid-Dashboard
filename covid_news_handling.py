"""
Functionality:
Modules includes all news handling.
"""

import requests
import json
from flask import Markup

with open('config.json') as json_file:
    config_data = json.load(json_file)

def news_API_request(covid_terms)-> dict:
    """
    Requests data form a news API containing certain keywords
    returning a dicitonary containing a list of dictionaries.

    Arguments:
    covid_terms -- any string of words to be searched for
    """
    covid_terms = covid_terms.lower()
    keywords = []
    keywords = covid_terms.split(' ')
    url = ('https://newsapi.org/v2/everything?q='+'&'.join(keywords)+'&sortBy=popularity&language=en&apiKey='+config_data['API_KEY'])
    response = requests.get(url)
    print('news updated')
    return response.json()

def update_news()-> list:
    """
    updates the articles in the news list from the API and extracts just the articles form the dictionary.

    Arguments:
    news_API_request -- function that returns data from the news API.
    """
    news = news_API_request('Covid COVID-19 coronavirus')['articles']
    return news

def add_read_more(news)-> list:
    for article in news:
        more = Markup(f'<a href = {article["url"]}> Read More </a>')
        article['content'] = article['content'] + more
    return news
