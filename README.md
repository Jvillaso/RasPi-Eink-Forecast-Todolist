# RasPi-Eink-Forecast-Todolist
This project displays your own todo list, weather, and calendar functions on a changable sized E-ink display. This program is run on python and is made to function on a rasberry pi, specifically a raspberry pi zero W. Since APIs are requested from the internet, an internet connection is required for the program.

## Getting Started
In order to get started, you need to create an account with:

[Todoist](https://app.todoist.com/) - To Do list app that you can add tasks to

[OpenWeather](https://openweathermap.org/) - Open weather app that tracks real time weather

After making accounts, you will need api keys for both of these websites, your personal keys are required inside the code as TODOIST_TOKEN and WEATHER_TOKEN variables. 

You will also need to update LAT and LON variables with each value being latitude and lontitude respectively of desired location for weather data.

### Installing
A few modules will have to be installed before running the program. Some of these modules are only able to be installed on linux OS or a raspberry pi.

Below are the pip modules needed for the code.

```
pip install waveshare-epaper

pip install todoist-api-python

pip install PILLOW
```

After installing the modules, the code should be ready to run. If you are getting an error with installing modules due to "spidev" or "RPGIO" it may be related to having to install the module specifically on the raspberry pi.

## Running Code
To run the program, you simply need to run main.py in the working directory. This can be done by simply running it or by running the code below in the working directory:

```
python main.py
```

## Built With
[Epaper](https://github.com/waveshareteam/e-Paper) - Epaper module for updating the display

[ToDoist](https://pypi.org/project/todoist-api-python/) - todoist module used for updating the todo list

## Versioning
0.1.0

## Authors
* **Joshua Villasol** - *Wrote and tested code*
