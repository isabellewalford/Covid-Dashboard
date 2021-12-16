"""
Functionality:
Module handles all covid data and scheduling.
"""

# Imported Modules
import time
import sched
import datetime
import json
import logging
from uk_covid19 import Cov19API
from global_var import updates
from covid_news_handling import update_news
s = sched.scheduler(time.time, time.sleep)

#Logging
logging.basicConfig(level = logging.INFO, filename='dashboard.log',
filemode='w', format='%(name)s - %(levelname)s - %(message)s')


with open('config.json', encoding="utf-8") as json_file:
    config_data = json.load(json_file)

# Functions for CSV formatted static file
def parse_csv_data(csv_filename:str) -> list:
    """
    Opens a csv file and reads each row appending it to a list,
    returning the list.

    Arguments:
    csv_filename -- the name of a csv formatted file in the same file path as the python file.

    Returns:
    list - list of each row within the csv file
    """

    # Opens then file and adds each row to a long list
    with open(csv_filename,'r', encoding ='utf-8') as csv_f:
        data = csv_f.readlines()
        file = []
        for row in data:
            file.append(row)
    return file
def process_covid_csv_data(covid_csv_data:list) -> int:
    """
    Takes the data from the previous function and processes it returning

    Arguments:
    covid_csv_data -- csv data parsed through the 'parse_cvs_function' as a list

    Returns:
    int - 3 integers containing the required data
    """
    # Defining the variables before adding values to it
    last7days_cases = 0
    current_hospital_cases = 0
    total_deaths = 0

    # Iterates through only the 7 rows needed spliting row
    # into induvidual values so they can be added to the variable
    for each in range(3,10):
        data = covid_csv_data[each].split(',')
        last7days_cases += int(data[6])

    # Splits only the row needed for the variable
    # so that it can be defined and changed to an integer value

    data = covid_csv_data[1].split(',')
    current_hospital_cases = int(data[5])

    data = covid_csv_data[14].split(',')
    total_deaths = int(data[4])

    return last7days_cases , current_hospital_cases , total_deaths

def covid_API_request(location:str = 'Exeter', location_type:str = 'ltla') -> dict:
    """
    Requests data and from the official covid API and ouputs a dictionary.

    Arguments:
    location -- location of the data that is to be requested.
    Default is Exeter
    location_type -- the type of area input into the loaction argument,
    can be ltla, utla and nation.
    Default is ltla which is the location type for exeter.

    Returns:
    dict -- dictionary of covid data
    """

    # Defines where the data is from
    area = [
    'areaType='+location_type,
    'areaName='+location
    ]
    # Defines the structure of the data that the API will return
    data_structure = {
        "date": "date",
        "areaName": "areaName",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumDeaths28DaysByPublishDate": "cumDeaths28DaysByPublishDate",
        "hospitalCases": "hospitalCases"
    }
    # Creates a list of dictionaries within a dictionary
    api = Cov19API(filters=area, structure=data_structure)
    data = api.get_json()
    return data

def process_json_data(covid_API_data:json) -> list:
    """
    Processes the data that is output by the covid API function returning a list of values.

    Arguments:
    covid_API_data -- data that is formatted as a json file from the covid API

    Returns:
    list - list of 3 integer values: last7days_cases, hospitalCases, cumDeaths28DaysByPublishDate
    """
    #defining local variables
    values = []
    last7days_cases = 0
    just_data = covid_API_data['data']

    #adding the last 7 days data to one variable
    for each in range(7):
        data = just_data[each]
        last7days_cases += data['newCasesByPublishDate']

    #adding each variable to a list to be returned
    values.append(last7days_cases)
    values.append((just_data[0])['hospitalCases'])
    values.append((just_data[0])['cumDeaths28DaysByPublishDate'])
    return values

def update_data() -> tuple:
    """
    Assigns values to the variables for local and national data to update them from the covid API.

    Arguments:
    process_json_data -- function that is previously defined
    """

    local_data= process_json_data(covid_API_request(location=config_data['local_area'],
    location_type= config_data['area_type']))
    national_data= process_json_data(covid_API_request(location=config_data['national_area'],
    location_type= 'nation'))
    logging.info('Data updated')

    return local_data, national_data

def find_difference(time_str:str)-> int:
    """
    finds the difference in an imput time and the current time

    Arguments:
    time_str -- any time in the format hh:mm

    Returns:
    int -- returns the time difference between a given time and the current time
    """
    #converts current time to seconds
    current_time = datetime.datetime.now()
    hou = current_time.hour
    mins = current_time.minute
    current = hou*60*60 + mins*60

    #converts update time to seconds
    hours, mins = time_str.split(":")
    update = (int(hours)*60*60)+(int(mins)*60)

    #checks if it was scheduled for a time before the current time
    # and schedules for the next day if it was
    difference =  update - current
    if difference <0:
        logging.debug('difference was negative')
        difference = difference + 24*60*60
    return difference

def remove_dict(update:dict, updates_list:list) -> list:
    """
    removes a dictionary from a given list

    Arguments:
    update -- an dictionary
    updates_list -- any list containing the dictionary

    Returns:
    int -- returns the time difference between a given time and the current time
    """

    name = update['title']
    for i, each in enumerate(updates_list):
        if each['title'] == name:
            del updates_list[i]
            logging.info('Update removed')
            break
    return updates_list

def add_update(info:dict)-> list:
    """
    Functon changes adds update to the list of updates to be scheduled

    Arguments:
    dict -- dictionary of information for a scheduled update

    Returns:
    list -- list of scheduled updates
    """

    info['scheduler'] = True
    logging.debug('Repeat update added')
    updates.append(info)
    return updates

def schedule_covid_updates(update_interval:int,update_name:list)-> list:
    """
    Schedules events based on the data input into a web server

    Arguments:
    update_interval -- difference
    update_name -- list of dictionaries containing data on what kind of update,
    the time difference and whether it should be repeated.

    Returns:
    list -- list of any scheduled updates
    """

    if update_data is not list:
        update_name = updates

    for i, each in enumerate(update_name):
        update_interval = each['difference']
        if each['scheduler'] is True:
            logging.debug('Scheduler is True.')

            if each['data'] == 'covid-data' and each['news'] == 'news':
                event = s.enter(update_interval,1,update_data)
                each['event'].append(event)
                event = s.enter(update_interval,1,update_news)
                each['event'].append(event)
                logging.debug('Both update scheduled')

            elif each['data'] == 'covid-data':
                event = s.enter(update_interval,1,update_data)
                each['event'].append(event)
                logging.debug('Data update scheduled')

            elif each['news'] == 'news':
                event = s.enter(update_interval,1,update_news)
                each['event'].append(event)
                logging.debug('News update scheduled')

            else:
                del update_name[i]
                logging.debug('Removed due to data or news not being true')

            event = s.enter(update_interval,1,remove_dict,(each,updates))
            logging.debug('Remove update scheduled')
            each['event'].append(event)
            each['scheduler'] = False

            if each['repeat'] == 'repeat':
                event = s.enter(24*60*60*60,1,add_update,each)
                each['event'].append(event)
                logging.debug('Repeat scheduled to add update')

            s.run(blocking=False)

    return updates
