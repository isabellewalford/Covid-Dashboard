"""
Functionality:
Modules includes all news handling.
"""
import json
import logging
import requests
from flask import Markup

#Logging
logging.basicConfig(level = logging.INFO,
filename='dashboard.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


with open('config.json', encoding="utf-8") as json_file:
    config_data = json.load(json_file)

def news_API_request(covid_terms:str)-> dict:
    """
    Requests data form a news API containing certain keywords
    returning a dicitonary containing a list of dictionaries.

    Arguments:
    covid_terms -- any string of words to be searched for
    """
    covid_terms = covid_terms.lower()
    keywords = []
    keywords = covid_terms.split(' ')
    url = (
        'https://newsapi.org/v2/everything?q='+
        '&'.join(keywords)+'&sortBy=popularity&language=en&apiKey='+
        config_data['API_KEY']
        )
    response = requests.get(url)
    logging.debug('News Requested')
    return response.json()

def update_news()-> list:
    """
    updates the articles in the news list from the API
    and extracts just the articles form the dictionary.

    Arguments:
    news_API_request -- function that returns data from the news API.
    """
    global news

    news = news_API_request('Covid COVID-19 coronavirus')['articles']
    logging.info('News updated')
    if len(news) == 0:
        logging.warning('No news found')
    return news

def add_read_more(news:list)-> list:
    """
    function adds a read more link to each news article dispalyed on the web link

    Arguments:
    news - list of dictionaries of news

    Returns:
    list - list of dictionaries of news with added url coding using markup
    """
    for article in news:
        more = Markup(f'<a href = {article["url"]}> Read More </a>')
        article['content'] = article['content'] + more
    return news
