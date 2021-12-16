# Covid Dashboard 
## Introduction
This Covid dashboard is a Continuous assessment for ECM1400 Programming that displays up to date covid data and news form APIs and sets scheduled updates for each.

## Prerequisites
**Version**:  Python 3.9.7

## Installation
	pip install flask
	pip install pytest
	pip install uk-covid19
	pip install pylint

*use pip3 for mac to install on the correct version of python*

## Getting started tutorial

***How to run the code:***
1. in the terminal navigate to the correct directory using `cd` and run:

		python3 main.py
2. then open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in any web browser.

***How to use the code:***
1. to schedule any update
	- add a time by clicking the clock symbol or typing
	- then add an update name 
	- tick the repeat box if you want to update to be repeated at the same time again
	- then tick either news covid data or both to decide what data should be scheduled to update
	- finally press submit or enter to schedule the update

***Personaling the dashboard***

Within the config.json file the places the data comes from can be easily changed.

**National location:**
- this can be any national location (England, Northern Ireland, Scotland, and Wales)
- note: the area type does not need to be defined this parameter is automatically a nation type
- this can be changed by changing th4 value for the key "national_area"

**Local location:**
- for the local location you must add two values if you want to change this
- firstly the value for the key "local_area" which should be the name of the area for example Exeter
- then the "area_type" value should correspond to this area, it can be a ltla or utla
data on what parameters can be added is on the covid 19 API website at 

[https://coronavirus.data.gov.uk/details/developers-guide/](https://coronavirus.data.gov.uk/details/developers-guide/).
 
## Testing

with the correct directory run pytest in the terminal.

## Github

*In order to use this dashboard you must input ypur own API key into the config.json file.*

This can be done by going to the news API website and creating an acount to get an API key, this can be found at [https://newsapi.org/](https://newsapi.org/).

Then this should be input into the file named config.json where the empty value is with the key "API_KEY".



