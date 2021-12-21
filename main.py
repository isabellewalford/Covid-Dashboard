"""
Functionality:
Module renders the html template,
uses other modules to process data and schedule updates for the data,
uses requests module to get data from the user and update the appropriate structure.
"""

#Imports
import logging
from flask import Flask, request, render_template, Markup
from covid_news_handling import update_news, add_read_more
from covid_data_handler import update_data, find_difference
from covid_data_handler import schedule_covid_updates
from covid_data_handler import s as data_s
from global_var import updates, news, local_data, national_data


#Variables
app = Flask(__name__)
news = update_news()
news = add_read_more(news)
local_data,national_data = update_data()

#Logging
logging.basicConfig(level = logging.INFO, filename='dashboard.log',
filemode='w', format='%(name)s - %(levelname)s - %(message)s')

@app.route('/')
def home()-> str:
    """
    Starts the scheduled events and renders the html template, declaring the variables.
    """
    return render_template(
        'index.html',
        title = Markup("<b>Covid Data and News Dashboard</b>"),
        location = Markup('<b>Exeter</b>'),
        local_7day_infections = local_data[0],
        nation_location = Markup('<b>England</b>'),
        national_7day_infections = national_data[0],
        hospital_cases = Markup('<b>Hospital Cases:</b>')+str(national_data[1]),
        deaths_total = Markup('<b>Deaths:</b>')+ str(national_data[2]),
        news_articles = news[0:4],
        image = 'me_and_olivia.jpg',
        updates = updates
        )

@app.route('/index')
def index()-> str:
    """
    Runs any scheduled events, takes user inputs and
    adds it to the correct data structure or processes it to give an ouput.
    """
    global updates, local_data, national_data, news
    data_s.run(blocking=False)
    schedule_covid_updates(0,updates)
    logging.debug('updates should now be scheduled')

    if request.args.get('notif'):
        news_story = request.args.get('notif')
        for i, each in enumerate(news):
            if each['title'] == news_story:
                del news[i]
                logging.info('News removed')
                break

    if request.args.get('two'):
        name = request.args.get('two')
        time = request.args.get('update')
        difference = find_difference(request.args.get('update'))
        data_update = request.args.get('covid-data')
        news_update = request.args.get('news')
        repeat = request.args.get('repeat')
        name = {
            'title':name,
            'content':time,
            'difference':difference,
            'data': data_update,
            'news': news_update,
            'repeat': repeat,
            'scheduler':True,
            'event': []
        }
        updates.append(name)
        logging.debug('Updated appended to list.')

    if request.args.get('update_item'):
        item = request.args.get('update_item')
        for i, each in enumerate(updates):
            if each['title'] == item:
                for event in each['event']:
                    try:
                        data_s.cancel(event)
                        logging.info('update cancelled')
                    except:
                        logging.warning('Scheduled event is not in the queue.')
                del updates[i]
                break

    return home()

if __name__ == '__main__':
    app.run()
