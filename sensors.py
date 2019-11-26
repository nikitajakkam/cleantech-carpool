# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 14:55:29 2019

@author: Felipe
"""

from dataclasses import dataclass
import random
from typing import List

from db import get_db

#https://www.geeksforgeeks.org/graph-plotting-in-python-set-1/
import matplotlib.pyplot as graphit
import io
import base64

sensor_locations = ['Living Room', 'Kitchen', 'Porch', 'Bedroom', 'Greenhouse',
                    'Hallway', 'Elephant room']

@dataclass
class sensor:
    name: str
    temp: float
    humidity: float
    
    def __init__(self, name: str, temp: int, humidity: int): #just initializes
        self.temp = temp
        self.humidity = humidity
        self.name = sensor_locations[random.randint(0, (len(sensor_locations) - 1))] if (not (name)) else name
        
    def current_vals(self):
        nt = self.temp + (random.randint(-5,5))/10 #new temperature
        self.temp = nt if (nt > -273) else self.temp #kelvin cause why not
        nh = self.humidity + (random.randint(-3,3))/10 #new humidity
        self.humidity = nh if ((nh > 0) and (nh < 100)) else self.humidity #humidity only between 0-100
        
    
Sensors : List[sensor] = []

def plot_data(sensors, which):
    pic = io.BytesIO()
    vals : List[int] = []
    names = []
    bars = range(len(sensors)) #how many bars
#    for a in bars:
#        a = a*2
    
    ez_condition = True if (which == 'temp') else False
    for i in sensors:
        vals.append(i.temp) if (ez_condition) else vals.append(i.humidity)
        names.append(i.name)
        
    graphit.bar(bars, vals, tick_label = names, width = 0.6, color=['red', 'blue'])
    graphit.xlabel('Temperature(C)') if (ez_condition) else graphit.xlabel('Humidity')
    graphit.ylabel('Value')
    graphit.title('Visualized Readings')
    graphit.savefig(pic, format='png')
    pic.seek(0) #https://technovechno.com/creating-graphs-in-python-using-matplotlib-flask-framework-pythonanywhere/
    pic_url = base64.b64encode(pic.getvalue()).decode()
    graphit.close()
    return 'data:image/png;base64,{}'.format(pic_url)
#    for returning it https://stackoverflow.com/questions/11017466/flask-to-return-image-stored-in-database/11017839#11017839
#    https://stackoverflow.com/questions/50728328/python-how-to-show-matplotlib-in-flask
#    
#def static_test_setup():
#    usercount = 10
#    nems = 'User'
#    s_count = 0
#    for i in range(usercount):
#        s_lim = random.randint(1,3) #sensor_limit
#        usr = user(str(nems+str(i)))
#        for j in range(s_lim):
#            s_count = s_count + 1
#            sen = sensor(str(s_count), random.randint(50,70), random.randint(20,40))
#            usr.add_sensor(s_count)
#            Sensors.append(sen)
#        Users.append(usr)

            
        
    
