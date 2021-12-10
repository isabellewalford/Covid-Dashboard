"""
Functionality:
Module handles all covid data and scheduling.
"""

# Imported Modules
from typing import List
from uk_covid19 import Cov19API
import datetime 
import time
import sched
from global_var import updates, local_data, national_data, news
from covid_news_handling import update_news, news_API_request
s = sched.scheduler(time.time, time.sleep)
import json

with open('config.json') as json_file:
    config_data = json.load(json_file)

# Functions for CSV formatted static file
def parse_csv_data(csv_filename) -> list: 
    """
    Opens a csv file and reads each row appending it to a list,
    returning the list.

    Keyword arguments:
    csv_filename -- the name of a csv formatted file in the same file path as the python file.
    """  

    # Opens then file and adds each row to a long list 
    with open(csv_filename,'r') as file:
        data = file.readlines()
        list = []
        for row in data:
            list.append(row)
    return list
def process_covid_csv_data(covid_csv_data) -> int:
    """
    Takes the data from the previous function and processes it returning 
    
    keyword arguments:
    covid_csv_data -- csv data parsed through the 'parse_cvs_function' as a list
    """
    # Defining the variables before adding values to it 
    last7days_cases = 0 
    current_hospital_cases = 0 
    total_deaths = 0 
    
    # Iterates through only the 7 rows needed spliting row into induvidual values so they can be added to the variable
    for each in range(3,10):
        data = covid_csv_data[each].split(',')
        last7days_cases += int(data[6])

    # Splits only the row needed for the variable so that it can be defined and changed to an integer value
    
    data = covid_csv_data[1].split(',')
    current_hospital_cases = int(data[5])

    data = covid_csv_data[14].split(',')
    total_deaths = int(data[4])


    return last7days_cases , current_hospital_cases , total_deaths

def covid_API_request(location = 'Exeter', location_type = 'ltla') -> dict:
    """
    Requests data and from the official covid API and ouputs a dictionary.

    Arguments:
    location -- location of the data that is to be requested. Default is Exeter
    location_type -- the type of area input into the loaction argument, can be ltla, utla and nation.
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

def process_json_data(covid_API_data) -> list:
    """
    Processes the data that is output by the covid API function returning a list of values.

    Arguments:
    covid_API_data -- data that is formatted as a json file from the covid API

    Returns:
    list - list of 3 integer values: last7days_cases, hospitalCases, cumDeaths28DaysByPublishDate
    """

    list = []
    last7days_cases = 0
    # The data is list of dictionaries within a dictionary so this gets the list within in the dictionary that contains all the data 
    just_data = covid_API_data['data']
    # Iterates from 0-7 to get the value of cases in the last 7 days and adds each to the variable 'last7days_cases'
    for each in range(7):
        data = just_data[each]
        last7days_cases += data['newCasesByPublishDate']
    list.append(last7days_cases)
    # The data is list of dictionaries within a dictionary so this gets the list within in the dictionary that contains all the data 
    list.append((just_data[0])['hospitalCases'])
    list.append((just_data[0])['cumDeaths28DaysByPublishDate'])
    return list

def update_data() -> tuple:
    """
    Assigns values to the variables for local and national data to update them from the covid API.

    Arguments:
    process_json_data -- function that is previously defined
    """
    print('data updated')
    local_data= process_json_data(covid_API_request(location=config_data['local_area'], location_type= 'ltla'))
    national_data= process_json_data(covid_API_request(location=config_data['national_area'], location_type= 'nation'))
    return local_data, national_data

def find_difference(time)-> int:
    """
    finds the difference in an imput time and the current time

    Arguments:
    time -- any time in the format hh:mm 

    Returns:
    int -- returns the time difference between a given time and the current time
    """

    current_time = datetime.datetime.now()
    h = current_time.hour
    m = current_time.minute
    current = h*60*60 + m*60
    hours, mins = time.split(":")
    update = (int(hours)*60*60)+(int(mins)*60)
    difference =  update - current
    if difference <0:
        difference = difference + 24*60*60
    return difference

def remove_dict(dict, list) -> list:
    """
    removes a dictionary from a given list

    Arguments:
    dict -- an dictionary
    list -- any list containing the dictionary

    Returns:
    int -- returns the time difference between a given time and the current time
    """
    name = dict['title']
    for i, each in enumerate(list):
        if each['title'] == name:
                del list[i]
                break
    return list

def add_update(dict)-> list:
    """
    Functon changes adds update to the list of updates to be scheduled 

    Arguments:
    dict -- dictionary of information for a scheduled update

    Returns:
    list -- list of scheduled updates
    """
    dict['scheduler'] == True
    print('update added')
    updates.append(dict)
    return updates
        
def schedule_covid_updates(update_interval,update_name)-> list:
    global updates,news,local_data,national_data
    """
    Schedules events based on the data input into a web server

    Arguments:
    update_interval -- difference
    update_name -- list of dictionaries containing data on what kind of update, 
    the time difference and whether it should be repeated.

    Returns:
    list -- list of any scheduled updates
    """

    for i, each in enumerate(update_name):
        print(each)
        update_interval = each['difference']
        e1 = each['content']
        if each['scheduler']== True:
            print('scheduler is true')
            if each['data'] == 'covid-data' and each['news'] == 'news':
                e1 = s.enter(update_interval,1,update_data)
                e1 = s.enter(update_interval,1,update_news)
            elif each['data'] == 'covid-data': 
                e1 = s.enter(update_interval,1,update_data)
                print('data scheduled')
            elif each['news'] == 'news':
                e1 = s.enter(update_interval,1,update_news)
                print('news scheduled')
            else:
                del update_name[i]
            e1 = s.enter(update_interval,1,remove_dict,(each,updates))
            each['scheduler']=False

            if each['repeat'] == 'repeat':
                print('repeat scheduled')
                e1 = s.enter(24*60*60*60,1,add_update,each)
    return updates
