import tweepy
import requests
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
import time
import httplib2


CONSUMER_KEY = ""
CONSUMER_SECRET = ""

ACCESS_KEY = ""
ACCESS_SECRET = ""

# NOTE: flush=True is just for running this script
# with PythonAnywhere's always-on task.
# More info: https://help.pythonanywhere.com/pages/AlwaysOnTasks/
print('this is my twitter bot', flush=True)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
# print(api)

FILE_NAME = 'last_seen_id.txt'

CountryName = 'Sri Lanka'


def get_sitrep():
    sitrep_found = False
    print("Getting Data from Epidemiology Unit Sri Lanka...")
    epid_date1 = time.strftime("%d-%m_10")
    epid_date2 = time.strftime("%d-%m-20%y_10")
    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y")
    http = httplib2.Http()
    pre_req = [epid_date1, "sl", "en"]
    pre_req2 = [epid_date2,"sl","en"]
    status, response = http.request('http://www.epid.gov.lk/web/index.php?option=com_content&view=article&id=225&lang=en')
    for link in BeautifulSoup(response, parse_only=SoupStrainer('a'),features="html.parser"):
        if link.has_attr('href'):
            if all(c in link['href'] for c in pre_req):
                print("Got the SitRep....")
                sitrep_pdf = link['href']
                sitrep_found = True
            elif all(c in link['href'] for c in pre_req2):
                print("Got the SitRep....")
                sitrep_pdf = link['href']
                sitrep_found = True
    if sitrep_found == True:
        sitrep_pdf = "http://www.epid.gov.lk" + sitrep_pdf
        print(sitrep_pdf)
        ReplyString = f"Today is {current_time},\nHere is the Situational Report by the Epidemiology Unit of Sri Lanka\n{sitrep_pdf}\n#LKA #SriLanka #Coronavirus #COVID2019 #COVID19"
        print(ReplyString)
        corona_prompt = input("Is the User pleased with the Reply String?(Y/N): ").lower()
        if corona_prompt == "y":
            print("Posting on @sahasbot...")
            api.update_status(ReplyString)
    else:
        print("Situational Report Not Found, Perhaps it is not uploaded yet...")


def get_corona():
    print("Fetching Corona Stats...")
    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    URL = 'http://hpb.health.gov.lk/api/get-current-statistical'
    page = requests.get(URL)
    json_object = page.json()
    new_cases = json_object["data"]["local_new_cases"]
    Tot = json_object["data"]["local_total_cases"]
    Rec = json_object["data"]["local_recovered"]
    global_new = json_object["data"]["global_new_cases"]
    ReplyString = 'Sri Lanka\nTotal No. Of Covid-19 Patients:' + str(Tot) + '\nNew Cases:' + str(new_cases) + '\nNo. Of Patients Recovered:' + str(Rec) + '\nNew Global Cases:' + str(global_new) +'\n' + current_time + '\n#LKA #SriLanka #Coronavirus #COVID2019 #COVID19\nFrom hpb.health.gov.lk'
    print(ReplyString)
    print(len(ReplyString))
    corona_prompt = input("Is the User pleased with the Reply String?(Y/N): ").lower()
    if corona_prompt == "y":
        print("Posting on @sahasbot...")
        api.update_status(ReplyString)

def get_temperature():
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?id=1248991&appid=c5cdc721216339b2b9da9d05cf535617')
    json_object = r.json()
    global temp_k
    global desc
    global humidity
    global wind
    global temp
    temp_k = float(json_object["main"]["temp"])
    # print(temp_k)
    temp_k = temp_k - 273
    temp = str(temp_k)[0:5]
    desc = str(json_object["weather"][0]["description"])
    # print(desc)
    humidity = str(json_object["main"]["humidity"])
    # print(humidity)
    wind = str(json_object["wind"]["speed"])
    # print(wind)

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if '#plsreply' in mention.full_text.lower():
            print('found #plsreply', flush=True)
            print('responding back...', flush=True)
            api.update_status('@' + mention.user.screen_name +
                    ' You now have my undivided attention child', mention.id)
        if 'weather' in mention.full_text.lower():
            print('Found request for weather..', flush=True)
            print('Calling Weather Function..', flush=True)
            get_temperature()
            ReplyString = f"Current Temperature: {temp} Celcius\nCurrent Humidity: {humidity}%\nWind Speed: {wind} meters per second\nDesc: {desc}\nhttps://twitter.com/{mention.user.screen_name}/status/{mention.id}"
            # ReplyString = '@' + mention.user.screen_name + '\nCurrent Temperature: ' + temp + ' Celcius\nCurrent Humidity: ' + humidity + '%\nWind Speed: ' +wind + 'meters per second\nDesc: ' + desc +"\nhttps://twitter.com/<user_displayname>/status/<tweet_id>"
            print(ReplyString)
            user_prompt = input("Is the User pleased with the Reply String?(Y/N): ").lower()
            if user_prompt == "y":
                print("Posting on @sahasbot...")
                api.update_status(ReplyString)




while True:
    sitrep_found = False
    input_option = input("T: Get Temperature\nR: Reply To Tweets\nC: Get Corono Stats\nS: Get Sitrep\nX: Exit\nWhat Needs to be Done?: ")
    if input_option.lower() == "t":
        reply_to_tweets()
    if input_option.lower() == "r":
        reply_to_tweets()
    if input_option.lower() == "c":
        get_corona()
    if input_option.lower() == "s":
        get_sitrep()
    if input_option.lower() == "x":
        exit()




