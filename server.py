# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 14:21:53 2019

@author: Felipe
"""
#example from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
from sensors import Users
from sensors import Sensors
from sensors import static_test_setup
from flask import Flask, redirect
from flask import request
#from sensors import read_sensor
#https://stackoverflow.com/questions/22947905/flask-example-with-post
app = Flask(__name__)

set_up = False #if server has been initalized


@app.route('/miniproj/<usr_id>', methods = ['GET', 'POST', 'DELETE'])
def showstuff(usr_id):
    if request.method == 'GET':
        ret_str = 'User ' + str(usr_id)
        uid = int(usr_id)
        print(uid, len(Users), sep=' , ')
        if (uid >= len(Users)):
            return 'User exceeds maximum'
        else:
            usr = Users[uid]
            usr.visits = usr.visits + 1
            for i in usr.probes:
                if (i <= len(Sensors)) :
                    sen = Sensors[i-1]
                    sen.current_vals() #update values
                    ret_str += '<p>Sensor: ' + sen.name 
                    ret_str += '<p>Humidity: ' + str(sen.humidity)
                    ret_str += ', Temperature: ' + str(sen.temp)
                    ret_str += '</p><p></p>'
                else :
                    ret_str += str(i) + ' Broke it. Only ' + str(len(Sensors)) + ' sensors'
            
            return ret_str
    else:
        return "I have no idea what you're trying to do"
   
    
@app.route('/miniproj/')
def minihome():
    ret_str = '<p>Add a number at the end of the url to check that user <\p>'
    ret_str += '<p>There are ' + str(len(Users)) + ' users to pick from <\p>'
    return ret_str
    
@app.route('/user/')
def home():
    return redirect('http://127.0.0.1:5000/miniproj/', code=302)

@app.route('/setup/')
def setup():
    global set_up
    if (not (set_up)): 
        static_test_setup()
        set_up = True
        print(str(len(Users)) + ' users set up. ' + str(len(Sensors)) + ' sensors set up')
    return redirect('http://127.0.0.1:5000/miniproj/', code=302)
    

#http://127.0.0.1:5000/miniproj/
@app.route('/')
def begin():
    #https://stackoverflow.com/questions/14343812/redirecting-to-url-in-flask
    return redirect('http://127.0.0.1:5000/setup/', code=302)

if __name__=='__main__':
    app.run()