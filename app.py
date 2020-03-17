import tweepy
import time
import requests
from bs4 import BeautifulSoup
# import time
from datetime import datetime

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

FILE_NAME = 'last_seen_id.txt'

CountryName = 'Sri Lanka'

def begin_dissection(res):
    global Tot
    global IPM
    Tot = res[12:15]
    # print(Tot)
    IPM = res[-4:-1]
    # print(IPM)

def get_corona():
    print("Fetching Corona Stats...")
    URL = 'https://www.worldometers.info/coronavirus/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    # soup = BeautifulSoup(URL)
    countries = soup.find_all('tr')
    # t = time.localtime()
    # current_time = time.strftime("%H:%M:%S", t)
    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    for country in countries:
        str = country.get_text()
        if CountryName in str:
            res = str
            # print(str)
            # print(len(str))
            begin_dissection(res)
    ReplyString = 'Sri Lanka\nNo. Of Covid-19 Patients: ' + Tot + '\nNo. Of Patients Per Million Of Population: ' + IPM +'\n' + current_time +'\n#LKA #SriLanka\nFrom worldometers.info'
    print(ReplyString)
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
            ReplyString = '@' + mention.user.screen_name + '\nCurrent Temperature: ' + temp + ' Celcius\nCurrent Humidity: ' + humidity + '%\nWind Speed: ' +wind + 'meters per second\nDesc: ' + desc
            print("Issuing Status Update....")
            api.update_status(ReplyString)





# get_temperature()
# reply_to_tweets()
get_corona()



