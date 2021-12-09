"""
Functionality:
Module renders the html template, 
uses other modules to process data and schedule updates for the data,
uses requests module to get data from the user and update the appropriate structure.
"""

#Imports
import sched
import time
from flask import Flask, request, render_template, Markup
from covid_news_handling import update_news, add_read_more
from covid_data_handler import update_data, find_difference
from covid_data_handler import schedule_covid_updates
from global_var import updates, news, local_data, national_data

#Variables
app = Flask(__name__)
news = update_news()
news = add_read_more(news)
local_data,national_data = update_data()
s = sched.scheduler(time.time,time.sleep)


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
        hospital_cases = 'Hospital Cases:'+str(national_data[1]),
        deaths_total = 'Deaths:'+str(national_data[2]),
        news_articles = news[0:3],
        image = 'me_and_olivia.jpg',
        updates = updates
        )

@app.route('/index')
def index()-> str:
    """
    Runs any scheduled events, takes user inputs and
    adds it to the correct data structure or processes it to give an ouput.
    """
    s.run(blocking=False)
    schedule_covid_updates(0,updates)

    if request.args.get('notif'):
        news_story = request.args.get('notif')
        for i, each in enumerate(news):
            if each['title'] == news_story:
                del news[i]
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
            'scheduler':True
        }
        updates.append(name)

    if request.args.get('update_item'):
        item = request.args.get('update_item')
        for i, each in enumerate(updates):
            if each['title'] == item:
                s.cancel(each['content'])
                del updates[i]
                break

    for i, each in enumerate(updates):
        if each['difference']< 60:
            del news[i]
            break
 
    return home()

if __name__ == '__main__':
    app.run()
