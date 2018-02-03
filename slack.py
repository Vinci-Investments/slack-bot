# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 19:59:35 2017

@author: Maxence COUPET
"""

##########################################################################
#                                                                        #
#                            Librairies                                  #
#                                                                        #
##########################################################################

from modules.scrapping import download_last_issue
import time
import re
from slackclient import SlackClient
import csv
import requests
from emoji import emojize
from time import gmtime, strftime
from weather import Weather
from random import randint
import io




##########################################################################
#                                                                        #
#                         Gathering API keys                             #
#                                                                        #
##########################################################################

lines_bot = [line.rstrip('\n') for line in open('bot.key')]
BOT_NAME = lines_bot[0]
BOT_ID = lines_bot[1]

lines_news = [line.rstrip('\n') for line in open('news.key')]
News_Key = lines_news[0]

lines_slack = [line.rstrip('\n') for line in open('slack.key')]
slack_key = lines_slack[0]




##########################################################################
#                                                                        #
#                        Initializing variables                          #
#                                                                        #
##########################################################################
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
weather = Weather()
slack_client = SlackClient(slack_key)
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
SLEEPING_PERIOD = 10
INFOS_CHANNEL = '#news'



##########################################################################
#                                                                        #
#                           Core functions                               #
#                                                                        #
##########################################################################



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
    print("job")
    today_date = str(strftime("%A", gmtime()))
    week_end = ["Sunday"]
    if(today_date not in week_end):
        if slack_client.rtm_connect():
            print("StarterBot connected and running!")
            date = str(strftime("%d/%m/%y", gmtime()))
            message = emojize(":wave:", use_aliases=True)+" Bonjour, nous sommes le " +date
            time_0 = str(strftime("%H h %M", gmtime()))
            time_1 = str(int(time_0[0:2])+1)
            message+= " et il est " +time_1+time_0[2:]+".\n"
            try:
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
                
            except:
                print("Error with weather")
            
            list_index = [["S&P500",'^spx'], ["Dow Jones",'^dji'],["CAC40",'^cac'], ["DAX", '^dax'],["FTSE", '^ukx'], ["Nikkei", "^nkx"], ["Topix", "^tpx"]]
            list_bond = [["OAT 10 ans France",'10fry.b'], ["Bund 10 ans Allemagne",'10dey.b'], ["BTP 10 ans Italie",'10ity.b']]
            list_currencies = [["EUR/USD",'eurusd'], ["EUR/GBP",'eurgbp'], ["USD/JPY",'usdjpy']]
            list_commodities = [["Once d'or en dollars",'xauusd'], ["Crude oil Brent",'CB.F']]
            list_crypto = [["Bitcoin/USD",'bitcoin'],["Ethereum/USD",'ethereum'], ["Litecoin/USD",'litecoin']]
            
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
            slack_client.api_call("chat.postMessage",channel=INFOS_CHANNEL,text=message)
            print("Message sent")
        else:
            print("Connection failed. Invalid Slack token or bot ID?")



def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    
    if command.startswith("gif"):
        key_word = command[4:]
        response = get_gif(key_word)
    
        
        

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

def get_gif(key_word):
    giphy_api_key = "vTNtSl5Tz6gSqa5DtD2Hoo77qWxfsQSr"
    nbr_gif = 10
    json_array = requests.request('GET', "http://api.giphy.com/v1/gifs"+
        "/search?q="+key_word+"&api_key="+giphy_api_key+"&limit="+str(nbr_gif))
    index = randint(0, nbr_gif)
    return json_array.json()["data"][index]['url']

def send_last_bb_businessweek():
    
    file_name = download_last_issue()
    
    if(file_name != 'Error'):
        with open('data/business_week_issues/'+file_name, 'rb') as last_issue:
            slack_client.api_call(
                "files.upload",
                channels=INFOS_CHANNEL,
                filename=file_name,
                title=file_name,
                initial_comment='Dernière édition du Bloomberg Business Week',
                file=io.BytesIO(last_issue.read())
            )
    
        print("Magazine succesfully sent")



if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        
        # Initialze variable for daily message
        bool_uniq = False
        
        while True:
            
            # Checking if new bloomberg businessweek issue
            send_last_bb_businessweek()
            
            # Checking if daily message should be sent 
            trigger_time = "08 h 25"
            message_time = "08 h 30"
            print("Temps actuel : \""+ str(strftime("%H h %M", gmtime()))+"\"")
            print("Trigger : \""+ trigger_time+ "\" ; Message : \""+ message_time+"\"")
            # Initialize each day at 01 h 00
            if(str(strftime("%H h %M", gmtime())) == trigger_time):
                bool_uniq = True
            
            if(str(strftime("%H h %M", gmtime())) == message_time and bool_uniq):
                job()
                bool_uniq = False
            
            # Getting different commands
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            
            # Sleeping process for CPU and Memory 
            time.sleep(SLEEPING_PERIOD)
    else:
        print("Connection failed. Exception traceback printed above.")
"""while 1:
    trigger_time = "08 h 25"
    message_time = "08 h 30"
    print("Temps actuel : \""+ str(strftime("%H h %M", gmtime()))+"\"")
    print("Trigger : \""+ trigger_time+ "\" ; Message : \""+ message_time+"\"")
    # Initialize each day at 01 h 00
    if(str(strftime("%H h %M", gmtime())) == trigger_time):
        bool_uniq = True
    
    if(str(strftime("%H h %M", gmtime())) == message_time and bool_uniq):
        job()
        bool_uniq = False

    time.sleep(10)"""
