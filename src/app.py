import os
from dotenv import load_dotenv
from datetime import datetime
import json
import time
from pathlib import Path
import requests
import tweepy
import api

load_dotenv()

def send_tweet(msg):
  # Authenticate to Twitter
  auth = tweepy.OAuthHandler(os.getenv('consume_key'), os.getenv('consume_secret'))
  auth.set_access_token(os.getenv('access_token'), os.getenv('access_key'))

  # Create API object
  twitter = tweepy.API(auth)

  # Create a tweet
  twitter.update_status(msg)

def form_message(status, airline, flight_num, time, from_airport):
  return f"{airline} airlines ({flight_num}) flying from {from_airport} is {status.lower()}!\n\nThe ETA is now {time}"

def check_if_posted(flight_num):
  file = open('./log/tweets.txt', 'r+')
  if flight_num in file.readlines():
    return False
  else:
    file.close()
    file = open('./log/tweets.txt', 'a')
    file.write(flight_num+"\n")
    file.close()
    return True


url = "https://s3-us-west-2.amazonaws.com/files.ocair.com/data/sna_export.js"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

json_response = response.json()

# Get Strapi token
token_payload = api.get_token(os.getenv('strapi_username'), os.getenv('strapi_password'))
token = token_payload['token']
flights = api.get_flights(token)


for flight in json_response['flights']['arrivals']:
  flight_status = flight['status']
  airline = ""
  delayed_time = ""
  from_airport = ""
  if flight_status in 'Delayed':
    airline = json_response['airlines'][flight['codes'][0][:2]]
    actual_time = datetime.strptime(flight['times']['actual'],'%Y-%m-%dT%H:%M:%S')
    from_airport = json_response['airports'][flight['route'][0]]
    flight_num = flight['codes'][0]
    existing = api.check_flights(flight_num, flights)
    if not existing:
      formatted_arrival_time = actual_time.strftime("%I:%M %p")
      api.add_flight_to_db(token, flight_num)
      send_tweet(form_message(flight_status, airline, flight_num, formatted_arrival_time, from_airport))