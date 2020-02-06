# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 14:21:53 2019

@author: Felipe Dale Figeman

"""
#example from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

import sqlite3
import json
import os #for supressing https warnings
import random

from flask import Flask, request, redirect, url_for, render_template
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from oauthlib.oauth2 import WebApplicationClient
import requests

from typing import List
from db import init_db_command
from user import User, trip

#https://stackoverflow.com/questions/22947905/flask-example-with-post
app = Flask(__name__)
app.secret_key = 'super-duper-secret'
set_up = False #if server has been initalized

yall : List[User] = []


client_id = ''
client_secret = ''
discovery_url = 'https://accounts.google.com/.well-known/openid-configuration'
def get_google_config():
    #error check the request returns right
    return requests.get(discovery_url).json()

#if you say this isn't secure enough
#it was secure enough for my internship at a cyber security company
def custom_id_getter(withreturn=False):
    id_file = open('whomst.txt', 'r')
    whomst = id_file.read()
    id_file.close()
    global client_id
    client_id = whomst
    if (withreturn):
        return client_id
    else:
        return

def custom_secret_getter(withreturn=False):
    secret_file = open('notouch.txt', 'r')
    secret = secret_file.read()
    secret_file.close()
    global client_secret
    client_secret = secret
    if (withreturn):
        return client_secret
    else:
        return

#################################################


def get_logged_in_user(user_id, index=False):
    global yall
    uid = int(user_id)
    loc = -1
    for i in range(len(yall)):
        if (int(yall[i].user_id) == uid):
            loc = i
            break
    if (loc >= 0):
        usr = yall[loc]
        return loc if (index) else usr
    else:
        print('No user found')
        return False

login_manager = LoginManager()
login_manager.init_app(app)


#Not sure why it's not in its own function
@login_manager.unauthorized_handler
def unauthorized():
    return ('You must be logged in to access this content.', 403)

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth 2 client setup
client = WebApplicationClient(client_id) if (set_up) else WebApplicationClient(custom_id_getter(True))
# Don't want to needlessly open files
############################################


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)




def fix_location(l1): #fixes GPS coordinates as stored on DB
    l1 = l1.replace('D', ', ')
    return l1

def load_trip_print(usr):
    retstr = ''
    tripcount = 1
    for i in usr.my_trips:
        retstr += ('<p>Trip ' + str(tripcount) + ')\n'
                  + 'Driver: ' + i.owner + ' From: ' + fix_location(i.starting_place)
                  + ' To: ' + fix_location(i.destination) + ' Stops: ' + str(i.total_stops)
                  + ' When?: ' + i.date + ' Vehicle: ' + i.vehicle + '\n'
                  + 'Notes: ' + i.comments + '</p>')
        tripcount = tripcount + 1
    return retstr
        

def save_trip_request(trp, usr):
    return 0


@app.route('/cleantech/trip/<trip_id>/requestspot', methods = ['GET', 'POST'])
@login_required
def trip_request(trip_id): #to keep this simple we could make it unclickable if there's no empty seats
    if (current_user.is_authenticated):
        tid = int(trip_id)
        uid = current_user.get_id()
    if (save_trip_request(tid, uid)):
        return('Trip saved')
    else:
        return('Saving failed')



@app.route('/cleantech/user/<usr_id>', methods = ['GET', 'POST', 'DELETE'])
@login_required
def showstuff(usr_id):
    if (request.method == 'GET'):
        if (current_user.is_authenticated):
    #        print('CU:',current_user.get_id(),'done',sep='\n') #debug
            uid = int(usr_id)
            usr = get_logged_in_user(uid) #shouldnt fail
            if (not usr):
                return redirect('http://127.0.0.1:5000/logout', code=302)
            if (not (usr.my_trips)):
                print('No trips found on DB for this user')
                return render_template('no_sensor.html')
            
            trps = load_trip_print(usr)
            return (trps)
    if (request.method == 'POST'):
        text = request.form['text']

        rstr = 'http://127.0.0.1:5000/cleantech/' + usr_id + '/add_trip/' + text + '/'
        return redirect(rstr, code=302)
#
    else:
        return "I have no idea what you're trying to do"

@app.route('/cleantech/user/')
@login_required
def reroutetouser():
    if (current_user.is_authenticated):        
        uid = current_user.get_id()
        whereto = 'http://127.0.0.1:5000/cleantech/user/' + uid
        return redirect(whereto, code=302)

@app.route('/cleantech/')
def home(): #Home page ish kinda thing
    return render_template('homepage.html')


@app.route('/cleantech/add_trip/')
@login_required
def reroutetoaddtrip():
    if (current_user.is_authenticated):        
        uid = current_user.get_id()
        whereto = 'http://127.0.0.1:5000/cleantech/user/' + uid + '/add_trip/nocomment/'
        return redirect(whereto, code=302)



@app.route('/cleantech/user/<usr_id>/add_trip/<comments>/' )
#@login_required rename to make_trip
def add_trip(usr_id, comments):
    uid = int(usr_id)
    usr = get_logged_in_user(uid)
    print(comments)
    
    #magic frontend that gets details from user goes here
    #usr.save_trip(usr.user_id, usr, date, stops, passangers, vehicle, starting_location, ending_location, comments)
    #trp = trip('Never', 'Tesla' '42.348097D-71.105963', '40.748298D-73.984827', 2, comments) #never instantiate a trip in this ever
    #usr.my_trips.append(trp)
    trp = usr.save_trip(usr.user_id, 'Never', 2, 60, 'Tesla', '42.348097D-71.105963', '40.748298D-73.984827', 'No Drugs or alcohol')
    trp.owner = usr_id
    usr.my_trips.append(trp)    
    whereto = 'http://127.0.0.1:5000/cleantech/user/'+str(usr.id)
    return redirect(whereto, code=302)
	
@app.route('/')
@login_required
def rut():
    if (current_user.is_authenticated):
        uid = current_user.get_id()
        whereto = 'http://127.0.0.1:5000/cleantech/user/' + uid
        return redirect(whereto, code=302)
    else: 
        return redirect('http://127.0.0.1:5000/login', code=302)

@app.route("/login")
def login():
    global set_up
    if (not (set_up)):
        custom_id_getter()
        custom_secret_getter()
    if (current_user.is_authenticated):
        uid = current_user.get_id()
        whereto = 'http://127.0.0.1:5000/cleantech/users/' + uid
        return redirect(whereto, code=302)

    google_config = get_google_config()
    authorization_endpoint = google_config["authorization_endpoint"]
    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/success",
        scope=["openid", "email", "profile"],
    )

    print('Redirected after login')
    return redirect(request_uri)



@app.route("/login/success")
def success():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_config = get_google_config()
    token_endpoint = google_config["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(client_id, client_secret)
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_config["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
#        picture = userinfo_response.json()["picture"] # todo: from exaple breaks without.
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
        user_id=unique_id, name=users_name, email=users_email)

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email)

    print(user.user_id)
    user.my_trips = user.load_trips(user.user_id) #load trips from DB so they are there when it is appended to yall
    
    # Begin user session by logging the user in
    login_user(user)
    yall.append(user)
    user.loaded = True
    #print(user)
    # Send user back to homepage
    whereto = 'http://127.0.0.1:5000/cleantech/user/'+str(user.id)
    return redirect(whereto, code=302)

@app.route('/setup/')
def setup():
    global set_up #flag for initialization
    if (not (set_up)):
        custom_id_getter()
        custom_secret_getter()
        set_up = True
    return redirect('http://127.0.0.1:5000/', code=302)


#http://127.0.0.1:5000/
@app.route('/')
def begin():
    global set_up
    if (not set_up):
        return redirect('http://127.0.0.1:5000/setup/', code=302)
        #redirects to setup page
    if (current_user.is_authenticated):
        return redirect('http://127.0.0.1:5000/cleantech/', code=302)
    else:
        return render_template('login.html')
    #redirects to setup page

@app.route("/logout")
@login_required
def logout():
    if (current_user.is_authenticated):
        global yall
        if get_logged_in_user(current_user.get_id(), True) : yall.pop(get_logged_in_user(current_user.get_id(), True)) #This is why OOP is bad
        logout_user()
        print('User logged out')
    return redirect('http://127.0.0.1:5000/', code=302)

@app.route("/weather/", methods=['GET'])
@login_required
def textbox():
    return render_template('search.html')

# to avoid issues iwth insecure transport over http
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#redirects learnt from https://stackoverflow.com/questions/14343812/redirecting-to-url-in-flask


if __name__=='__main__':
    app.run()
