import epaper
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import calendar
import time
import requests
from todoist_api_python.api import TodoistAPI
import datetime
from pathlib import Path


# remember to pip install (waveshare-epaper, PILLOW, requests, todoist_api_python)
#the epd module is not installable unless on a linux device *sigh*
# may need SpiDev module to install EPD module



#Initialze variables for E-Ink Display dimensions
EPD_Width = 800
EPD_Height = 480

# Intialize personal Tokens for to do list and Weather app ; Put your own personal API tokens here!
TODOIST_TOKEN = ""
WEATHER_TOKEN = ""
LAT = ""
LON = ""

def main():

    time.sleep(5) #gives pi time to set up network connections

    #global variable declerations
    global Debug_Mode; Debug_Mode = 0  #DEBUG TESTING: Draws both red and Black photos to "output" file. 
    global do_screen_update; do_screen_update = 1
    global TODOapi; TODOapi = TodoistAPI(TODOIST_TOKEN)
    global working_directory; working_directory = str(Path(__file__).absolute().parent)
    global epd; epd = epaper.epaper('epd7in5b_V2').EPD()

    if Debug_Mode == 0:
        print("==Initializing ...")
        epd.init() #EPD
        print('...done==')
    else:
        print("== Debug ==")

    global todo_response; todo_response = ""
    global calendar_width; calendar_width = 240
    global line_start; line_start = 48
    global weather_response

    #font intialization
    #calendar font
    global font_calendar; font_calendar = ImageFont.truetype(f"{working_directory}/font/RobotoMono-Bold.ttf", 18)
    global font_day; font_day = ImageFont.truetype(f"{working_directory}/font/Roboto-Black.ttf", 110)
    global font_weather; font_weather = ImageFont.truetype(f"{working_directory}/font/Roboto-Black.ttf", 30)
    global font_day_str; font_day_str = ImageFont.truetype(f"{working_directory}/font/Roboto-Light.ttf", 40)
    global font_month_str; font_month_str = ImageFont.truetype(f"{working_directory}/font/Roboto-Light.ttf", 25)
    
    #Icon List for weather Icons
    global font_weather_icons; font_weather_icons = ImageFont.truetype(working_directory + "/font/meteocons-webfont.ttf", 60)
    global icons_list; icons_list = {u'01d':u'B', u'01n':u'C', u'02d':u'H', u'02n':u'I', u'03d':u'N', u'03n':u'N', u'04d':u'Y', u'04n':u'Y', u'09d':u'R', u'09n':u'R', u'10d':u'R', u'10n':u'R', u'11d':u'P', u'11n':u'P', u'13d':u'G', u'13n':u'G', u'50d':u'M', u'50n':u'M'}

    #task font list
    global font_tasks_list_title; font_tasks_list_title = ImageFont.truetype(f"{working_directory}/font/Roboto-Light.ttf", 30)
    global font_tasks_list; font_tasks_list = ImageFont.truetype(f"{working_directory}/font/PTSerif-Regular.ttf", 20)
    global font_tasks_list_duedate; font_tasks_list_duedate = ImageFont.truetype(f"{working_directory}/font/PTSerif-Regular.ttf", 15)
    global font_tasks_list_priority; font_tasks_list_priority = ImageFont.truetype(f"{working_directory}/font/PTSerif-Regular.ttf", 10)
    global font_update_movement; font_update_movement = ImageFont.truetype(f"{working_directory}/font/PTSerif-Regular.ttf",15)

    #sets first day to monday
    calendar.setfirstweekday(0)

    #refresh wait commands
    global todoist_wait; todoist_wait = 60 #todo list wait timer
    global refresh_time; refresh_time = 600 #full refresh of screen
    start_time = time.time() + refresh_time

    while True:
        query_todo_list()
    
        if (do_screen_update == 1):
            do_screen_update = 0
            refresh_Screen()
            start_time = time.time() + refresh_time
        elif (time.time() - start_time) > 0:
            print("== Refresh ==")
            refresh_Screen()
            start_time=time.time() + refresh_time

        time.sleep(todoist_wait)


def query_todo_list():
    global todo_response
    global do_screen_update

    print("== Pinging TODO API ==")
    while True:
        try:
            new_todo_response = TODOapi.get_tasks() #Fixed API issues, should function correctly
            break

        except ValueError:
            print(" == TODO API failed ==")
            time.sleep(todoist_wait)

        except ConnectionError:
            print("== TODO could not connect ==")
            time.sleep(todoist_wait)

    if (new_todo_response != todo_response):
        print("== Task List Change ==")
        do_screen_update = 1
        todo_response = new_todo_response
        return True
    

def query_weather():
    global weather_response

    print("== pinging Weather API ==")
    while True:
        try:
            weather_response = requests.get("https://api.openweathermap.org/data/3.0/onecall", params={"appid":WEATHER_TOKEN,"lat":LAT, "lon":LON}).json()
            break

        except ValueError:
            print("== Weather API JSON Failed ==")
            time.sleep(refresh_time)

def refresh_Screen():
    global todo_response
    global Debug_Mode
    global weather_response
    line_location = 20

    #clear up black frame
    image_black = Image.open(f"{working_directory}/blanks/BK_Black.bmp")
    draw_black = ImageDraw.Draw(image_black)

    #clear up red frame
    image_red = Image.open(f"{working_directory}/blanks/BK_Red.bmp")
    draw_red = ImageDraw.Draw(image_red)

    #Calendar strings
    day_str = time.strftime("%A")
    day_number = time.strftime("%d")
    month_str = time.strftime("%B") + " " + time.strftime("%Y")
    month_cal = str(calendar.month(int(time.strftime("%y")), int(time.strftime("%m"))))
    month_cal = month_cal.split("\n",1)[1]
    update_moment = time.strftime("%I") + " " + time.strftime("%M") + " " + time.strftime("%p")

    #centers calendar
    w_day_str, h_day_str = font_day_str.getsize(day_str)
    x_day_str = (calendar_width/2) - (w_day_str / 2)

    #calendar num centered
    w_day_num, h_day_num = font_day.getsize(day_number)
    x_day_num = (calendar_width / 2) - (w_day_num / 2)

    #the setting for the month
    w_month_str, h_month_str = font_month_str.getsize(month_str)
    x_month_str = (calendar_width / 2) - (w_month_str / 2)

    #Calendar and Task header drawn
    draw_black.rectangle((0, 0, 240, 480), fill = 0) #calendar area
    draw_black.text((10,220), month_cal, font = font_calendar, fill = "#fff") #calendar text
    draw_black.text((x_day_str, 5), day_str, font = font_day_str, fill = "#fff") #day calendar text
    draw_black.text((x_day_num,35), day_number, font= font_day, fill = "#fff")#day number calendar text
    draw_black.text((x_month_str, 150), month_str, font = font_month_str, fill = "#fff")# month text
    draw_black.line((10,380,230,380), fill = "#fff")#line for weather
    draw_black.line((245,380,785,380), fill = 0)# footer

    draw_red.rectangle((245,0,800,55), fill = 0) #task banner
    draw_red.text((255,10), "To Do List", font = font_tasks_list_title, fill = "#fff") #task text
    draw_black.text((690,450),update_moment, font= font_update_movement, fill = '#fff')# update text

    #weather variables
    query_weather()
    current_weather = weather_response['current']['weather'][0]['main']
    current_icon = weather_response['current']['weather'][0]['icon']

    
    current_temp = str(round(((int(weather_response['current']['temp']) - 273.15) * 9/5 + 32))) + '° F'
    forecast_weather = weather_response['daily'][0]['weather'][0]['main']
    forecast_icon = weather_response['daily'][0]['weather'][0]['icon']
    forecast_min_max = str(round(((int(weather_response['daily'][0]['temp']['min'])- 273.15) * 9/5 + 32))) + '° F / ' + str(round(((int(weather_response['daily'][0]['temp']['max'])- 273.15) * 9/5 + 32))) + "° F"

    if(len(current_weather) >= 9):
        current_weather = current_weather[0:7] + '.'
    if(len(forecast_weather) >= 9):
        forecast_weather = forecast_weather[0:7] + '.'


    #weather text locations/ dimensions
    w_weather_icon,h_weather_icon = font_weather_icons.getsize(icons_list[str(current_icon)]) #weather width/height
    y_weather_icon = 420 + ((384 - 320) / 2) - (h_weather_icon) #weather icon height from top
    w_current_weath, h_current_weath = font_weather.getsize(current_weather) #current weather width/height
    w_current_temp, h_current_temp = font_weather.getsize(current_temp) #current temp width/height
    w_forecast_weather, h_forecast_weather = font_weather.getsize(forecast_weather) #forecast weather width/height
    w_forecast_temp_min_max, h_forecast_temp_min_max = font_weather.getsize(forecast_min_max) #forecast temp width/height

    x_current_temp = ((w_current_weath - w_current_temp) / 2 + 30 + w_weather_icon)
    x_forecast_temp = ((w_forecast_weather - w_forecast_temp_min_max) / 2 + 80 + 240 + w_weather_icon)
    
    #draw all the weather related information
    draw_black.text((10,y_weather_icon), icons_list[str(current_icon)], font = font_weather_icons, fill = "#fff") #current weather icon
    draw_black.text((30 + w_weather_icon, y_weather_icon - 10), current_weather, font = font_weather, fill = '#fff') #current weather status 
    draw_black.line((10 + w_weather_icon, y_weather_icon + h_weather_icon/2, 50 + w_weather_icon + w_current_weath, y_weather_icon + h_weather_icon/2), fill = '#fff') #line seperator
    draw_black.text((x_current_temp, y_weather_icon + h_weather_icon/2 + 10), current_temp, font = font_weather, fill = '#fff') #current tempurature

    #draw arrow
    draw_black.rectangle((240 - 15, y_weather_icon + 20, 240, y_weather_icon + h_weather_icon - 20), fill = '#fff')#rectangle portion of arrow
    draw_black.rectangle((240, y_weather_icon + 20, 240 + 10, y_weather_icon + h_weather_icon - 20), fill = 0) #draws second part of the rectagnle
    draw_black.polygon([245, y_weather_icon + 10, 245, y_weather_icon + h_weather_icon - 10, 260, y_weather_icon + h_weather_icon/2], fill = 0)# triangle portion of arrow

    #forecast weather
    draw_black.text((30 + 240, y_weather_icon), icons_list[str(forecast_icon)], font = font_weather_icons, fill = 0) #forecast weather icon
    draw_black.text((80 + 240 + w_weather_icon, y_weather_icon - 10), forecast_weather, font = font_weather, fill = 0) #forecast weather status
    draw_black.line((40 + 240 + w_weather_icon, y_weather_icon + h_weather_icon/2, 120 + 240 + w_weather_icon + w_forecast_weather, y_weather_icon + h_weather_icon/2), fill = 0) #line seperator
    draw_black.text((x_forecast_temp, y_weather_icon + h_weather_icon/2 + 10), forecast_min_max, font = font_weather, fill = 0) #forecast tempurature
    
    for task in todo_response:
        item = str(task.content)
        priority = str(task.priority)
        
        if (len(item) > 55):
            item = item[0:55] + '...'

        if task.due == None:
            due_date = -1
        else:
            due_date = (int(task.due.date.split('-')[0]) - 1970) * 31556926 + (int(task.due.date.split('-')[1]) - 1) * 2629743 + (int(task.due.date.split('-')[2]) - 1) * 86400
        
        if((due_date < time.time()) & (due_date > 0)):
            temp_draw = draw_red
        else:
            temp_draw = draw_black

        #draw individual tasks
        temp_draw.text((265, line_start + line_location - 7), item, font = font_tasks_list, fill = 0) #text for task
        temp_draw.chord((247.5, line_start + 2 + line_location, 257.5, line_start + 12 + line_location), 0, 360, fill = 0) #circle for priority
        temp_draw.text((250, line_start + 2 + line_location), priority, font = font_tasks_list_priority, fill = '#fff') #priority Number
        temp_draw.line((250, line_start + 18 + line_location, 800, line_start + 18 + line_location), fill = 0) #footer for each task
        if due_date != -1:
            temp_draw.rectangle((755, line_start + 2 + line_location, 800, line_start + 18 + line_location), fill = 0) #rectangle for due date
            temp_draw.text((762.5, line_start + 3.5 + line_location - 3), task.due.string, font = font_tasks_list_duedate, fill = '#fff') #text for due date

        if((due_date < time.time()) & (due_date > 0)):
            draw_red = temp_draw
        else:
            draw_black = temp_draw
        
        line_location += 26
        if (line_start + line_location + 28 >= 360):
            
            #draw additional tasks list
            draw_red.rectangle((710, line_start + 2 + line_location, 800, 380), fill = 0) #draws the rectangle for too many tasks

            tasks_not_shown = '...&' + str(len(todo_response) - 11) + ' More...'
            w_not_shown, h_not_shown = font_tasks_list_duedate.getsize(tasks_not_shown)
            x_not_shown = 710 + ((800 - 710) / 2) - (w_not_shown / 2)

            draw_red.text((x_not_shown, line_start + 8.5 + line_location), tasks_not_shown, font = font_tasks_list_duedate, fill = '#fff')#draws the text
            break


    if Debug_Mode == 1:
        print('== view E-Ink... ==')
        image_black.save(f'{working_directory}/output/Black_Frame.png')
        image_red.save(f'{working_directory}/output/Red_Frame.png')
        image_merged = Image.blend(image_black, image_red, 0.5)
        image_merged.save(f"{working_directory}/output/Merged_image.png")
        print('== ...done ==')
    else:
        print('== Updating Paper... ==')
        epd.display(epd.getbuffer(image_black), epd.getbuffer(image_red)) #EPD
        print('== ...done ==')
