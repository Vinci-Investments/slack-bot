# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 19:59:35 2017

@author: Maxence
"""

import time
from slackclient import SlackClient
import csv
import requests
from emoji import emojize
from time import gmtime, strftime
from weather import Weather
import schedule

weather = Weather()




lines_bot = [line.rstrip('\n') for line in open('bot.key')]
BOT_NAME = lines_bot[0]
BOT_ID = lines_bot[1]


# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

lines_news = [line.rstrip('\n') for line in open('news.key')]
News_Key = lines_news[0]

lines_slack = [line.rstrip('\n') for line in open('slack.key')]
slack_key = lines_slack[0]
slack_client = SlackClient(slack_key)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

def return_csv(item):
    message = ""
    with requests.Session() as s:
        CSV_URL = 'https://stooq.com/q/d/l/?s='+item[1]+'&i=d'
        download = s.get(CSV_URL)
    
        decoded_content = download.content.decode('utf-8')
    
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        close = my_list[-1][4]
        message="       "+emojize(":small_blue_diamond:", use_aliases=True)+" "+item[0]+" : "+close+"\n"
    return message

def return_csv_crypto(item):
    message = ""
    json_d = requests.request('GET', "https://api.coinmarketcap.com/v1/ticker/?limit=100")
    for data_c in json_d.json():
        if(data_c["id"] == item[1]):
            message="       "+emojize(":small_blue_diamond:", use_aliases=True)+" "+item[0]+" : "+data_c['price_usd']+"\n"
            break
    return message

def job():
    today_date = str(strftime("%A", gmtime()))
    week_end = ["Saturday"]
    if(today_date not in week_end):
        if slack_client.rtm_connect():
            print("StarterBot connected and running!")
            date = str(strftime("%d/%m/%y", gmtime()))
            message = emojize(":wave:", use_aliases=True)+" Bonjour, nous somme le " +date
            time_0 = str(strftime("%H h %M", gmtime()))
            time_1 = str(int(time_0[0:2])+1)
            message+= " et il est " +time_1+time_0[2:]+".\n"
            
            location = weather.lookup_by_location('Paris')
        
            condition = location.condition()
            texte = condition.text()
            if("cloud" in texte.lower()):
                message+= emojize(":cloud:", use_aliases=True)+" "
            if("sun" in texte.lower()):
                message+= emojize(":sunny:", use_aliases=True)+" "
            if("rain" in texte.lower()):
                message+= emojize(":umbrella:", use_aliases=True)+" "
            if("snow" in texte.lower()):
                message+= emojize(":snowflake:", use_aliases=True)+" "
            
            temp = int(round((float(condition.temp()) - 32) * 5.0/9.0,0))
            message += "La température est de "+str(temp)+"°C à La défense."
            message+= "\n\nVoici votre récapitulatif d'aujourd'hui :\n\n"
            message+= emojize(":chart_with_upwards_trend:", use_aliases=True)+" L'état du marché : " +"\n"
            
            list_index = [["S&P500",'^spx'], ["Dow Jones",'^dji'],["CAC40",'^cac'], ["DAX", '^dax'],["FTSE", '^ukx'], ["Nikkei", "^nkx"], ["Topix", "^tpx"]]
            list_bond = [["OAT 10 ans France",'10fry.b'], ["Bund 10 ans Allemagne",'10dey.b'], ["BTP 10 ans Italie",'10ity.b']]
            list_currencies = [["EUR/USD",'eurusd'], ["EUR/GBP",'eurgbp'], ["USD/JPY",'usdjpy']]
            list_commodities = [["Once d'or en dollars",'xauusd'], ["Crude oil Brent",'CB.F']]
            list_crypto = [["Bitcoin/USD",'bitcoin'],["Ethereum/USD",'ethereum'], ["Ripple/USD",'ripple']]
            
            dict_data = {}
            dict_data[0] = ["Indices boursiers", list_index]
            dict_data[1] = ["Obligations", list_bond]
            dict_data[2] = ["Forex", list_currencies]
            dict_data[3] = ["Matières premières", list_commodities]
            dict_data[4] = ["Cryptomonnaies", list_crypto]
            
            for i in range(4):
                message+= "\n"+emojize(":small_orange_diamond:", use_aliases=True)+" "+dict_data[i][0]+" :\n"
                for item in dict_data[i][1]:
                    message+= return_csv(item)
            
            message+= "\n"+emojize(":small_orange_diamond:", use_aliases=True)+" "+dict_data[4][0]+" :\n"
            for item in dict_data[4][1]:
                message+= return_csv_crypto(item)
            
            message += "\n"
            message += emojize(":newspaper:", use_aliases=True)+" Les dernières nouvelles sur Bloomberg : "+"\n"
            request_result = requests.request("GET", "https://newsapi.org/v1/articles?source=bloomberg&sortBy=top&apiKey="+News_Key)
            request_json = request_result.json()
            for i in range(3):
                message += emojize(":small_blue_diamond:", use_aliases=True)+request_json['articles'][i]['title']+". Lien : "+request_json['articles'][i]['url']+"\n"
            slack_client.api_call("chat.postMessage",channel="#test2",text=message)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")

schedule.every().day.at("18:20").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)
